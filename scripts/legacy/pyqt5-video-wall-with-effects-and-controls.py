#!/usr/bin/env python3
"""
Video Wall Display System
------------------------
Author: Jason Paul Michaels
Date: March 3, 2025
Version: 1.1.0

Description:
    A PyQt5-based video wall system that creates a dynamic multi-screen video display.
    Supports multiple video sources, dynamic effects, and screen management.

Features:
    - Multi-screen support
    - Dynamic video effects (scale, rotate, crop, frame rate)
    - Randomized video selection
    - Fullscreen and windowed modes
    - Control interface for randomness and playback
    - M3U8 playlist support

Requirements:
    - Python 3.6+
    - PyQt5
    - PyQt5-multimediawidgets
    - Qt5

Usage:
    python video-wall-basic.py

Controls:
    - Space: Toggle pause
    - Left/Right arrows: Change videos
    - Slider: Adjust randomness level
"""

import os
import sys
import random
import time
import logging
import threading
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Tuple, Optional, Any

# Try to import PyQt5, provide helpful message if not available
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, 
        QSizePolicy, QFileDialog, QPushButton, QSlider, QLabel,
        QHBoxLayout, QMessageBox
    )
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    from PyQt5.QtCore import QUrl, Qt, QEvent, QSize, QPoint, QTimer
    from PyQt5.QtGui import QScreen, QIcon
except ImportError:
    print("Error: This script requires PyQt5.")
    print("Install with: pip install PyQt5 PyQt5-multimediawidgets")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("video-wall")

# Video extensions for file filtering
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.m4v', '.mpg', '.mpeg', '.wmv', '.m3u8')

def parse_m3u8(m3u8_path: str) -> str:
    """
    Parse an M3U8 playlist file and return the first valid URL.
    
    Args:
        m3u8_path: Path to the M3U8 file
        
    Returns:
        First valid URL found in the playlist or the original path if none found
    """
    try:
        if not os.path.exists(m3u8_path):
            logger.error(f"M3U8 file not found: {m3u8_path}")
            return m3u8_path
        
        with open(m3u8_path, 'r') as f:
            content = f.readlines()
        
        # Find the first line that looks like a URL
        for line in content:
            line = line.strip()
            if line and not line.startswith('#') and ('://' in line or line.endswith('.ts')):
                logger.info(f"Found URL in M3U8: {line}")
                return line
        
        logger.warning(f"No valid URLs found in M3U8 file: {m3u8_path}")
        return m3u8_path
    
    except Exception as e:
        logger.error(f"Error parsing M3U8 file {m3u8_path}: {e}")
        return m3u8_path

def select_directories() -> List[str]:
    """
    Display a dialog to select multiple video directories.
    
    Returns:
        List of selected directory paths
    """
    root = tk.Tk()
    root.withdraw()
    
    # First ask how many directories to select
    msg = "How would you like to select videos?\n" \
          "1. Select multiple directories\n" \
          "2. Select individual video files"
    
    selection_type = tk.simpledialog.askinteger(
        "Selection Method", 
        msg,
        minvalue=1, maxvalue=2
    )
    
    if not selection_type:
        return []
    
    directories = []
    
    if selection_type == 1:
        # Select directories
        done = False
        while not done:
            directory = filedialog.askdirectory(
                title="Select a directory containing videos"
            )
            
            if directory:
                directories.append(directory)
                done = not tk.messagebox.askyesno(
                    "Add More", 
                    f"Added: {directory}\nDo you want to add another directory?"
                )
            else:
                done = True
    else:
        # Select individual files
        files = filedialog.askopenfilenames(
            title="Select video files",
            filetypes=[
                ("Video files", " ".join(f"*{ext}" for ext in VIDEO_EXTENSIONS)),
                ("All files", "*.*")
            ]
        )
        
        if files:
            # Group files by directory for processing
            file_dirs = set(os.path.dirname(f) for f in files)
            directories = list(file_dirs)
    
    root.destroy()
    return directories

def get_all_videos(directory: str) -> List[str]:
    """
    Get all video files in a directory.
    
    Args:
        directory: Directory to search for videos
        
    Returns:
        List of video file paths
    """
    videos = []
    
    if not os.path.exists(directory):
        logger.error(f"Directory does not exist: {directory}")
        return videos
    
    for file in os.listdir(directory):
        if file.lower().endswith(VIDEO_EXTENSIONS):
            videos.append(os.path.join(directory, file))
    
    return videos

