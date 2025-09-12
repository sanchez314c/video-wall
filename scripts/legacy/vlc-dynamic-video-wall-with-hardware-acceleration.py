#!/usr/bin/env python3
"""
FFplay Local Video Wall - Dynamic Tiles
-------------------------------------
Author: Jason Paul Michaels
Date: January 30, 2024
Version: 2.0.0

Description:
    Creates a video wall display system for local video files with dynamic tile management.
    Supports automatic layout adjustment and display clustering with hardware acceleration.
"""
import os
import random
import sys
import time
import vlc
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy, QFileDialog, QGridLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('video_wall.log')
    ]
)
logger = logging.getLogger(__name__)

class VLCVideoTile(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: black;")
        
        # Enhanced VLC arguments for hardware acceleration
        vlc_args = [
            '--no-xlib',
            '--quiet',
            '--no-video-title-show',
            '--no-snapshot-preview',
            '--aspect-ratio=fill',
            '--zoom=1',
            '--aout=none',  # Disable audio output
            '--vout=gpu',  # Use GPU video output for better performance
            '--avcodec-hw=any',  # Allow any hardware decoder
            '--avcodec-skiploopfilter=4',  # Skip loop filter for performance
            '--avcodec-skip-frame=0',  # Don't skip frames
            '--avcodec-skip-idct=0',  # Don't skip IDCT
            '--video-filter=deinterlace',  # Add deinterlacing
            '--deinterlace-mode=blend',
            '--no-audio',  # Completely disable audio
            '--no-osd',  # No on-screen display
            '--no-spu',  # No subtitles
            '--no-stats',  # No statistics
            '--no-sub-autodetect-file',  # Don't auto-load subtitles
            '--avcodec-threads=0',  # Auto-detect CPU threads
            '--file-caching=1000',  # Reduce file caching for better performance
            '--network-caching=1000'  # Reduce network caching
        ]
        
        self.instance = vlc.Instance(' '.join(vlc_args))
        self.player = self.instance.media_player_new()
        self.is_playing = False
        self.current_file = None
        
        if sys.platform == "darwin":
            self.player.set_nsobject(int(self.winId()))
        
        # Initialize with proper scaling
        self.player.video_set_scale(0)  # Auto scale
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
        
        # Enable hardware acceleration for Qt
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
