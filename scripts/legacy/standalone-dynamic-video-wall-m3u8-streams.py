#!/usr/bin/env python3
"""
Dynamic Video Wall Player
------------------------
Author: Jason Paul Michaels
Date: March 3, 2025
Version: 1.0.0

Creates a dynamic video wall with randomly sized and positioned streams.
Features:
- Auto-rotating streams with custom timing
- Randomly generated layouts
- Borderless playback windows
- Multi-monitor support
- Command-line configurable
"""

import os
import sys
import random
import time
import logging
import argparse
import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_THREADS = max(multiprocessing.cpu_count() - 1, 1)

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QGridLayout,
        QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
    )
    from PyQt5.QtCore import Qt, QTimer, QRect, QUrl, QSize, pyqtSignal
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    from PyQt5.QtGui import QColor, QPalette
except ImportError:
    logger.error("Required libraries not found. Please install the following packages:")
    logger.error("pip install PyQt5")
    sys.exit(1)

def show_message(title: str, message: str, message_type: str = "info") -> None:
    """
    Display a standardized message dialog.
    
    Args:
        title: Dialog title
        message: Message text
        message_type: One of "info", "warning", "error"
    """
    root = tk.Tk()
    root.withdraw()
    
    if message_type == "info":
        messagebox.showinfo(title, message, parent=root)
    elif message_type == "warning":
        messagebox.showwarning(title, message, parent=root)
    elif message_type == "error":
        messagebox.showerror(title, message, parent=root)
    else:
        messagebox.showinfo(title, message, parent=root)

def get_file_path(title: str = "Select File", 
                  filetypes: List[Tuple[str, str]] = None, 
                  initial_dir: str = None) -> Optional[str]:
    """
    Display native file selection dialog.
    
    Args:
        title: Dialog window title
        filetypes: List of (label, pattern) tuples
        initial_dir: Starting directory
        
    Returns:
        str: Selected file path or None if canceled
    """
    if filetypes is None:
        filetypes = [("All Files", "*.*")]
    
    if initial_dir is None:
        initial_dir = str(Path.home())
        
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=filetypes,
        initialdir=initial_dir
    )
    
    return file_path if file_path else None

class StreamTile(QVideoWidget):
    """Video widget for displaying stream content."""
    
    error_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Initialize video tile.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up appearance
        self.setStyleSheet("background-color: black; border: none;")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Enable hardware acceleration
        self.setAttribute(Qt.WA_AccelChildrenInheritClip)
        self.setAttribute(Qt.WA_NativeWindow)
        
        # Create media player
        self.player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.player.setVideoOutput(self)
        
        # Connect error handler
        self.player.error.connect(self._handle_error)
        
    def set_stream(self, url: str) -> None:
        """
        Set and play stream URL.
        
        Args:
            url: Stream URL
        """
        try:
            logger.debug(f"Setting stream: {url}")
            self.player.setMedia(QMediaContent(QUrl(url)))
            self.player.play()
        except Exception as e:
            logger.error(f"Error setting stream: {str(e)}")
            self.error_signal.emit(str(e))
    
    def stop(self) -> None:
        """Stop playback and release resources."""
        self.player.stop()
    
    def _handle_error(self) -> None:
        """Handle media player errors."""
        error = self.player.errorString()
        if error:
            logger.error(f"Player error: {error}")
            self.error_signal.emit(error)

