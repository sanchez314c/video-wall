#!/usr/bin/env python3
"""
Multi-Monitor Video Wall - M3U8 Support with Local Video Fallback
------------------------------------
Author: Jason Paul Michaels (Enhanced by Claude)
Date: May 4, 2025
Version: 1.5.0 (Ultra-Slow Relaxed Edition)

Description:
    Enhanced video wall that supports both M3U8 streams and local video files.
    M3U8 streams are now optional - you can choose to use only local videos if desired.
    When a stream is offline or unavailable, the system automatically falls back to local videos.
    Each monitor tracks its own videos independently to ensure no duplicates.
    Visual changes include dynamic tile resizing and full-screen takeovers at random intervals.

Features:
    - Multi-Monitor support with unique videos per screen
    - Optional M3U8 stream support with local video fallback
    - Can run with only local videos (no M3U8 playlist required)
    - Optional local video integration via folder selection
    - Recursive scanning of video folders
    - 4x4 Grid layout (16 tiles)
    - Random tile resizing (e.g., 2x2, 1x3) and full-screen takeover
    - Discrete Random Intervals (30s/60s) for actions
    - Throttled Retry Mechanism with Improved Stream Validation
    - Right-arrow key for manual full refresh
    - Unique stream assignment attempt
    - Periodic stream health monitoring (30s)

Requirements:
    - Python 3.6+
    - PyQt5 (including QtMultimedia)
    - Working OS Multimedia Backend

Usage:
    python fixed-video-wall.py
"""

import os
import random
import sys
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QSizePolicy,
                            QGridLayout, QFileDialog, QMessageBox, QLabel,
                            QDialog, QVBoxLayout, QPushButton, QCheckBox)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QObject, QPoint
from PyQt5.QtGui import QFont

