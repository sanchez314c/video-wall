#!/usr/bin/env python3
"""
FFplay Local Video Wall - Floating Tiles
--------------------------------------
Author: Jason Paul Michaels
Date: November 23, 2023
Version: 1.0.0

Description:
    Creates a video wall with floating dynamic tiles for local video files.
    Supports automated movement and arrangement of video tiles.

Features:
    - Floating tile animation
    - Dynamic positioning
    - Automated movement patterns
    - Local video support

Requirements:
    - Python 3.6+
    - ffmpeg/ffplay
    - Local video files

Usage:
    python ffplay-local-videowall-floating.py
"""
import os
import random
import sys
import vlc
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSizePolicy, QFileDialog, QFrame
from PyQt5.QtCore import Qt, QTimer, QRect

class VLCPlayer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize VLC instance with hardware acceleration
        vlc_args = [
            '--no-xlib',
            '--quiet',
            '--vout=gpu',
            '--avcodec-hw=any',
            '--avcodec-threads=0',
            '--file-caching=1000',
            '--no-audio',
            '--no-osd'
        ]
        self.instance = vlc.Instance(' '.join(vlc_args))
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
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.all_videos = videos
        self.num_videos = min(6, len(videos))
        self.video_widgets = []

        for _ in range(self.num_videos):
            player = VLCPlayer(self)
            self.video_widgets.append(player)
            layout.addWidget(player)

        QTimer.singleShot(500, self.set_random_videos)
        QTimer.singleShot(1000, self.start_random_resize)

    def set_random_videos(self):
        try:
            self.current_videos = random.sample(self.all_videos, self.num_videos)
            for widget, video in zip(self.video_widgets, self.current_videos):
                print(f"Playing: {video}")
                widget.play(video)
        except Exception as e:
            print(f"Error setting videos: {e}")

    def start_random_resize(self):
        try:
            for video_widget in self.video_widgets:
                self.resize_video_widget(video_widget)
            QTimer.singleShot(random.randint(15000, 30000), self.start_random_resize)
        except Exception as e:
            print(f"Error in random resize: {e}")

    def resize_video_widget(self, video_widget):
        try:
            screen_geometry = self.screen().geometry()
            min_width = max(int(screen_geometry.width() // 3), 100)
            max_width = min(int(screen_geometry.width() // 1.5), screen_geometry.width())
            min_height = max(int(screen_geometry.height() // 3), 100)
            max_height = min(int(screen_geometry.height() // 1.5), screen_geometry.height())
            
            random_width = random.randint(min_width, max_width)
            random_height = random.randint(min_height, max_height)
            random_x = random.randint(0, max(0, screen_geometry.width() - random_width))
            random_y = random.randint(0, max(0, screen_geometry.height() - random_height))
            
            video_widget.setGeometry(QRect(random_x, random_y, random_width, random_height))
        except Exception as e:
            print(f"Error resizing widget: {e}")

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
        if len(videos) < 1:
            print(f"No videos found in the selected directory.")
            return

        app = QApplication.instance() or QApplication(sys.argv)
        
        # Enable high DPI scaling and hardware acceleration
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        app.setAttribute(Qt.AA_UseOpenGLES, True)
        app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
        app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
        
        screens = app.screens()
        if not screens:
            print("No displays detected.")
            return

        print(f"Number of screens detected: {len(screens)}")
        for i, screen in enumerate(screens):
            print(f"Screen {i}: {screen.name()}")
            video_wall = VideoWall(videos, screen, fullscreen=True)
            video_wall.show()

        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