class DynamicVideoWall(QMainWindow):
    """Main application window for video wall."""
    
    def __init__(self, stream_file: str, layout_interval: int = 30, 
                 stream_interval: int = 45, min_tiles: int = 3, 
                 max_tiles: int = 8, fullscreen: bool = True):
        """
        Initialize video wall.
        
        Args:
            stream_file: Path to file containing stream URLs
            layout_interval: Seconds between layout changes
            stream_interval: Seconds between stream rotations
            min_tiles: Minimum number of video tiles
            max_tiles: Maximum number of video tiles
            fullscreen: Whether to display in fullscreen mode
        """
        super().__init__()
        
        # Store configuration
        self.layout_interval = layout_interval * 1000  # Convert to milliseconds
        self.stream_interval = stream_interval * 1000  # Convert to milliseconds
        self.min_tiles = min_tiles
        self.max_tiles = max_tiles
        
        # Set up window
        self.setWindowTitle("Dynamic Video Wall")
        if fullscreen:
            self.showFullScreen()
        else:
            self.resize(1280, 720)
        
        # Set dark background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Load stream URLs
        self.load_streams(stream_file)
        
        # Initialize tiles container
        self.tiles = []
        
        # Create initial layout
        self.create_random_layout()
        
        # Setup timers
        self.layout_timer = QTimer(self)
        self.layout_timer.timeout.connect(self.create_random_layout)
        self.layout_timer.start(self.layout_interval)
        
        self.stream_timer = QTimer(self)
        self.stream_timer.timeout.connect(self.rotate_streams)
        self.stream_timer.start(self.stream_interval)
        
        # Status display timer (fades after 5 seconds)
        self.status_label = QLabel(self)
        self.status_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 180); padding: 10px; border-radius: 5px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.status_label.hide)
        
        # Log startup information
        logger.info(f"Video wall initialized with {len(self.streams)} streams")
        logger.info(f"Layout change interval: {self.layout_interval/1000}s")
        logger.info(f"Stream rotation interval: {self.stream_interval/1000}s")
        
        # Show initial status
        self.show_status(f"Video wall started with {len(self.streams)} streams")

    def load_streams(self, stream_file: str) -> None:
        """
        Load stream URLs from file.
        
        Args:
            stream_file: Path to file containing stream URLs
        """
        try:
            with open(stream_file, 'r') as f:
                self.streams = [line.strip() for line in f if line.strip() and line.strip().endswith('.m3u8')]
                
            logger.info(f"Loaded {len(self.streams)} streams from {stream_file}")
            
            if not self.streams:
                show_message(
                    "No Streams",
                    f"No valid m3u8 streams found in {stream_file}",
                    "error"
                )
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Error loading streams: {str(e)}")
            show_message(
                "Error Loading Streams",
                f"Failed to load streams from {stream_file}: {str(e)}",
                "error"
            )
            sys.exit(1)
    
    def clear_layout(self) -> None:
        """Stop and remove all current tiles."""
        for tile in self.tiles:
            tile.stop()
            tile.deleteLater()
        self.tiles.clear()
    
    def create_random_layout(self) -> None:
        """Generate and apply random layout of video tiles."""
        self.clear_layout()
        
        # Determine number of tiles (between min and max)
        num_tiles = min(len(self.streams), random.randint(self.min_tiles, self.max_tiles))
        
        # Get window dimensions
        screen_width = self.width()
        screen_height = self.height()
        
        logger.debug(f"Creating new layout with {num_tiles} tiles")
        
        # Create tiles with random positions and sizes
        for i in range(num_tiles):
            # Create new tile
            tile = StreamTile(self.central_widget)
            tile.error_signal.connect(lambda msg, t=tile: self.handle_tile_error(t, msg))
            
            # Generate random size
            # Ensure tiles are at least 20% and at most 60% of screen dimensions
            width = random.randint(int(screen_width * 0.2), int(screen_width * 0.6))
            height = random.randint(int(screen_height * 0.2), int(screen_height * 0.6))
            
            # Generate random position (ensuring tile is fully visible)
            x = random.randint(0, screen_width - width)
            y = random.randint(0, screen_height - height)
            
            # Set geometry
            tile.setGeometry(x, y, width, height)
            
            # Start stream
            stream_url = random.choice(self.streams)
            tile.set_stream(stream_url)
            
            # Add to tracked tiles
            self.tiles.append(tile)
            tile.show()
        
        self.show_status(f"New layout: {num_tiles} tiles")
    
    def rotate_streams(self) -> None:
        """Change streams without changing layout."""
        logger.debug("Rotating streams")
        
        # Select random streams for each tile
        stream_selection = random.sample(
            self.streams, 
            min(len(self.streams), len(self.tiles))
        )
        
        # Apply new streams to tiles
        for i, tile in enumerate(self.tiles):
            tile.set_stream(stream_selection[i])
        
        self.show_status("Streams rotated")
    
    def handle_tile_error(self, tile: StreamTile, error: str) -> None:
        """
        Handle stream playback errors.
        
        Args:
            tile: The tile with the error
            error: Error message
        """
        logger.warning(f"Tile error: {error}")
        
        # Try to recover by setting a different stream
        if self.streams:
            tile.set_stream(random.choice(self.streams))
    
    def show_status(self, message: str, duration: int = 3000) -> None:
        """
        Show status message overlay.
        
        Args:
            message: Status message
            duration: Message display duration in milliseconds
        """
        self.status_label.setText(message)
        self.status_label.adjustSize()
        
        # Position at bottom center
        label_x = (self.width() - self.status_label.width()) // 2
        label_y = self.height() - self.status_label.height() - 50
        self.status_label.move(label_x, label_y)
        
        self.status_label.show()
        self.status_timer.start(duration)
    
    def keyPressEvent(self, event) -> None:
        """
        Handle keyboard input.
        
        Args:
            event: Key event
        """
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            self.create_random_layout()
            self.show_status("Layout changed (Space)")
        elif event.key() == Qt.Key_R:
            self.rotate_streams()
            self.show_status("Streams rotated (R)")
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            # Add more tiles
            self.min_tiles += 1
            self.max_tiles += 1
            self.create_random_layout()
            self.show_status(f"Increased tiles: {self.min_tiles}-{self.max_tiles}")
        elif event.key() == Qt.Key_Minus:
            # Reduce tiles (minimum 1)
            if self.min_tiles > 1:
                self.min_tiles -= 1
            if self.max_tiles > self.min_tiles:
                self.max_tiles -= 1
            self.create_random_layout()
            self.show_status(f"Decreased tiles: {self.min_tiles}-{self.max_tiles}")
    
    def closeEvent(self, event) -> None:
        """
        Clean up on window close.
        
        Args:
            event: Close event
        """
        self.layout_timer.stop()
        self.stream_timer.stop()
        self.clear_layout()
        super().closeEvent(event)