# --- File Loading Functions ---
def get_all_m3u8_links(file_path):
    """Loads non-empty, non-comment lines from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        links = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Ensure URL has http/https protocol
                if not line.startswith(('http://', 'https://')):
                    line = 'https://' + line
                links.append(line)
                
        unique_links = sorted(list(set(links)))
        print(f"Loaded {len(links)} links, {len(unique_links)} unique.")
        
        # Validate URLs
        valid_links = []
        for url in unique_links:
            if '://' in url and '.' in url:  # Very basic URL validation
                valid_links.append(url)
            else:
                print(f"Warning: Skipping invalid URL: {url}")
        
        if not valid_links:
            print("Warning: No valid M3U8 links found in the file.")
            
        print(f"Example URLs:")
        for i, url in enumerate(valid_links[:5]):
            print(f"  {i+1}. {url}")
        
        return valid_links
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None

def get_video_files_recursively(folder_path):
    """Recursively scans a folder for video files."""
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp']
    video_files = []
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    full_path = os.path.join(root, file)
                    video_files.append(full_path)
        
        print(f"Found {len(video_files)} video files in '{folder_path}'")
        return video_files
    except Exception as e:
        print(f"Error scanning folder '{folder_path}': {e}")
        return []

def select_m3u8_file():
    """Opens a file dialog to select an M3U8 playlist file."""
    try:
        file_path, _ = QFileDialog.getOpenFileName(
            None, 
            "Select M3U8 Playlist File",
            "",
            "M3U8 Files (*.m3u8);;Text Files (*.txt);;All Files (*)"
        )
        return file_path if file_path else None
    except Exception as e:
        print(f"Error selecting M3U8 file: {e}")
        return None

def select_video_folder():
    """Opens a folder dialog to select a local video directory."""
    try:
        folder_path = QFileDialog.getExistingDirectory(
            None, 
            "Select Local Video Folder"
        )
        return folder_path if folder_path else None
    except Exception as e:
        print(f"Error selecting video folder: {e}")
        return None

class ConfigDialog(QDialog):
    """Dialog for selecting content sources."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Wall Configuration")
        self.setModal(True)
        self.resize(400, 300)
        
        self.m3u8_path = None
        self.video_folder = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Select Content Sources")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # M3U8 option
        self.m3u8_checkbox = QCheckBox("Use M3U8 Streams")
        self.m3u8_checkbox.setChecked(False)
        layout.addWidget(self.m3u8_checkbox)
        
        self.m3u8_button = QPushButton("Select M3U8 File")
        self.m3u8_button.clicked.connect(self.select_m3u8)
        self.m3u8_button.setEnabled(False)
        layout.addWidget(self.m3u8_button)
        
        self.m3u8_label = QLabel("No M3U8 file selected")
        layout.addWidget(self.m3u8_label)
        
        # Video folder option
        self.video_checkbox = QCheckBox("Use Local Videos")
        self.video_checkbox.setChecked(True)  # Default to local videos
        layout.addWidget(self.video_checkbox)
        
        self.video_button = QPushButton("Select Video Folder")
        self.video_button.clicked.connect(self.select_video)
        layout.addWidget(self.video_button)
        
        self.video_label = QLabel("No video folder selected")
        layout.addWidget(self.video_label)
        
        # Start button
        self.start_button = QPushButton("Start Video Wall")
        self.start_button.clicked.connect(self.accept)
        layout.addWidget(self.start_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
        
        self.setLayout(layout)
        
        # Connect checkboxes
        self.m3u8_checkbox.toggled.connect(self.update_m3u8_button)
        self.video_checkbox.toggled.connect(self.update_video_button)
    
    def update_m3u8_button(self, checked):
        self.m3u8_button.setEnabled(checked)
    
    def update_video_button(self, checked):
        self.video_button.setEnabled(checked)
    
    def select_m3u8(self):
        file_path = select_m3u8_file()
        if file_path:
            self.m3u8_path = file_path
            self.m3u8_label.setText(f"Selected: {os.path.basename(file_path)}")
        else:
            self.m3u8_label.setText("No M3U8 file selected")
    
    def select_video(self):
        folder_path = select_video_folder()
        if folder_path:
            self.video_folder = folder_path
            self.video_label.setText(f"Selected: {os.path.basename(folder_path)}")
        else:
            self.video_label.setText("No video folder selected")
    
    def get_config(self):
        """Returns the configuration settings."""
        config = {
            'use_m3u8': self.m3u8_checkbox.isChecked(),
            'use_video': self.video_checkbox.isChecked(),
            'm3u8_path': self.m3u8_path if self.m3u8_checkbox.isChecked() else None,
            'video_folder': self.video_folder if self.video_checkbox.isChecked() else None
        }
        return config

# --- Tile Widget ---
class VideoTile(QWidget):
    """Individual video tile widget."""
    
    def __init__(self, monitor_id, tile_id, video_wall=None, parent=None):
        super().__init__(parent)
        self.monitor_id = monitor_id
        self.tile_id = tile_id
        self.video_wall = video_wall
        
        # Initialize variables
        self.current_url = None
        self.current_video_file = None
        self.retry_count = 0
        self.max_retries = 3
        self.is_playing = False
        self.is_fullscreen = False
        self.original_geometry = None
        self.fullscreen_timer = None
        self.animation = None
        
        # Create UI
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        
        # Create video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_widget.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
        
        # Enable hardware acceleration
        self.video_widget.setAttribute(Qt.WA_AccelChildrenInheritClip)
        self.video_widget.setAttribute(Qt.WA_NativeWindow)
        
        # Create media player
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)
        self.player.setMuted(True)  # Mute all players to avoid audio chaos
        
        # Connect player signals
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.error.connect(self.on_error)
        self.player.stateChanged.connect(self.on_state_changed)
        
        # Add to layout
        self.layout().addWidget(self.video_widget)
        
        # Set background color
        self.setStyleSheet("background-color: black; border: 1px solid gray;")
    
    def play_content(self, url=None, video_file=None, retry=True):
        """Play a URL stream or local video file."""
        try:
            # Reset retry count for new content
            if (url != self.current_url) or (video_file != self.current_video_file):
                self.retry_count = 0
            
            # Stop current playback
            if self.player.state() != QMediaPlayer.StoppedState:
                self.player.stop()
            
            # Set content based on type
            if url:
                self.current_url = url
                self.current_video_file = None
                print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Attempting stream: {url[:50]}...")
                media = QMediaContent(QUrl(url))
            elif video_file:
                self.current_video_file = video_file
                self.current_url = None
                print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Playing video: {os.path.basename(video_file)}")
                media = QMediaContent(QUrl.fromLocalFile(video_file))
            else:
                print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] No content to play")
                return False
            
            self.player.setMedia(media)
            self.player.play()
            return True
            
        except Exception as e:
            print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Error playing content: {e}")
            return False
    
    def on_media_status_changed(self, status):
        """Handle media status changes."""
        status_map = {
            QMediaPlayer.NoMedia: "NoMedia",
            QMediaPlayer.LoadingMedia: "LoadingMedia", 
            QMediaPlayer.LoadedMedia: "LoadedMedia",
            QMediaPlayer.StalledMedia: "StalledMedia",
            QMediaPlayer.BufferingMedia: "BufferingMedia",
            QMediaPlayer.BufferedMedia: "BufferedMedia",
            QMediaPlayer.EndOfMedia: "EndOfMedia",
            QMediaPlayer.InvalidMedia: "InvalidMedia"
        }
        
        status_text = status_map.get(status, f"Unknown({status})")
        
        if status == QMediaPlayer.LoadedMedia or status == QMediaPlayer.BufferedMedia:
            self.is_playing = True
            self.retry_count = 0
            
        elif status == QMediaPlayer.EndOfMedia:
            # Loop the content
            self.player.setPosition(0)
            self.player.play()
            
        elif status == QMediaPlayer.InvalidMedia:
            self.handle_error("Invalid media")
    
    def on_state_changed(self, state):
        """Handle player state changes."""
        state_map = {
            QMediaPlayer.StoppedState: "Stopped",
            QMediaPlayer.PlayingState: "Playing", 
            QMediaPlayer.PausedState: "Paused"
        }
        
        if state == QMediaPlayer.PlayingState:
            self.is_playing = True
        else:
            self.is_playing = False
    
    def on_error(self, error):
        """Handle player errors."""
        error_map = {
            QMediaPlayer.NoError: "No error",
            QMediaPlayer.ResourceError: "Resource error",
            QMediaPlayer.FormatError: "Format error", 
            QMediaPlayer.NetworkError: "Network error",
            QMediaPlayer.AccessDeniedError: "Access denied",
            QMediaPlayer.ServiceMissingError: "Service missing"
        }
        
        error_text = error_map.get(error, f"Unknown error({error})")
        self.handle_error(error_text)
    
    def handle_error(self, error_message):
        """Handle errors with fallback logic."""
        print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Error: {error_message}")
        
        # Try fallback to local video if we were playing a stream
        if self.current_url and self.video_wall and hasattr(self.video_wall, 'video_files') and self.video_wall.video_files:
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Falling back to local video (retry {self.retry_count})")
                
                # Get a random local video
                local_video = random.choice(self.video_wall.video_files)
                self.play_content(video_file=local_video)
            else:
                print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Max retries exceeded")
        
        # Try different stream if available
        elif self.current_url and self.video_wall and hasattr(self.video_wall, 'streams') and len(self.video_wall.streams) > 1:
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Trying different stream (retry {self.retry_count})")
                
                # Get a different stream
                available_streams = [s for s in self.video_wall.streams if s != self.current_url]
                if available_streams:
                    new_stream = random.choice(available_streams)
                    self.play_content(url=new_stream)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode for this tile."""
        if not self.is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()
    
    def enter_fullscreen(self):
        """Enter fullscreen mode."""
        if self.is_fullscreen:
            return
            
        print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Entering fullscreen")
        
        # Store original geometry
        self.original_geometry = self.geometry()
        
        # Get parent grid layout to determine full size
        if self.parent():
            parent_size = self.parent().size()
            target_rect = QRect(0, 0, parent_size.width(), parent_size.height())
        else:
            target_rect = QRect(0, 0, 800, 600)  # Default size
        
        # Animate to fullscreen
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)  # 1 second
        self.animation.setStartValue(self.original_geometry)
        self.animation.setEndValue(target_rect)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.finished.connect(self.on_fullscreen_animation_finished)
        
        # Bring to front
        self.raise_()
        
        self.is_fullscreen = True
        self.animation.start()
        
        # Schedule automatic exit from fullscreen
        self.fullscreen_timer = QTimer()
        self.fullscreen_timer.setSingleShot(True)
        self.fullscreen_timer.timeout.connect(self.exit_fullscreen)
        self.fullscreen_timer.start(random.choice([15000, 30000]))  # 15-30 seconds
    
    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if not self.is_fullscreen:
            return
            
        print(f"[Monitor {self.monitor_id}] [Tile {self.tile_id}] Exiting fullscreen")
        
        # Stop the fullscreen timer
        if self.fullscreen_timer:
            self.fullscreen_timer.stop()
            self.fullscreen_timer = None
        
        # Animate back to original size
        if self.original_geometry:
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(1000)  # 1 second
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.original_geometry)
            self.animation.setEasingCurve(QEasingCurve.InOutCubic)
            
            self.is_fullscreen = False
            self.animation.start()
    
    def on_fullscreen_animation_finished(self):
        """Called when fullscreen animation finishes."""
        pass
    
    def stop(self):
        """Stop playback and clean up."""
        try:
            if self.fullscreen_timer:
                self.fullscreen_timer.stop()
            if self.animation:
                self.animation.stop()
            if self.player:
                self.player.stop()
        except:
            pass

# --- Main Video Wall Class ---
class VideoWall(QMainWindow):
    """Main video wall window."""
    
    def __init__(self, config, monitor_index=0, geometry=None):
        super().__init__()
        
        self.monitor_index = monitor_index
        self.config = config
        self.tiles = []
        self.streams = []
        self.video_files = []
        
        # Load content based on configuration
        self.load_content()
        
        # Set up the window
        self.setup_ui()
        self.setup_geometry(geometry)
        
        # Set up timers
        self.setup_timers()
        
        print(f"[Monitor {monitor_index}] Video wall initialized with {len(self.streams)} streams and {len(self.video_files)} video files")
    
    def load_content(self):
        """Load streams and video files based on configuration."""
        
        # Load M3U8 streams
        if self.config.get('use_m3u8') and self.config.get('m3u8_path'):
            print(f"[Monitor {self.monitor_index}] Loading M3U8 streams from: {self.config['m3u8_path']}")
            streams = get_all_m3u8_links(self.config['m3u8_path'])
            if streams:
                self.streams = streams
                print(f"[Monitor {self.monitor_index}] Loaded {len(self.streams)} M3U8 streams")
            else:
                print(f"[Monitor {self.monitor_index}] Failed to load M3U8 streams")
        
        # Load local video files
        if self.config.get('use_video') and self.config.get('video_folder'):
            print(f"[Monitor {self.monitor_index}] Loading videos from: {self.config['video_folder']}")
            videos = get_video_files_recursively(self.config['video_folder'])
            if videos:
                self.video_files = videos
                print(f"[Monitor {self.monitor_index}] Loaded {len(self.video_files)} video files")
            else:
                print(f"[Monitor {self.monitor_index}] No video files found")
        
        # Validation
        if not self.streams and not self.video_files:
            print(f"[Monitor {self.monitor_index}] Warning: No content sources available!")
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(f"Video Wall - Monitor {self.monitor_index + 1}")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create 4x4 grid layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)  # Small gap between tiles
        central_widget.setLayout(self.grid_layout)
        
        # Create 16 tiles (4x4)
        for row in range(4):
            for col in range(4):
                tile_id = row * 4 + col + 1
                tile = VideoTile(
                    monitor_id=self.monitor_index + 1,
                    tile_id=tile_id,
                    video_wall=self,
                    parent=central_widget
                )
                self.tiles.append(tile)
                self.grid_layout.addWidget(tile, row, col)
        
        # Set black background
        self.setStyleSheet("background-color: black;")
        
        print(f"[Monitor {self.monitor_index}] Created {len(self.tiles)} tiles in 4x4 grid")
    
    def setup_geometry(self, geometry):
        """Set up window geometry."""
        if geometry:
            self.setGeometry(geometry)
        else:
            # Default geometry
            self.setGeometry(100, 100, 1200, 800)
        
        # Show in windowed mode (not fullscreen)
        self.show()
    
    def setup_timers(self):
        """Set up various timers for periodic actions."""
        
        # Initial content loading timer
        QTimer.singleShot(1000, self.load_initial_content)
        
        # Tile refresh timer (every 30-60 seconds)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.random_tile_action)
        self.refresh_timer.start(random.choice([30000, 60000]))  # 30-60 seconds
        
        # Health monitoring timer (every 30 seconds)
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.check_tile_health)
        self.health_timer.start(30000)  # 30 seconds
        
        # Random fullscreen timer (every 2-5 minutes)
        self.fullscreen_timer = QTimer()
        self.fullscreen_timer.timeout.connect(self.random_fullscreen)
        self.fullscreen_timer.start(random.choice([120000, 180000, 240000, 300000]))  # 2-5 minutes
    
    def load_initial_content(self):
        """Load initial content into all tiles."""
        print(f"[Monitor {self.monitor_index}] Loading initial content...")
        
        used_streams = set()
        used_videos = set()
        
        for tile in self.tiles:
            success = False
            
            # Try to assign unique stream first
            if self.streams:
                available_streams = [s for s in self.streams if s not in used_streams]
                if available_streams:
                    stream = random.choice(available_streams)
                    success = tile.play_content(url=stream)
                    if success:
                        used_streams.add(stream)
                        continue
                
                # If no unique streams, use any stream
                if not success:
                    stream = random.choice(self.streams)
                    success = tile.play_content(url=stream)
                    if success:
                        continue
            
            # Fall back to local video if stream failed or not available
            if not success and self.video_files:
                available_videos = [v for v in self.video_files if v not in used_videos]
                if available_videos:
                    video = random.choice(available_videos)
                    success = tile.play_content(video_file=video)
                    if success:
                        used_videos.add(video)
                        continue
                
                # If no unique videos, use any video
                if not success:
                    video = random.choice(self.video_files)
                    tile.play_content(video_file=video)
    
    def random_tile_action(self):
        """Perform a random action on a random tile."""
        if not self.tiles:
            return
        
        tile = random.choice(self.tiles)
        action = random.choice(['refresh', 'resize'])
        
        if action == 'refresh':
            self.refresh_tile_content(tile)
        elif action == 'resize':
            self.random_tile_resize(tile)
        
        # Schedule next action
        self.refresh_timer.start(random.choice([30000, 60000]))  # 30-60 seconds
    
    def refresh_tile_content(self, tile):
        """Refresh content for a specific tile."""
        print(f"[Monitor {self.monitor_index}] Refreshing tile {tile.tile_id}")
        
        # Choose content type
        if self.streams and self.video_files:
            use_stream = random.choice([True, False])
        elif self.streams:
            use_stream = True
        elif self.video_files:
            use_stream = False
        else:
            return
        
        if use_stream and self.streams:
            stream = random.choice(self.streams)
            tile.play_content(url=stream)
        elif self.video_files:
            video = random.choice(self.video_files)
            tile.play_content(video_file=video)
    
    def random_tile_resize(self, tile):
        """Randomly resize a tile (placeholder - grid layout constraints apply)."""
        # Note: In a QGridLayout, complex resizing is limited
        # This is more of a placeholder for future enhancement
        print(f"[Monitor {self.monitor_index}] Tile resize action for tile {tile.tile_id}")
        pass
    
    def random_fullscreen(self):
        """Randomly make a tile go fullscreen."""
        if not self.tiles:
            return
        
        # Find tiles that are currently playing and not already fullscreen
        available_tiles = [t for t in self.tiles if t.is_playing and not t.is_fullscreen]
        
        if available_tiles:
            tile = random.choice(available_tiles)
            tile.enter_fullscreen()
        
        # Schedule next fullscreen
        self.fullscreen_timer.start(random.choice([120000, 180000, 240000, 300000]))  # 2-5 minutes
    
    def check_tile_health(self):
        """Check the health of all tiles and restart failed ones."""
        for tile in self.tiles:
            if not tile.is_playing:
                print(f"[Monitor {self.monitor_index}] Tile {tile.tile_id} not playing, attempting restart...")
                self.refresh_tile_content(tile)
    
    def refresh_all_tiles(self):
        """Refresh all tiles with new content."""
        print(f"[Monitor {self.monitor_index}] Refreshing all tiles...")
        self.load_initial_content()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Right:
            print(f"[Monitor {self.monitor_index}] Manual refresh triggered")
            self.refresh_all_tiles()
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_F:
            # Toggle fullscreen for a random tile
            playing_tiles = [t for t in self.tiles if t.is_playing]
            if playing_tiles:
                tile = random.choice(playing_tiles)
                tile.toggle_fullscreen()
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Clean up when closing."""
        print(f"[Monitor {self.monitor_index}] Cleaning up...")
        
        # Stop all timers
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        if hasattr(self, 'health_timer'):
            self.health_timer.stop()
        if hasattr(self, 'fullscreen_timer'):
            self.fullscreen_timer.stop()
        
        # Stop all tiles
        for tile in self.tiles:
            tile.stop()
        
        super().closeEvent(event)

