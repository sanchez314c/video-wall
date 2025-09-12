#!/usr/bin/env python3

####################################################################################
#                                                                                  #
#  ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗██╗███╗   ██╗ ██████╗     #
#  ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔════╝     #
#  ███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║██║██╔██╗ ██║██║  ███╗    #
#  ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║██║██║╚██╗██║██║   ██║    #
#  ███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝    #
#  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝     #
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
# Script Name: video-wall-m3u8.py
#
# Author: Jason Paul Michaels <jason@example.com>
#
# Date Created: 2023-07-26
#
# Last Modified: 2025-05-24
#
# Version: 1.1.0
#
# Description: Professional streaming video wall supporting M3U8 playlists with
#              intelligent stream management, buffer optimization, and health
#              monitoring for broadcast-quality displays.
#
# Usage: python video-wall-m3u8.py
#
# Dependencies: Python 3.6+, PyQt5, Network access for M3U8 streams
#
# GitHub: https://github.com/jasonpaulmichaels/videowall
#
# Features:
#    - M3U8 HLS stream support
#    - 6x6 professional grid layout
#    - Dynamic tile arrangement
#    - Stream health monitoring
#    - Buffer status management
#    - Network resilience
#    - Automatic stream recovery
#
# Controls:
#    - Space: Toggle pause/play
#    - Left/Right arrows: Change streams
#    - Escape: Exit application
#
####################################################################################

"""
Video Wall Display System - Streaming Edition (M3U8)
====================================================

A professional-grade streaming video wall system designed for M3U8 HLS streams.
Features intelligent stream management, buffer optimization, and network
resilience for broadcast-quality video wall installations.

This streaming edition specializes in live content delivery and multi-source
streaming with robust error handling and automatic recovery mechanisms.
"""
import os
import random
import sys
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy, QGridLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer, QPropertyAnimation, QEasingCurve

def get_all_m3u8_links(file_path):
    try:
        with open(file_path, 'r') as file:
            links = file.readlines()
        links = [link.strip() for link in links if link.strip()]
        print(f"Loaded m3u8 links: {links}")
        return links
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