class DynamicEffectsManager:
    """Manages visual effects for video widgets."""
    
    def __init__(self, video_widgets: List[QVideoWidget], effect_intervals: List[int]):
        """
        Initialize the effects manager.
        
        Args:
            video_widgets: List of video widgets to apply effects to
            effect_intervals: List of possible intervals between effects (seconds)
        """
        self.video_widgets = video_widgets
        self.effect_intervals = effect_intervals
        self.effects = {
            "scale": self.apply_scale,
            "rotate": self.apply_rotate,
            "crop": self.apply_crop,
            "frame_rate": self.apply_frame_rate
        }
        self.running = True
        self.effect_timers = {}

    def start_effects(self):
        """Start applying effects to video widgets."""
        self.running = True
        for widget in self.video_widgets:
            # Create a separate thread for each widget's effects
            thread = threading.Thread(
                target=self._effect_loop,
                args=(widget,),
                daemon=True
            )
            thread.start()

    def stop_effects(self):
        """Stop all effects."""
        self.running = False
        # Cancel all pending timers
        for timer_id in self.effect_timers.values():
            QTimer.singleShot(0, timer_id.stop)
        self.effect_timers.clear()

    def _effect_loop(self, widget: QVideoWidget):
        """
        Apply effects in a loop for a specific widget.
        
        Args:
            widget: Video widget to apply effects to
        """
        while self.running:
            try:
                # Apply a random effect
                self.apply_random_effect(widget)
                
                # Sleep for a random interval
                interval = random.choice(self.effect_intervals)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in effect loop: {e}")
                time.sleep(1)  # Avoid tight loop if errors occur

    def apply_random_effect(self, widget: QVideoWidget):
        """
        Apply a random effect to a widget.
        
        Args:
            widget: Video widget to apply the effect to
        """
        if not self.running:
            return
            
        effect = random.choice(list(self.effects.keys()))
        try:
            self.effects[effect](widget)
        except Exception as e:
            logger.error(f"Error applying effect '{effect}': {e}")

    def apply_scale(self, widget: QVideoWidget):
        """
        Adjust scale randomly.
        
        Args:
            widget: Video widget to scale
        """
        try:
            scale_factor = random.uniform(0.8, 1.2)
            current_size = widget.size()
            new_width = int(current_size.width() * scale_factor)
            new_height = int(current_size.height() * scale_factor)
            new_size = QSize(new_width, new_height)
            
            # Apply on UI thread using QTimer
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: widget.resize(new_size))
            timer.start(0)
            
            # Store timer reference to prevent garbage collection
            self.effect_timers[id(widget)] = timer
        except Exception as e:
            logger.error(f"Error in apply_scale: {e}")

    def apply_rotate(self, widget: QVideoWidget):
        """
        Rotate widget randomly.
        
        Args:
            widget: Video widget to rotate
        """
        try:
            angle = random.randint(-15, 15)  # Less extreme rotation
            
            # Create a timer to apply the rotation on the UI thread
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: widget.setProperty("rotation", angle))
            timer.start(0)
            
            # Store timer reference to prevent garbage collection
            self.effect_timers[id(widget)] = timer
        except Exception as e:
            logger.error(f"Error in apply_rotate: {e}")

    def apply_crop(self, widget: QVideoWidget):
        """
        Crop widget randomly.
        
        Args:
            widget: Video widget to crop
        """
        try:
            original_size = widget.size()
            crop_factor = random.uniform(0.8, 0.95)  # Less extreme cropping
            new_width = int(original_size.width() * crop_factor)
            new_height = int(original_size.height() * crop_factor)
            
            x_offset = random.randint(0, int(original_size.width() - new_width))
            y_offset = random.randint(0, int(original_size.height() - new_height))
            
            # Apply on UI thread using QTimer
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(
                lambda: widget.setGeometry(x_offset, y_offset, new_width, new_height)
            )
            timer.start(0)
            
            # Store timer reference to prevent garbage collection
            self.effect_timers[id(widget)] = timer
        except Exception as e:
            logger.error(f"Error in apply_crop: {e}")

    def apply_frame_rate(self, widget: QVideoWidget):
        """
        Change frame rate randomly.
        
        Args:
            widget: Video widget to adjust frame rate for
        """
        try:
            player = None
            
            # Look for the player in the widget's parent
            for p in self.get_players(widget):
                if isinstance(p, QMediaPlayer):
                    player = p
                    break
            
            if player:
                new_rate = random.uniform(0.7, 1.3)  # Less extreme speed changes
                
                # Apply on UI thread using QTimer
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: player.setPlaybackRate(new_rate))
                timer.start(0)
                
                # Store timer reference to prevent garbage collection
                self.effect_timers[id(widget)] = timer
        except Exception as e:
            logger.error(f"Error in apply_frame_rate: {e}")
            
    def get_players(self, widget: QWidget) -> List[Any]:
        """
        Find all potential QMediaPlayer objects associated with a widget.
        
        Args:
            widget: Widget to search for associated players
            
        Returns:
            List of found player objects
        """
        players = []
        
        # Check if the parent has a 'players' attribute
        if hasattr(widget.parent(), 'players'):
            players.extend(widget.parent().players)
        
        # Check if the widget itself is a player
        if isinstance(widget, QMediaPlayer):
            players.append(widget)
            
        return players