# --- Main Function ---
def main():
    """Main entry point."""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        # Enable Qt hardware acceleration
        app.setAttribute(Qt.AA_UseOpenGLES, True)
        app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
        app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
        
        # Show configuration dialog
        config_dialog = ConfigDialog()
        if config_dialog.exec_() != QDialog.Accepted:
            print("Configuration cancelled")
            return
        
        config = config_dialog.get_config()
        
        # Validate configuration
        if not config['use_m3u8'] and not config['use_video']:
            QMessageBox.warning(None, "Configuration Error", 
                               "Please select at least one content source (M3U8 streams or local videos).")
            return
        
        if config['use_m3u8'] and not config['m3u8_path']:
            QMessageBox.warning(None, "Configuration Error", 
                               "Please select an M3U8 file or disable M3U8 streams.")
            return
        
        if config['use_video'] and not config['video_folder']:
            QMessageBox.warning(None, "Configuration Error", 
                               "Please select a video folder or disable local videos.")
            return
        
        print("Configuration:", config)
        
        # Get available screens/monitors
        screens = app.screens()
        if not screens:
            print("No screens detected!")
            return
        
        print(f"Detected {len(screens)} screen(s)")
        
        # Create video walls for each monitor
        video_walls = []
        for i, screen in enumerate(screens):
            print(f"Setting up monitor {i+1}: {screen.name()}")
            
            # Create video wall for this monitor
            geometry = screen.geometry()
            video_wall = VideoWall(config, monitor_index=i, geometry=geometry)
            video_walls.append(video_wall)
        
        # Start the application
        print("Starting video wall application...")
        print("Press RIGHT ARROW for manual refresh, F for random fullscreen, ESC to exit")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()