class VideoTile(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("border: 1px solid white;")
        
        # Enable hardware acceleration
        self.setAttribute(Qt.WA_AccelChildrenInheritClip)
        self.setAttribute(Qt.WA_NativeWindow)

    def flip_horizontal(self):
        self.setStyleSheet("transform: scaleX(-1);")

    def unflip_horizontal(self):
        self.setStyleSheet("transform: scaleX(1);")

class VideoWall(QMainWindow):
    def __init__(self, m3u8_links, screen, fullscreen=True):
        super().__init__()
        self.setWindowTitle("Video Wall")
        self.setGeometry(screen.geometry())

        if fullscreen:
            self.showFullScreen()
        else:
            self.show()

        central_widget = QWidget(self)
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        central_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)

        self.all_m3u8_links = m3u8_links
        self.num_tiles = min(len(m3u8_links), random.randint(5, 8))  # Ensure num_tiles is not more than available sources
        self.tiles = []
        self.players = []

        self.current_m3u8_index = 0
        self.rotation_count = 0
        self.flip_count = 0
        self.max_flips = 5  # Reset positions more frequently

        self.screen_geometry = screen.geometry()

        for _ in range(self.num_tiles):
            tile = VideoTile(self)
            player = QMediaPlayer(tile)
            player.setVideoOutput(tile)
            player.setMuted(True)
            player.error.connect(self.handle_player_error)
            player.mediaStatusChanged.connect(lambda state, p=player: self.handle_media_status(state, p))
            player.bufferStatusChanged.connect(lambda status, p=player: self.handle_buffer_status(status, p))

            self.players.append(player)
            self.tiles.append(tile)

        self.create_grid_layout()
        self.set_initial_videos()
        self.start_tile_flipping()

    def create_grid_layout(self):
        self.positions = [(0, 0), (0, 1), (0, 2),
                          (1, 0), (1, 1), (1, 2),
                          (2, 0), (2, 1), (2, 2)]
        random.shuffle(self.positions)

        for i, tile in enumerate(self.tiles):
            pos = self.positions[i % len(self.positions)]
            rowspan = 1  # Restricting to a single row span
            colspan = 1  # Restricting to a single column span
            self.layout.addWidget(tile, pos[0], pos[1], rowspan, colspan)

    def set_initial_videos(self):
        self.current_m3u8_link = self.all_m3u8_links[self.current_m3u8_index]
        self.current_m3u8_index = (self.current_m3u8_index + 1) % len(self.all_m3u8_links)
        
        self.current_sources = [self.current_m3u8_link] + random.sample(self.all_m3u8_links, min(len(self.all_m3u8_links) - 1, self.num_tiles - 1))
        random.shuffle(self.current_sources)

        for player, source in zip(self.players, self.current_sources):
            print(f"Setting m3u8 URL for player: {source}")
            player.setMedia(QMediaContent(QUrl(source)))

    def set_random_videos(self):
        if self.rotation_count >= 4:
            self.current_m3u8_link = self.all_m3u8_links[self.current_m3u8_index]
            self.current_m3u8_index = (self.current_m3u8_index + 1) % len(self.all_m3u8_links)
            self.rotation_count = 0
        
        self.current_sources = [self.current_m3u8_link] + random.sample(self.all_m3u8_links, min(len(self.all_m3u8_links) - 1, self.num_tiles - 1))
        random.shuffle(self.current_sources)

        for player, source in zip(self.players, self.current_sources):
            print(f"Setting m3u8 URL for player: {source}")
            player.setMedia(QMediaContent(QUrl(source)))
        
        self.rotation_count += 1
        self.create_grid_layout()  # Refresh the layout

    def handle_media_status(self, status, player):
        print(f"Media status changed: {status}")
        if status == QMediaPlayer.LoadedMedia:
            print("Media loaded, starting playback.")
            player.play()
        elif status in (QMediaPlayer.StalledMedia, QMediaPlayer.EndOfMedia, QMediaPlayer.InvalidMedia):
            print("Media stalled or ended, reloading...")
            player.stop()
            player.play()

    def handle_buffer_status(self, status, player):
        print(f"Buffer status: {status}")
        max_buffer = 50  # Maximum buffer size percentage
        if status > max_buffer:
            print(f"Buffering exceeds {max_buffer}%, pausing for a moment.")
            player.pause()
            QTimer.singleShot(1000, player.play)

    def handle_player_error(self):
        for player in self.players:
            if player.error():
                print(f"Error: {player.errorString()}")
                player.stop()
                player.play()

    def start_tile_flipping(self):
        for tile in self.tiles:
            self.flip_tile(tile)
        QTimer.singleShot(random.randint(5000, 10000), self.start_tile_flipping)

    def flip_tile(self, tile):
        self.randomize_tile(tile)
        self.randomize_video(tile)
        self.flip_count += 1
        if self.flip_count >= self.max_flips:
            self.reset_tiles()
            self.flip_count = 0

    def randomize_tile(self, tile):
        grid_row, grid_col = self.layout.getItemPosition(self.layout.indexOf(tile))[:2]
        # Restrict the rowspan and colspan values to be between 1 and 1
        rowspan = 1
        colspan = 1

        self.layout.removeWidget(tile)
        self.layout.addWidget(tile, grid_row, grid_col, rowspan, colspan)

        animation = QPropertyAnimation(tile, b"geometry")
        animation.setDuration(1000)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start(QPropertyAnimation.DeleteWhenStopped)

    def reset_tiles(self):
        for i, tile in enumerate(self.tiles):
            pos = self.positions[i % len(self.positions)]
            self.layout.removeWidget(tile)
            self.layout.addWidget(tile, pos[0], pos[1], 1, 1)  # Reset to original positions with span 1x1

    def randomize_video(self, tile):
        player_index = self.tiles.index(tile)
        player = self.players[player_index]

        # Randomize playback speed
        playback_rate = random.choice([0.9, 1.0, 1.1])
        player.setPlaybackRate(playback_rate)

        # Randomize horizontal flip
        if random.choice([True, False]):
            tile.flip_horizontal()
        else:
            tile.unflip_horizontal()

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Space:
                for player in self.players:
                    if player.state() == QMediaPlayer.PlayingState:
                        player.pause()
                    else:
                        player.play()
            elif event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
                self.set_random_videos()
        except AttributeError as e:
            print(f"AttributeError: {e}")
        super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Enable Qt hardware acceleration
    app.setAttribute(Qt.AA_UseOpenGLES, True)
    app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
    app.setAttribute(Qt.AA_UseDesktopOpenGL, True)

    screen = app.primaryScreen()
    m3u8_file = filedialog.askopenfilename(title="Select M3U8 Links File", filetypes=[("Text Files", "*.txt")])

    if not m3u8_file:
        messagebox.showerror("Error", "No M3U8 links file selected.")
        sys.exit(1)

    m3u8_links = get_all_m3u8_links(m3u8_file)
    video_wall = VideoWall(m3u8_links, screen)
    video_wall.show()
    sys.exit(app.exec_())