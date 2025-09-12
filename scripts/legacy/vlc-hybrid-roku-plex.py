#!/usr/bin/env python3

####################################################################################
#                                                                                  #
#  ██████╗  ██████╗ ██╗  ██╗██╗   ██╗    ██╗███╗   ██╗████████╗███████╗ ██████╗   #
#  ██╔══██╗██╔═══██╗██║ ██╔╝██║   ██║    ██║████╗  ██║╚══██╔══╝██╔════╝██╔════╝   #
#  ██████╔╝██║   ██║█████╔╝ ██║   ██║    ██║██╔██╗ ██║   ██║   █████╗  ██║  ███╗  #
#  ██╔══██╗██║   ██║██╔═██╗ ██║   ██║    ██║██║╚██╗██║   ██║   ██╔══╝  ██║   ██║  #
#  ██║  ██║╚██████╔╝██║  ██╗╚██████╔╝    ██║██║ ╚████║   ██║   ███████╗╚██████╔╝  #
#  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝     ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝ ╚═════╝   #
#                                                                                  #
#  ██╗    ██╗ █████╗ ██╗     ██╗                                                  #
#  ██║    ██║██╔══██╗██║     ██║                                                  #
#  ██║ █╗ ██║███████║██║     ██║                                                  #
#  ██║███╗██║██╔══██║██║     ██║                                                  #
#  ╚███╔███╔╝██║  ██║███████╗███████╗                                             #
#   ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝                                             #
#                                                                                  #
####################################################################################
#
# Script Name: video-wall-roku.py
#
# Author: Jason Paul Michaels <jason@example.com>
#
# Date Created: 2023-11-23
#
# Last Modified: 2025-05-24
#
# Version: 1.1.0
#
# Description: Integrated video wall combining local files with Roku/Plex streaming.
#              Features automated device control, content management, and hybrid
#              source coordination for smart home entertainment systems.
#
# Usage: python video-wall-roku.py
#
# Dependencies: Python 3.6+, PyQt5, python-vlc, requests, Roku devices, Plex server
#
# GitHub: https://github.com/jasonpaulmichaels/videowall
#
# Features:
#    - Hybrid local + streaming content
#    - Roku device automation
#    - Plex server integration
#    - Smart home coordination
#    - Multi-device synchronization
#    - Content library management
#    - Automated playlist navigation
#
# Controls:
#    - Space: Toggle pause/play
#    - Left/Right arrows: Change content
#    - Escape: Exit application
#
####################################################################################

"""
Video Wall Display System - Smart Integration Edition
====================================================

A comprehensive smart home video wall system that seamlessly integrates local
video files with Roku streaming devices and Plex media servers. Features
intelligent content coordination and automated device management.

This integration edition specializes in smart home entertainment systems
with multi-source content delivery and synchronized playback control.
"""
import os
import requests
from xml.etree import ElementTree
import random
import sys
import time
import vlc
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QSizePolicy, QFileDialog, QFrame
from PyQt5.QtCore import Qt, QTimer

class VLCVideoWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize VLC instance with hardware acceleration
        vlc_args = '--no-xlib --quiet --vout=gpu --avcodec-hw=any --avcodec-threads=0 --file-caching=1000'
        self.instance = vlc.Instance(vlc_args)
        self.player = self.instance.media_player_new()
        
        # Set the window ID
        if sys.platform == "darwin":  # macOS
            self.player.set_nsobject(int(self.winId()))
        elif sys.platform == "linux":  # linux
            self.player.set_xwindow(self.winId())
        elif sys.platform == "win32":  # windows
            self.player.set_hwnd(self.winId())

    def play(self, filepath):
        try:
            media = self.instance.media_new(filepath)
            self.player.set_media(media)
            self.player.audio_set_volume(0)  # Mute
            self.player.play()
        except Exception as e:
            print(f"Error playing {filepath}: {e}")

    def stop(self):
        try:
            self.player.stop()
        except Exception as e:
            print(f"Error stopping playback: {e}")

    def __del__(self):
        try:
            self.player.stop()
            self.player.release()
            self.instance.release()
        except:
            pass

def get_plex_playlist_videos(plex_server_ip, plex_public_ip, plex_token, playlist_id):
    headers = {
        "X-Plex-Token": plex_token
    }
    url = f"http://{plex_server_ip}:32400/playlists/{playlist_id}/items"
    try:
        response = requests.get(url, headers=headers)
        tree = ElementTree.fromstring(response.content)
        
        video_urls = []
        for item in tree.findall(".//Video"):
            media = item.find("Media")
            if media is not None:
                part = media.find("Part")
                if part is not None:
                    media_key = part.get("key")
                    video_url = f"http://{plex_public_ip}:12096{media_key}?X-Plex-Token={plex_token}"
                    video_urls.append(video_url)
                    print(f"Found video URL: {video_url}")
        
        return video_urls
    except Exception as e:
        print(f"Error fetching Plex playlist: {e}")
        return []