class VideoWall(QMainWindow):
    """Main video wall application window."""
    
    def __init__(self, videos: List[str], screen: QScreen, fullscreen: bool = True):
        """
        Initialize the video wall.
        
        Args:
            videos: List of video file paths
            screen: Screen to display the video wall on
            fullscreen: Whether to show in fullscreen mode
        """
        super().__init__()
        self.setWindowTitle("Video Wall")
        self.setGeometry(screen.geometry())

        if fullscreen:
            self.showFullScreen()
        else:
            self.show()

        # Set up main widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Initialize video-related variables
        self.all_videos = videos
        self.num_videos = min(6, len(videos))  # Ensure we don't exceed available videos
        self.players = []
        self.current_videos = []
        self.paused = False
        self.randomness_level = 50

        # Create splitters for layout
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)  # Thin borders between video panels

        upper_splitter = QSplitter(Qt.Horizontal)
        upper_splitter.setHandleWidth(1)
        lower_splitter = QSplitter(Qt.Horizontal)
        lower_splitter.setHandleWidth(1)
        splitter.addWidget(upper_splitter)
        splitter.addWidget(lower_splitter)

        layout.addWidget(splitter)

        # Create video widgets and players
        self.video_widgets = []
        for i in range(self.num_videos):
            video_widget = QVideoWidget(self)
            video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            video_widget.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)

            player = QMediaPlayer(video_widget)
            player.setVideoOutput(video_widget)
            player.setMuted(True)
            
            # Enable hardware acceleration hints
            video_widget.setAttribute(Qt.WA_AccelChildrenInheritClip)
            video_widget.setAttribute(Qt.WA_NativeWindow)
            self.players.append(player)
            self.video_widgets.append(video_widget)

            # Add to the appropriate splitter
            if i < 3:
                upper_splitter.addWidget(video_widget)
            else:
                lower_splitter.addWidget(video_widget)

        # Create control bar
        control_bar = QWidget(self)
        control_layout = QHBoxLayout(control_bar)
        
        # Randomness control
        random_label = QLabel("Random Level:", control_bar)
        control_layout.addWidget(random_label)
        
        self.randomness_slider = QSlider(Qt.Horizontal, control_bar)
        self.randomness_slider.setMinimum(0)
        self.randomness_slider.setMaximum(100)
        self.randomness_slider.setValue(self.randomness_level)
        self.randomness_slider.valueChanged.connect(self.update_randomness)
        self.randomness_slider.setMinimumWidth(100)
        control_layout.addWidget(self.randomness_slider)
        
        # Pause button
        self.pause_button = QPushButton("Pause", control_bar)
        self.pause_button.clicked.connect(self.toggle_pause)
        control_layout.addWidget(self.pause_button)
        
        # Change videos button
        self.change_button = QPushButton("Change Videos", control_bar)
        self.change_button.clicked.connect(self.set_random_videos)
        control_layout.addWidget(self.change_button)
        
        # Add controls to main layout
        layout.addWidget(control_bar)

        # Start playing videos
        self.set_random_videos()

        # Initialize the effects manager
        self.effects_manager = DynamicEffectsManager(
            self.video_widgets, 
            [5, 10, 15]  # Effect intervals in seconds
        )
        self.effects_manager.start_effects()
        
        # Connect close event
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def set_random_videos(self):
        """Set random videos on all players."""
        try:
            # Adjust sample size based on randomness level
            sample_size = max(1, int(len(self.all_videos) * (self.randomness_level / 100)))
            sample_pool = random.sample(
                self.all_videos, 
                min(sample_size, len(self.all_videos))
            )
            
            # Select from the sample pool
            self.current_videos = random.sample(
                sample_pool,
                min(self.num_videos, len(sample_pool))
            )
            
            # Loop through each player and set its media
            for i, (player, video) in enumerate(zip(self.players, self.current_videos)):
                logger.info(f"Setting video {i+1}: {os.path.basename(video)}")
                
                # Process M3U8 files
                if video.lower().endswith(".m3u8"):
                    video_url = parse_m3u8(video)
                    player.setMedia(QMediaContent(QUrl(video_url)))
                else:
                    player.setMedia(QMediaContent(QUrl.fromLocalFile(video)))
                
                # Connect loop handler
                player.mediaStatusChanged.connect(
                    lambda state, p=player: self.handle_loop(state, p)
                )
                
                # Start playing
                player.play()
        except Exception as e:
            logger.error(f"Error setting random videos: {e}")

    def handle_loop(self, state: QMediaPlayer.MediaStatus, player: QMediaPlayer):
        """
        Handle looping of videos when they end.
        
        Args:
            state: Media player state
            player: The media player that triggered the state change
        """
        if state == QMediaPlayer.EndOfMedia:
            player.setPosition(0)
            player.play()

    def keyPressEvent(self, event):
        """
        Handle keyboard events.
        
        Args:
            event: Key press event
        """
        if event.key() == Qt.Key_Space:
            self.toggle_pause()
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
            self.set_random_videos()
        elif event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)

    def toggle_pause(self):
        """Toggle pause/play for all videos."""
        self.paused = not self.paused
        
        for player in self.players:
            if self.paused:
                player.pause()
            else:
                player.play()
        
        # Update button text
        self.pause_button.setText("Play" if self.paused else "Pause")

    def update_randomness(self, value: int):
        """Update randomness level for video selection."""
        self.randomness_level = value
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop effect threads
        if hasattr(self, 'effects_manager'):
            self.effects_manager.stop_effects()
        
        # Stop all players
        for player in self.players:
            player.stop()
        
        # Accept the close event
        super().closeEvent(event)

