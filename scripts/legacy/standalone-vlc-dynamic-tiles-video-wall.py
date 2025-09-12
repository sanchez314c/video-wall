#!/usr/bin/env python3

####################################################################################
#                                                                                  #
#  ██████╗ ██╗   ██╗███╗   ██╗ █████╗ ███╗   ███╗██╗ ██████╗                      #
#  ██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗████╗ ████║██║██╔════╝                      #
#  ██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██╔████╔██║██║██║                           #
#  ██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║╚██╔╝██║██║██║                           #
#  ██████╔╝   ██║   ██║ ╚████║██║  ██║██║ ╚═╝ ██║██║╚██████╗                      #
#  ╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝ ╚═════╝                      #
#                                                                                  #
#  ████████╗██╗██╗     ███████╗███████╗                                           #
#  ╚══██╔══╝██║██║     ██╔════╝██╔════╝                                           #
#     ██║   ██║██║     █████╗  ███████╗                                           #
#     ██║   ██║██║     ██╔══╝  ╚════██║                                           #
#     ██║   ██║███████╗███████╗███████║                                           #
#     ╚═╝   ╚═╝╚══════╝╚══════╝╚══════╝                                           #
#                                                                                  #
####################################################################################
#
# Script Name: video-wall-dynamic.py
#
# Author: Jason Paul Michaels <jason@example.com>
#
# Date Created: 2024-01-30
#
# Last Modified: 2025-05-24
#
# Version: 2.1.0
#
# Description: Advanced VLC-based video wall with dynamic tile management,
#              hardware acceleration, and intelligent grid layouts.
#
# Usage: python video-wall-dynamic.py
#
# Dependencies: Python 3.6+, PyQt5, python-vlc, VLC Media Player
#
# GitHub: https://github.com/jasonpaulmichaels/videowall
#
# Features:
#    - Dynamic grid tile management
#    - Hardware-accelerated video decoding
#    - Animated tile transitions
#    - Cross-platform VLC integration
#    - Performance optimization
#    - Real-time tile flipping and effects
#
# Controls:
#    - Space: Toggle pause/play
#    - Left/Right arrows: Change videos
#    - Escape: Exit application
#
####################################################################################

"""
Video Wall Display System - Dynamic Tiles Edition
=================================================

An advanced VLC-powered video wall system featuring dynamic tile management,
hardware acceleration, and sophisticated layout algorithms. Designed for
high-performance video playback with intelligent resource management.

This dynamic edition specializes in animated tile arrangements and
optimized video processing for professional installations.
"""
import os
import random
import sys
import time
import vlc
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy, QFileDialog, QGridLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve

# Import shared utilities
try:
    from video_utils import setup_logging, get_video_files, select_video_directory, validate_video_count, set_process_priority
    from vlc_utils import get_vlc_args, setup_vlc_player_window, configure_vlc_player
except ImportError:
    def setup_logging(name, level=logging.INFO):
        logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(name)
    def set_process_priority():
        if sys.platform == 'darwin': os.nice(10)

# Configure logging
logger = setup_logging("video-wall-dynamic")