def main() -> None:
    """Main function to run the video wall."""
    # Configure argument parser
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: ./dynamic_video_wall.py --input streams.txt --layout-interval 60 --stream-interval 30"
    )
    
    parser.add_argument(
        '--input', type=str,
        help='Path to file containing stream URLs (default: streams.txt)'
    )
    
    parser.add_argument(
        '--layout-interval', type=int, default=30,
        help='Seconds between layout changes (default: 30)'
    )
    
    parser.add_argument(
        '--stream-interval', type=int, default=45,
        help='Seconds between stream rotations (default: 45)'
    )
    
    parser.add_argument(
        '--min-tiles', type=int, default=3,
        help='Minimum number of video tiles (default: 3)'
    )
    
    parser.add_argument(
        '--max-tiles', type=int, default=8,
        help='Maximum number of video tiles (default: 8)'
    )
    
    parser.add_argument(
        '--windowed', action='store_true',
        help='Run in windowed mode instead of fullscreen'
    )
    
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine input file
    if args.input:
        stream_file = args.input
    else:
        # Try to use streams.txt by default
        default_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streams.txt")
        
        if os.path.exists(default_file):
            stream_file = default_file
        else:
            # Prompt for file selection
            stream_file = get_file_path(
                "Select Stream URLs File",
                [("Text Files", "*.txt"), ("All Files", "*.*")]
            )
    
    if not stream_file:
        show_message("Canceled", "No stream file selected", "warning")
        sys.exit(1)
    
    if not os.path.exists(stream_file):
        show_message(
            "File Not Found", 
            f"Stream file not found: {stream_file}",
            "error"
        )
        sys.exit(1)
    
    # Create and run application
    try:
        app = QApplication(sys.argv)
        
        # Enable Qt hardware acceleration
        app.setAttribute(Qt.AA_UseOpenGLES, True)
        app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
        app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
        
        window = DynamicVideoWall(
            stream_file=stream_file,
            layout_interval=args.layout_interval,
            stream_interval=args.stream_interval,
            min_tiles=args.min_tiles,
            max_tiles=args.max_tiles,
            fullscreen=not args.windowed
        )
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        show_message(
            "Error",
            f"An error occurred: {str(e)}",
            "error"
        )

if __name__ == "__main__":
    main()