def main():
    """Main program entry point."""
    try:
        # Select video directories
        video_dirs = select_directories()
        if not video_dirs:
            logger.info("No directories selected, exiting.")
            return

        # Get all videos from selected directories
        videos = []
        for directory in video_dirs:
            dir_videos = get_all_videos(directory)
            videos.extend(dir_videos)
            logger.info(f"Found {len(dir_videos)} videos in {directory}")

        # Check if we found enough videos
        min_videos = 6
        if len(videos) < min_videos:
            tk.Tk().withdraw()
            tk.messagebox.showerror(
                "Not Enough Videos",
                f"Not enough videos in the selected directories.\n"
                f"Found {len(videos)}, need at least {min_videos}."
            )
            return

        # Initialize QApplication with hardware acceleration
        app = QApplication(sys.argv)
        
        # Enable hardware acceleration
        app.setAttribute(Qt.AA_UseOpenGLES, True)
        app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
        app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
        
        # Get available screens
        screens = app.screens()
        num_screens = len(screens)

        if num_screens == 0:
            logger.error("No displays connected.")
            return

        # Create video wall for each screen
        for i in range(num_screens):
            # Make the first one not fullscreen for easier control
            fullscreen = i != 0
            
            # Create video wall for this screen
            video_wall = VideoWall(videos, screens[i], fullscreen)
            
            # Resize and position non-fullscreen window
            if not fullscreen:
                video_wall.resize(1280, 720)
                video_wall.move(100, 100)
            
            # Show the window
            video_wall.show()

        # Start the application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        
        # Show error message
        try:
            tk.Tk().withdraw()
            tk.messagebox.showerror(
                "Error",
                f"An error occurred: {str(e)}"
            )
        except:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()