class VLCVideoTile(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: black;")
        
        # Get platform-specific VLC arguments
        try:
            vlc_args = get_vlc_args()
        except NameError:
            # Fallback if utils not available with hardware acceleration
            vlc_args = ['--quiet', '--no-audio', '--no-osd', '--vout=gpu', '--avcodec-hw=any', '--avcodec-threads=0', '--file-caching=1000']
        
        self.instance = vlc.Instance(' '.join(vlc_args))
        self.player = self.instance.media_player_new()
        self.is_playing = False
        self.current_file = None
        
        # Set up platform-specific window embedding
        try:
            setup_vlc_player_window(self.player, self)
        except NameError:
            # Fallback if utils not available
            if sys.platform == "darwin":
                self.player.set_nsobject(int(self.winId()))
            elif sys.platform == "linux":
                self.player.set_xwindow(self.winId())
            elif sys.platform == "win32":
                self.player.set_hwnd(self.winId())
        
        # Configure player settings
        try:
            configure_vlc_player(self.player)
        except NameError:
            # Fallback configuration
            self.player.video_set_scale(0)
            self.player.video_set_aspect_ratio("16:9")
        
    def play(self, filepath):
        try:
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return False
            
            # Stop any existing playback
            self.stop()
            
            media = self.instance.media_new(filepath)
            media.add_option(':input-repeat=999999')  # Loop video
            media.add_option(':hardware-decoding=1')  # Force hardware decoding
            media.add_option(':avcodec-hw=any')  # Allow any hardware decoder
            
            self.player.set_media(media)
            self.player.audio_set_volume(0)
            
            # Start playback and verify
            success = self.player.play()
            time.sleep(0.1)  # Give it a moment to start
            
            # Verify playback started
            retry_count = 0
            while not self.player.is_playing() and retry_count < 3:
                time.sleep(0.5)
                retry_count += 1
            
            self.is_playing = self.player.is_playing()
            if self.is_playing:
                self.current_file = filepath
                logger.info(f"Successfully started playback of {filepath}")
            else:
                logger.error(f"Failed to start playback of {filepath}")
            
            return self.is_playing
            
        except Exception as e:
            logger.error(f"Error playing {filepath}: {e}")
            return False

    def stop(self):
        try:
            if self.is_playing:
                self.player.stop()
                self.is_playing = False
                self.current_file = None
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")

    def set_playback_rate(self, rate):
        try:
            self.player.set_rate(rate)
        except Exception as e:
            logger.error(f"Error setting playback rate: {e}")

    def flip_horizontal(self):
        self.setStyleSheet("background-color: black;")
        self.setLayoutDirection(Qt.RightToLeft)

    def unflip_horizontal(self):
        self.setStyleSheet("background-color: black;")
        self.setLayoutDirection(Qt.LeftToRight)

    def __del__(self):
        self.stop()
        self.player.release()
        self.instance.release()

class VideoWall(QMainWindow):
    def __init__(self, videos, screen, screen_index, fullscreen=True):
        super().__init__()
        self.setWindowTitle(f"Video Wall {screen_index}")
        self.setGeometry(screen.geometry())
        self.move(screen.geometry().x(), screen.geometry().y())

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
        self.layout.setSpacing(0)

        self.all_videos = videos
        self.num_tiles = random.randint(4, 6)  # Reduced for better performance
        self.tiles = []
        self.active_tiles = []

        # Initialize tiles with verification
        for _ in range(self.num_tiles):
            tile = VLCVideoTile(self)
            if self.verify_tile(tile):
                self.tiles.append(tile)
                self.active_tiles.append(True)

        self.create_grid_layout()
        # Increased delay for proper initialization
        QTimer.singleShot(1000, self.set_random_videos)
        QTimer.singleShot(2000, self.start_tile_flipping)

    def verify_tile(self, tile):
        try:
            return tile.player is not None and tile.instance is not None
        except:
            logger.error("Failed to verify tile initialization")
            return False

    def create_grid_layout(self):
        positions = [(0, 0), (0, 1), (0, 2),
                    (1, 0), (1, 1), (1, 2),
                    (2, 0), (2, 1), (2, 2)]
        random.shuffle(positions)
        
        for i, tile in enumerate(self.tiles):
            if i < len(positions):
                pos = positions[i]
                rowspan = random.randint(1, 2)
                colspan = random.randint(1, 2)
                self.layout.addWidget(tile, pos[0], pos[1], rowspan, colspan)

    def set_random_videos(self):
        try:
            logger.info(f"Setting videos for wall {self.windowTitle()}")
            available_videos = [v for v in self.all_videos if os.path.exists(v)]
            if not available_videos:
                logger.error("No valid videos available")
                return

            for i, tile in enumerate(self.tiles):
                if self.active_tiles[i]:
                    video = random.choice(available_videos)
                    retry_count = 0
                    while not tile.play(video) and retry_count < 3:
                        video = random.choice(available_videos)
                        retry_count += 1
                        time.sleep(0.5)
                    
                    if retry_count >= 3:
                        logger.error(f"Failed to load video for tile {i}")
                        self.active_tiles[i] = False
                    else:
                        logger.info(f"Successfully playing: {video}")

        except Exception as e:
            logger.error(f"Error setting videos: {e}")

    def start_tile_flipping(self):
        for i, tile in enumerate(self.tiles):
            if self.active_tiles[i]:
                self.flip_tile(tile)
        QTimer.singleShot(random.randint(5000, 10000), self.start_tile_flipping)

    def flip_tile(self, tile):
        self.randomize_tile(tile)
        self.randomize_video(tile)

    def randomize_tile(self, tile):
        try:
            grid_row, grid_col = self.layout.getItemPosition(self.layout.indexOf(tile))[:2]
            rowspan = random.randint(1, 2)
            colspan = random.randint(1, 2)

            self.layout.removeWidget(tile)
            self.layout.addWidget(tile, grid_row, grid_col, rowspan, colspan)

            target_geometry = tile.geometry()
            animation = QPropertyAnimation(tile, b"geometry")
            animation.setDuration(1000)
            animation.setStartValue(tile.geometry())
            animation.setEndValue(target_geometry)
            animation.setEasingCurve(QEasingCurve.InOutQuad)
            animation.start(QPropertyAnimation.DeleteWhenStopped)
        except Exception as e:
            logger.error(f"Error randomizing tile: {e}")

    def randomize_video(self, tile):
        try:
            playback_rate = random.choice([0.9, 1.0, 1.1])
            tile.set_playback_rate(playback_rate)
            if random.choice([True, False]):
                tile.flip_horizontal()
            else:
                tile.unflip_horizontal()
        except Exception as e:
            logger.error(f"Error randomizing video: {e}")

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Space:
                for i, tile in enumerate(self.tiles):
                    if self.active_tiles[i]:
                        if tile.is_playing:
                            tile.player.pause()
                        else:
                            tile.player.play()
            elif event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
                self.set_random_videos()
            elif event.key() == Qt.Key_Escape:
                self.close()
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
        super().keyPressEvent(event)

    def closeEvent(self, event):
        try:
            for tile in self.tiles:
                tile.stop()
        except:
            pass
        super().closeEvent(event)

def select_directory():
    app = QApplication.instance() or QApplication(sys.argv)
    folder_selected = QFileDialog.getExistingDirectory(None, "Select Folder")
    if folder_selected:
        logger.info(f"Selected directory: {folder_selected}")
        return folder_selected
    return None

def get_all_videos(directory):
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv')
    videos = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(video_extensions):
                videos.append(os.path.join(root, file))
    logger.info(f"Found {len(videos)} video files")
    return videos

def main():
    try:
        if sys.platform == 'darwin':
            os.nice(10)
        
        video_dir = select_directory()
        if not video_dir:
            logger.error("No directory selected, exiting.")
            return

        videos = get_all_videos(video_dir)
        if len(videos) < 5:
            logger.error(f"Not enough videos found. Need at least 5.")
            return

        app = QApplication.instance() or QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        # Enable Qt hardware acceleration
        app.setAttribute(Qt.AA_UseOpenGLES, True)
        app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
        app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
        
        screens = app.screens()
        if not screens:
            logger.error("No displays detected.")
            return

        logger.info(f"Number of screens detected: {len(screens)}")
        video_walls = []
        for i, screen in enumerate(screens):
            logger.info(f"Screen {i}: {screen.name()}")
            video_wall = VideoWall(videos, screen, i, fullscreen=True)
            video_wall.show()
            video_walls.append(video_wall)

        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