class VideoWall(QMainWindow):
    def __init__(self, videos, screen, fullscreen=True):
        super().__init__()
        self.setWindowTitle("Video Wall")
        self.setGeometry(screen.geometry())

        if fullscreen:
            self.showFullScreen()
        else:
            self.show()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)

        self.all_videos = videos
        self.num_videos = 6
        self.video_widgets = []

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)

        upper_splitter = QSplitter(Qt.Horizontal)
        upper_splitter.setHandleWidth(1)
        lower_splitter = QSplitter(Qt.Horizontal)
        lower_splitter.setHandleWidth(1)
        splitter.addWidget(upper_splitter)
        splitter.addWidget(lower_splitter)

        layout.addWidget(splitter)

        for i in range(self.num_videos):
            video_widget = VLCVideoWidget(self)
            self.video_widgets.append(video_widget)

            if i < 3:
                upper_splitter.addWidget(video_widget)
            else:
                lower_splitter.addWidget(video_widget)

        QTimer.singleShot(500, self.set_random_videos)

    def set_random_videos(self):
        try:
            self.current_videos = random.sample(self.all_videos, self.num_videos)
            for widget, video in zip(self.video_widgets, self.current_videos):
                print(f"Playing: {video}")
                widget.play(video)
        except Exception as e:
            print(f"Error setting videos: {e}")

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Space:
                for widget in self.video_widgets:
                    if widget.player.is_playing():
                        widget.player.pause()
                    else:
                        widget.player.play()
            elif event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
                self.set_random_videos()
            elif event.key() == Qt.Key_Escape:
                self.close()
        except Exception as e:
            print(f"Error handling key press: {e}")
        super().keyPressEvent(event)

    def closeEvent(self, event):
        try:
            for widget in self.video_widgets:
                widget.stop()
        except:
            pass
        super().closeEvent(event)

def select_directory():
    app = QApplication.instance() or QApplication(sys.argv)
    folder_selected = QFileDialog.getExistingDirectory(None, "Select Folder")
    if folder_selected:
        print(f"Selected directory: {folder_selected}")
        return folder_selected
    return None

def get_all_videos(directory):
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv')
    videos = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(video_extensions):
                videos.append(os.path.join(root, file))
    return videos

def send_command_to_roku(roku_ip, command, params=None):
    try:
        url = f"http://{roku_ip}:8060/{command}"
        response = requests.post(url, data=params)
        print(f"Response from {roku_ip}: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Roku command error: {e}")
        return False

def launch_plex_on_roku(roku_ip, plex_app_id="13535"):
    print(f"Launching Plex app on Roku at IP: {roku_ip}")
    return send_command_to_roku(roku_ip, f"launch/{plex_app_id}")

def navigate_and_play_playlist(roku_ip):
    print(f"Navigating playlist on Roku at IP: {roku_ip}")
    commands = ["keypress/Down", "keypress/Select", "keypress/Right", "keypress/Select"]
    for command in commands:
        send_command_to_roku(roku_ip, command)
        time.sleep(1)

def main():
    try:
        # Lower process priority on macOS
        if sys.platform == 'darwin':
            os.nice(10)
        
        video_dir = select_directory()
        if not video_dir:
            print("No directory selected, exiting.")
            return

        videos = get_all_videos(video_dir)
        if len(videos) < 6:
            print(f"Not enough videos found. Need at least 6.")
            return

        # Plex configuration
        plex_config = {
            'server_ip': "127.0.0.1",
            'public_ip': "97.129.125.55",
            'token': "vjA_ycJ9wBwUUqABzaSK",
            'playlist_id': "2451"
        }

        # Get Plex videos if configured
        plex_videos = get_plex_playlist_videos(
            plex_config['server_ip'],
            plex_config['public_ip'],
            plex_config['token'],
            plex_config['playlist_id']
        )
        
        if plex_videos:
            videos.extend(plex_videos)

        app = QApplication.instance() or QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        
        # Enable Qt hardware acceleration
        app.setAttribute(Qt.AA_UseOpenGLES, True)
        app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
        app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
        
        screens = app.screens()
        if not screens:
            print("No displays detected.")
            return

        print(f"Number of screens detected: {len(screens)}")
        video_walls = []
        
        for i, screen in enumerate(screens):
            print(f"Screen {i}: {screen.name()}")
            fullscreen = i != 0
            video_wall = VideoWall(videos, screen, fullscreen)
            if not fullscreen:
                video_wall.resize(800, 600)
                video_wall.move(100, 100)
            video_wall.show()
            video_walls.append(video_wall)

        # Roku control
        roku_ips = [
            "10.0.0.207",
            "10.0.0.235",
            "10.0.0.242",
            "10.0.0.248"
        ]

        for i, roku_ip in enumerate(roku_ips):
            if launch_plex_on_roku(roku_ip):
                print(f"Roku {i+1} launched Plex at {roku_ip}")
                QTimer.singleShot(60000, lambda ip=roku_ip: navigate_and_play_playlist(ip))

        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()