"""
Main VideoWall implementation.
"""
import os
import random
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from src.config.settings import DEFAULT_GRID_ROWS, DEFAULT_GRID_COLS
from src.core.display_manager import DisplayManager
from src.core.video_manager import VideoManager
from src.core.layout_manager import LayoutManager

class VideoWall(QMainWindow):
    """
    VideoWall main window class responsible for managing multiple
    video tiles across one or more monitors.
    """
    
    def __init__(self, app, m3u8_links=None, local_videos=None, screen=None, parent=None):
        """
        Initialize the VideoWall with configuration.
        
        Args:
            app (QApplication): The Qt application instance
            m3u8_links (list, optional): List of M3U8 stream URLs
            local_videos (list, optional): List of local video file paths
            screen (QScreen, optional): Screen to display the video wall on
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.app = app
        self.screen = screen
        self.m3u8_links = m3u8_links or []
        self.local_videos = local_videos or []
        self.is_fullscreen = True
        self.windowed_geometry = None
        
        # Window setup
        self.setWindowTitle(f"VideoWall - {screen.name() if screen else 'Default'}")
        if screen:
            self.setGeometry(screen.geometry())
        self.showFullScreen()
        
        # Store original geometry to restore when toggling
        self.windowed_geometry = self.geometry()
        
        # Initialize display manager
        self.display_manager = DisplayManager(self)
        
        # Initialize grid and tiles
        self.display_manager.initialize_grid(animator=True)
        
        # Initialize video manager
        self.video_manager = VideoManager(self, m3u8_links, local_videos)
        
        # Initialize layout manager
        self.layout_manager = LayoutManager(self.display_manager)
        
        # Initialize animator
        self.animator = self.display_manager.animator
        
        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Set up periodic refresh timer
        self._setup_refresh_timer()
        
        # Initial content assignment (delayed to prevent blocking)
        QTimer.singleShot(1000, self.refresh_all_videos)  # Start videos after 1 second
    
    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for the application."""
        # Right arrow key triggers manual refresh
        self.right_key_timer = QTimer(self)
        self.right_key_timer.setSingleShot(True)
        self.right_key_timer.timeout.connect(self.refresh_all_videos)
    
    def _setup_refresh_timer(self):
        """Set up periodic refresh timer for stream health checks."""
        self.stream_check_timer = QTimer(self)
        self.stream_check_timer.timeout.connect(self.check_stream_health)
        self.stream_check_timer.start(30000)  # 30 seconds
    
    def refresh_all_videos(self):
        """Refresh all videos with new content and layout."""
        # Stop animations
        if self.animator:
            self.animator.stop_timers_and_animations()
        
        # Pause all players
        self.video_manager.pause_all_players()
        
        # Apply a new random layout
        layout_pattern = self.layout_manager.apply_random_layout()
        print(f"Applied {layout_pattern} layout pattern")
        
        # Assign videos to tiles
        self.video_manager.assign_content_to_tiles()
        
        # Resume playback after a delay for smooth transition
        QTimer.singleShot(500, self.video_manager.resume_visible_players)
        
        # Restart animator
        if self.animator:
            self.animator.start_random_timer()
    
    def check_stream_health(self):
        """Check the health of all streams and retry if needed."""
        for i, player in enumerate(self.video_manager.players):
            # Check only visible stream tiles (not local videos)
            if (self.display_manager.tiles[i].isVisible() and 
                not self.video_manager.using_local_video.get(i, True)):
                
                # Check if player is in a good state
                if player.state() != QMediaPlayer.PlayingState:
                    # Try to recover the stream
                    print(f"Stream health check: Tile {i} needs recovery")
                    self.video_manager.retry_tile_stream(i)
    
    def keyPressEvent(self, event):
        """
        Handle key press events for the application.
        
        Args:
            event (QKeyEvent): Key event
        """
        key = event.key()
        
        if key == Qt.Key_Escape:
            # Escape key exits fullscreen or quits
            if self.is_fullscreen:
                self.display_manager.toggle_fullscreen()
            else:
                self.close()
                
        elif key == Qt.Key_F11 or (event.modifiers() == Qt.AltModifier and key == Qt.Key_F):
            # F11 or Alt+F toggles fullscreen
            self.display_manager.toggle_fullscreen()
            
        elif key == Qt.Key_Right:
            # Right arrow key triggers manual refresh
            if not self.right_key_timer.isActive():
                print("Manual refresh triggered")
                self.right_key_timer.start(500)  # Debounce for 500ms
                
        elif event.modifiers() == Qt.ControlModifier and key == Qt.Key_Q:
            # Ctrl+Q quits the application
            self.close()
            
        else:
            # Pass other key events to parent class
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event (QCloseEvent): Close event
        """
        # Stop all timers
        if hasattr(self, 'stream_check_timer'):
            self.stream_check_timer.stop()
        
        if hasattr(self, 'right_key_timer'):
            self.right_key_timer.stop()
        
        # Stop animations
        if self.animator:
            self.animator.stop_timers_and_animations()
        
        # Pause all players
        if hasattr(self, 'video_manager'):
            self.video_manager.pause_all_players()
        
        # Accept the close event
        event.accept()