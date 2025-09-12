#!/usr/bin/env python3
"""
M3U8 Multi-Monitor Video Wall
----------------------------
Author: Jason Paul Michaels
Version: 3.0.1
"""

import sys
import random
import vlc
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                            QFileDialog, QFrame, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, QSize, QRect
from PyQt5.QtGui import QPalette, QColor

class VideoTile(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 180)
        self.setStyleSheet("""
            QFrame { 
                background-color: black; 
                border: 1px solid #333;
                border-radius: 4px;
            }
        """)
        
        # Enhanced VLC instance with optimized settings and hardware acceleration
        vlc_args = [
            '--no-xlib',
            '--network-caching=3000',
            '--live-caching=3000',
            '--file-caching=1000',
            '--disc-caching=3000',
            '--clock-jitter=0',
            '--clock-synchro=0',
            '--no-audio',
            '--avcodec-fast',
            '--avcodec-skiploopfilter=2',
            '--avcodec-skip-frame=2',
            '--avcodec-skip-idct=2',
            '--vout=gpu',
            '--avcodec-hw=any',
            '--avcodec-threads=0'
        ]
        
        self.instance = vlc.Instance(' '.join(vlc_args))
        self.player = self.instance.media_player_new()
        
        if sys.platform == "darwin":
            self.player.set_nsobject(int(self.winId()))
        else:
            self.player.set_xwindow(int(self.winId()))
        
        self.current_stream = None
        self.error_count = 0
        self.max_errors = 3
        self.last_restart = 0
        self.restart_cooldown = 5  # seconds

    def play_stream(self, url):
        try:
            self.current_stream = url
            media = self.instance.media_new(url)
            media.add_option('network-caching=3000')
            media.add_option('clock-jitter=0')
            media.add_option('clock-synchro=0')
            media.add_option('http-reconnect=true')
            media.add_option('http-continuous=true')
            self.player.set_media(media)
            self.player.play()
            self.error_count = 0
            print(f"Playing stream: {url}")
        except Exception as e:
            print(f"Error playing stream {url}: {e}")
            self.error_count += 1

    def stop(self):
        try:
            self.player.stop()
            self.current_stream = None
        except Exception as e:
            print(f"Error stopping player: {e}")

    def restart_stream(self):
        current_time = time.time()
        if self.current_stream and (current_time - self.last_restart) > self.restart_cooldown:
            self.stop()
            self.play_stream(self.current_stream)
            self.last_restart = current_time

    def is_healthy(self):
        return (self.player.is_playing() and 
                self.error_count < self.max_errors and 
                self.player.get_state() not in [vlc.State.Error, vlc.State.Ended])

class VideoWallWindow(QMainWindow):
    def __init__(self, screen, streams, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Video Wall - Screen {screen.name()}")
        self.setGeometry(screen.geometry())
        self.streams = streams
        
        # Set window properties for full coverage
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.grid = QGridLayout(central_widget)
        self.grid.setSpacing(2)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        self.tiles = []
        self.setup_grid(screen.geometry())

    def setup_grid(self, geometry):
        # Calculate optimal grid size based on screen resolution
        aspect_ratio = geometry.width() / geometry.height()
        if aspect_ratio > 1.77:  # Wider screen
            rows, cols = 3, 4
        else:
            rows, cols = 4, 3
            
        tile_width = geometry.width() // cols
        tile_height = geometry.height() // rows
        
        for i in range(rows):
            for j in range(cols):
                tile = VideoTile(self)
                tile.setFixedSize(tile_width, tile_height)
                self.grid.addWidget(tile, i, j)
                self.tiles.append(tile)
                
        # Start playback for this window's tiles
        self.start_playback()

    def start_playback(self):
        for tile in self.tiles:
            if self.streams:
                stream = random.choice(self.streams)
                tile.play_stream(stream)

class MultiMonitorVideoWall:
    def __init__(self, streams):
        self.streams = streams
        self.windows = []
        self.setup_windows()
        
        # Global rotation timer
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_all_streams)
        self.rotation_timer.start(30000)  # 30 second rotation
        
        # Global health check timer
        self.health_check_timer = QTimer()
        self.health_check_timer.timeout.connect(self.check_all_streams)
        self.health_check_timer.start(5000)  # 5 second health check

    def setup_windows(self):
        screens = QApplication.screens()
        for screen in screens:
            window = VideoWallWindow(screen, self.streams)
            window.show()
            self.windows.append(window)

    def rotate_all_streams(self):
        for window in self.windows:
            for tile in window.tiles:
                if random.random() < 0.3:  # 30% chance to rotate each tile
                    stream = random.choice(self.streams)
                    tile.stop()
                    tile.play_stream(stream)

    def check_all_streams(self):
        for window in self.windows:
            for tile in window.tiles:
                if not tile.is_healthy():
                    stream = random.choice(self.streams)
                    tile.play_stream(stream)

    def handle_key_event(self, event):
        if event.key() == Qt.Key_Escape:
            for window in self.windows:
                window.close()
        elif event.key() == Qt.Key_Space:
            for window in self.windows:
                for tile in window.tiles:
                    if tile.player.is_playing():
                        tile.player.pause()
                    else:
                        tile.player.play()
        elif event.key() == Qt.Key_Left:
            self.rotate_all_streams()
        elif event.key() == Qt.Key_Down:
            for window in self.windows:
                for tile in window.tiles:
                    tile.restart_stream()

def main():
    app = QApplication(sys.argv)
    
    # Enable Qt hardware acceleration
    app.setAttribute(Qt.AA_UseOpenGLES, True)
    app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
    app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
    
    # Set application-wide dark theme
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    # File selection
    file_dialog = QFileDialog()
    file_dialog.setNameFilter("M3U8 Lists (*.txt *.m3u *.m3u8)")
    file_dialog.setWindowTitle("Select Stream List")
    
    if file_dialog.exec_():
        file_path = file_dialog.selectedFiles()[0]
        try:
            with open(file_path, 'r') as f:
                streams = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not streams:
                QMessageBox.warning(None, "Error", "No valid streams found in file")
                return 1
                
            wall = MultiMonitorVideoWall(streams)
            return app.exec_()
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error loading streams: {e}")
            return 1
    return 1

if __name__ == "__main__":
    sys.exit(main())
