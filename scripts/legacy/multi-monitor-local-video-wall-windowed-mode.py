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
                # Skip hidden files (starting with ._) and other metadata files
                if file.startswith('._') or file.startswith('.'):
                    continue
                    
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    full_path = os.path.join(root, file)
                    # Verify file exists and is accessible
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                        video_files.append(full_path)
        
        print(f"Found {len(video_files)} valid local video files in {folder_path} and subdirectories.")
        return video_files
    except Exception as e:
        print(f"Error scanning for video files: {e}")
        return []

# --- Local Video Selection Dialog ---
class LocalVideoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Wall Configuration")
        self.setMinimumWidth(500)
        
        self.layout = QVBoxLayout()
        
        # Add a title label with larger font
        title_label = QLabel("Video Wall Configuration")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
        
        # Stream Configuration Section
        stream_group = QWidget()
        stream_layout = QVBoxLayout(stream_group)
        
        stream_header = QLabel("Stream Settings")
        stream_header.setFont(QFont("Arial", 12, QFont.Bold))
        stream_layout.addWidget(stream_header)
        
        # Stream testing options
        stream_options_label = QLabel("Live Stream Handling:")
        stream_layout.addWidget(stream_options_label)
        
        # Skip stream testing checkbox
        self.skip_stream_testing = QCheckBox("Skip Stream Testing (Assume All Streams are Valid)")
        self.skip_stream_testing.setChecked(True)  # Default to skipping tests
        self.skip_stream_testing.setToolTip("Enable this to skip stream validation and assume all streams are valid. Recommended for better startup.")
        stream_layout.addWidget(self.skip_stream_testing)
        
        # Warning label
        warning_label = QLabel("Note: When streams go offline, they'll automatically fall back to local videos.")
        warning_label.setStyleSheet("color: #AA5500;")
        warning_label.setWordWrap(True)
        stream_layout.addWidget(warning_label)
        
        # Local Video Configuration Section
        local_group = QWidget()
        local_layout = QVBoxLayout(local_group)
        
        local_header = QLabel("Local Video Settings")
        local_header.setFont(QFont("Arial", 12, QFont.Bold))
        local_layout.addWidget(local_header)
        
        # Add description
        desc_label = QLabel("Would you like to include local videos in the playback? "
                           "Local videos will be used as fallbacks when streams are offline.")
        desc_label.setWordWrap(True)
        local_layout.addWidget(desc_label)
        
        # Checkbox for enabling local videos
        self.enable_local_videos = QCheckBox("Enable Local Video Fallback")
        self.enable_local_videos.setChecked(True)
        local_layout.addWidget(self.enable_local_videos)
        
        # Button to select folder
        self.select_folder_button = QPushButton("Select Video Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        local_layout.addWidget(self.select_folder_button)
        
        # Status label
        self.status_label = QLabel("No folder selected")
        local_layout.addWidget(self.status_label)
        
        # Add sections to main layout
        self.layout.addWidget(stream_group)
        self.layout.addWidget(local_group)
        
        # Buttons
        self.continue_button = QPushButton("Start Video Wall")
        self.continue_button.clicked.connect(self.accept)
        self.layout.addWidget(self.continue_button)
        
        self.setLayout(self.layout)
        
        self.folder_path = None
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Video Files")
        if folder:
            self.folder_path = folder
            self.status_label.setText(f"Selected: {folder}")
            
    def get_results(self):
        return {
            "use_local_videos": self.enable_local_videos.isChecked(),
            "folder_path": self.folder_path,
            "skip_stream_testing": self.skip_stream_testing.isChecked()
        }

# --- Enhanced Tile Animator Class ---
class TileAnimator(QObject):
    def __init__(self, tiles, layout, grid_rows, grid_cols, parent_window, parent=None):
        super().__init__(parent)
        self.tiles = tiles
        self.layout = layout
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.parent_window = parent_window
        self.animations = {}
        self.current_layout = [(1, 1)] * len(tiles)
        self.full_screen_tile = None
        self.last_transitions = []
        self.upcoming_transition_type = 'resize'  # Initial transition type

        self.random_timer = QTimer(self)
        self.random_timer.timeout.connect(self.trigger_random_action)
        print(f"Animator initialized for {parent_window.screen.name()}. Starting random interval timer.")
        self.start_random_timer()

    def get_tile_position(self, tile):
        """Attempts to find the grid row and column of a given tile widget."""
        try:
            if tile and self.layout and tile.parentWidget():
                idx = self.layout.indexOf(tile)
                if idx != -1:
                    row, col, _, _ = self.layout.getItemPosition(idx)
                    return row, col
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error getting tile position for {getattr(tile, 'tile_id', 'N/A')}: {e}")
            return None
        
    def trigger_random_action(self):
        """Executes transitions based on pre-selected transition type for variety."""
        # If we're in full-screen mode, always revert first
        if self.full_screen_tile:
            print(f"Animator ({self.parent_window.screen.name()}): Reverting from full-screen mode")
            self.revert_from_full_screen()
        else:
            # Use the pre-selected transition type from previous timer
            transition_type = getattr(self, 'upcoming_transition_type', 'resize')
            
            # Execute the selected transition
            if transition_type == 'swap':
                print(f"Animator ({self.parent_window.screen.name()}): Triggering Tile Swap")
                self.trigger_random_swap()
            elif transition_type == 'full_screen':
                print(f"Animator ({self.parent_window.screen.name()}): Triggering Full-Screen Takeover")
                self.trigger_full_screen_takeover()
            elif transition_type == 'resize':
                print(f"Animator ({self.parent_window.screen.name()}): Triggering Tile Resize")
                self.trigger_random_resize()
            elif transition_type == 'refresh':
                print(f"Animator ({self.parent_window.screen.name()}): Triggering Full Video Refresh")
                if self.parent_window:
                    self.parent_window.refresh_all_tile_videos()

        # Start the next timer with a new transition type
        self.start_random_timer()

    def trigger_random_swap(self):
        """Selects two valid random tiles from the grid and initiates an animated swap."""
        if self.full_screen_tile:
            return
        valid_tiles = [t for t in self.tiles if t and t.parentWidget()]
        if len(valid_tiles) < 2:
            print(f"Animator ({self.parent_window.screen.name()}): Not enough valid tiles ({len(valid_tiles)}) to perform swap.")
            return
        try:
            tile1, tile2 = random.sample(valid_tiles, 2)
        except ValueError:
            print(f"Animator ({self.parent_window.screen.name()}): Error sampling tiles for swap.")
            return

        pos1 = self.get_tile_position(tile1)
        pos2 = self.get_tile_position(tile2)

        if pos1 and pos2:
            row1, col1 = pos1
            row2, col2 = pos2
            print(f"Animator ({self.parent_window.screen.name()}): Swapping Tile {tile1.tile_id} ({row1},{col1}) with Tile {tile2.tile_id} ({row2},{col2})")
            self.animate_swap(tile1, tile2, row1, col1, row2, col2)
        else:
            print(f"Animator ({self.parent_window.screen.name()}): Failed to get positions for swap (Pos1: {pos1}, Pos2: {pos2}). Aborting swap.")

    def start_random_timer(self):
        """Sets the random timer to trigger at much longer intervals for an extremely relaxed pace."""
        # More frequent intervals - 30-90 seconds for readily visible transitions
        possible_intervals_ms = [30000, 45000, 60000, 90000]
        interval_ms = random.choice(possible_intervals_ms)
        print(f"Animator ({self.parent_window.screen.name()}): Next random action in {interval_ms / 1000} seconds.")
        
        # Save last few transitions to prevent getting stuck in a pattern
        if not hasattr(self, 'last_transitions'):
            self.last_transitions = []
            
        # Store this transition type to avoid repetition
        self.last_transitions.append(self.upcoming_transition_type)
        if len(self.last_transitions) > 3:
            self.last_transitions.pop(0)
            
        # Choose the next transition type, avoiding repeating the same one too often
        self.choose_next_transition()
        
        # Make sure the animation timer is active
        if self.random_timer.isActive():
            self.random_timer.stop()
            
        # Add a debug message to ensure timer is being set up correctly
        print(f"Setting timer for next transition '{self.upcoming_transition_type}' in {interval_ms/1000} seconds")
        self.random_timer.start(interval_ms)
    
    def choose_next_transition(self):
        """Choose the next transition type, with updated weights to ensure layout changes happen."""
        # Define transition types with their probabilities (must sum to 1.0)
        # Heavily favor resize operations to ensure layouts change
        transition_weights = {
            'swap': 0.05,        # 5% chance - simple tile swap (reduced further)
            'resize': 0.85,      # 85% chance - reorganize tiles in new layout (increased dramatically)
            'full_screen': 0.10, # 10% chance - full-screen takeover
            'refresh': 0.0       # 0% chance - refresh videos (disabled)
        }
        
        # Build a weighted list of transitions, excluding recent ones
        available_transitions = {}
        
        # If we have a history of transitions, lower the weight of recent ones
        if hasattr(self, 'last_transitions') and self.last_transitions:
            # Copy weights but reduce probability of recent transitions by 80%
            for t_type, weight in transition_weights.items():
                if t_type in self.last_transitions:
                    available_transitions[t_type] = weight * 0.2  # 80% reduction
                else:
                    available_transitions[t_type] = weight
        else:
            # No history yet, use original weights
            available_transitions = transition_weights.copy()
            
        # Normalize weights to ensure they sum to 1.0
        total_weight = sum(available_transitions.values())
        normalized_transitions = {t: w/total_weight for t, w in available_transitions.items()}
        
        # Select transition based on weighted probability
        r = random.random()
        cumulative = 0
        for t_type, weight in normalized_transitions.items():
            cumulative += weight
            if r <= cumulative:
                self.upcoming_transition_type = t_type
                break
        
        print(f"Next transition will be: {self.upcoming_transition_type}")

    def animate_swap(self, tile1, tile2, row1, col1, row2, col2):
        """Handles the visual animation of swapping two tiles."""
        target_rect1 = self.calculate_target_rect(row2, col2)
        target_rect2 = self.calculate_target_rect(row1, col1)

        if not tile1 or not tile1.parentWidget() or not tile2 or not tile2.parentWidget():
             print("Warning: One or both tiles became invalid before initiating swap animation.")
             return

        geom1 = tile1.geometry()
        geom2 = tile2.geometry()

        self.layout.removeWidget(tile1)
        self.layout.removeWidget(tile2)

        self.layout.addWidget(tile1, row2, col2, 1, 1)
        self.layout.addWidget(tile2, row1, col1, 1, 1)

        if tile1 and tile1.parentWidget(): tile1.setGeometry(geom1)
        if tile2 and tile2.parentWidget(): tile2.setGeometry(geom2)

        self.start_animation(tile1, geom1, target_rect1)
        self.start_animation(tile2, geom2, target_rect2)

    def start_animation(self, tile, start_geom, end_rect):
        """Creates and starts a geometry animation for a tile with dramatically slower transitions."""
        if not tile or not tile.parentWidget():
             print(f"Warning: Attempted to animate invalid tile {getattr(tile, 'tile_id', 'N/A')}")
             return

        if tile in self.animations:
            self.animations[tile].stop()

        # Create the geometry animation
        animation = QPropertyAnimation(tile, b"geometry", self)
        
        # Set a more moderate duration for animations
        animation.setDuration(8000)  # 8 seconds for smooth transitions
        animation.setStartValue(start_geom)
        animation.setEndValue(end_rect)
        
        # Choose the gentlest easing curves for slow, relaxed movement
        easing_curves = [
            QEasingCurve.InOutSine,     # Very gentle sine wave motion
            QEasingCurve.OutCubic,      # Smooth deceleration - less bouncy
            QEasingCurve.InOutQuad      # Smooth acceleration/deceleration
        ]
        animation.setEasingCurve(random.choice(easing_curves))

        animation.finished.connect(lambda t=tile: self.animation_finished(t))

        animation.start(QPropertyAnimation.DeleteWhenStopped)

        self.animations[tile] = animation
        
        # Moderate fade effect for graceful transitions
        tile.setStyleSheet("background-color: rgba(0, 0, 0, 0.85);")  # Very slight fade
        QTimer.singleShot(4000, lambda: tile.setStyleSheet("background-color: black;"))  # 4 second fade

    def animation_finished(self, tile):
        """Callback function when an animation completes."""
        tile_id = getattr(tile, 'tile_id', 'N/A')
        if tile in self.animations:
            del self.animations[tile]

    def calculate_target_rect(self, row, col, row_span=1, col_span=1):
        """Calculates the absolute screen rectangle for a given grid cell with spans."""
        grid_widget = self.layout.parentWidget()
        if not grid_widget: return QRect()
        parent_width = grid_widget.width()
        parent_height = grid_widget.height()
        if self.grid_cols <= 0 or self.grid_rows <= 0: return QRect()

        cell_width = parent_width / self.grid_cols
        cell_height = parent_height / self.grid_rows
        target_x = col * cell_width
        target_y = row * cell_height
        target_width = cell_width * col_span
        target_height = cell_height * row_span

        return QRect(int(target_x), int(target_y), int(target_width), int(target_height))

    def trigger_random_resize(self):
        """Randomly resizes tiles with enhanced layout variety."""
        print(f"RESIZE: Starting tile resize operation on {self.parent_window.screen.name()}")
        if self.full_screen_tile:
            print(f"RESIZE: Aborting - full screen mode active")
            return

        # Log information about current tiles
        valid_tiles = [t for t in self.tiles if t and t.parentWidget()]
        print(f"RESIZE: Found {len(valid_tiles)} valid tiles out of {len(self.tiles)} total")
        
        self.parent_window.pause_all_players()

        for tile in self.tiles:
            if tile and tile.parentWidget():
                self.layout.removeWidget(tile)
                tile.hide()

        # Select a layout pattern for this resize operation
        layout_patterns = [
            'varied',        # Mix of different size tiles
            'feature',       # One dominant feature tile with smaller ones
            'columns',       # Column-based layout
            'rows',          # Row-based layout
            'grid',          # Standard grid (2x2, 3x3, etc.)
            'asymmetric'     # Asymmetric design
        ]
        pattern = random.choice(layout_patterns)
        print(f"Using '{pattern}' layout pattern")
        
        # Define more possible tile sizes based on pattern
        if pattern == 'varied':
            possible_sizes = [
                (2, 2), (1, 3), (3, 1), (1, 1), (2, 1), (1, 2)
            ]
        elif pattern == 'feature':
            possible_sizes = [
                (3, 3), (2, 2), (1, 1)  # Allow for one big feature tile
            ]
        elif pattern == 'columns':
            possible_sizes = [
                (4, 1), (3, 1), (2, 1), (1, 1)  # Vertical column layouts
            ]
        elif pattern == 'rows':
            possible_sizes = [
                (1, 4), (1, 3), (1, 2), (1, 1)  # Horizontal row layouts
            ]
        elif pattern == 'grid':
            # Pick a specific grid size for consistency
            grid_size = random.choice([(2, 2), (4, 4), (3, 2), (2, 3)])
            row_size, col_size = grid_size
            possible_sizes = [(row_size, col_size)]
        else:  # asymmetric
            possible_sizes = [
                (2, 3), (3, 2), (2, 1), (1, 2), (1, 1)
            ]

        tiles_to_place = self.tiles.copy()
        random.shuffle(tiles_to_place)
        occupied = [[False] * self.grid_cols for _ in range(self.grid_rows)]
        self.current_layout = [(1, 1)] * len(self.tiles)

        # If using 'feature' pattern, place a large feature tile first
        if pattern == 'feature' and len(tiles_to_place) > 0:
            feature_tile = tiles_to_place[0]
            feature_size = (3, 3) if self.grid_rows >= 4 and self.grid_cols >= 4 else (2, 2)
            row, col = 0, 0
            row_span, col_span = feature_size
            
            # Mark cells as occupied
            for r in range(row, row + row_span):
                for c in range(col, col + col_span):
                    if r < self.grid_rows and c < self.grid_cols:
                        occupied[r][c] = True
                        
            # Add the feature tile
            self.layout.addWidget(feature_tile, row, col, row_span, col_span)
            feature_tile.show()
            self.current_layout[self.tiles.index(feature_tile)] = (row_span, col_span)
            target_rect = self.calculate_target_rect(row, col, row_span, col_span)
            feature_tile.setGeometry(target_rect)
            print(f"Placed feature Tile {feature_tile.tile_id} at ({row},{col}) with size {row_span}x{col_span}")
            
            # Remove the feature tile from tiles to place
            tiles_to_place.pop(0)

        # Place the rest of the tiles
        tile_idx = 0
        while tile_idx < len(tiles_to_place) and tiles_to_place[tile_idx]:
            tile = tiles_to_place[tile_idx]
            placed = False
            
            # Filter possible sizes based on remaining space
            filtered_sizes = []
            for row_span, col_span in possible_sizes:
                # Check if this size can fit anywhere
                can_fit = False
                for row in range(self.grid_rows - row_span + 1):
                    for col in range(self.grid_cols - col_span + 1):
                        fits = True
                        for r in range(row, row + row_span):
                            for c in range(col, col + col_span):
                                if r >= self.grid_rows or c >= self.grid_cols or occupied[r][c]:
                                    fits = False
                                    break
                            if not fits:
                                break
                        if fits:
                            can_fit = True
                            break
                    if can_fit:
                        break
                if can_fit:
                    filtered_sizes.append((row_span, col_span))
            
            # If no sizes fit, use 1x1
            if not filtered_sizes:
                filtered_sizes = [(1, 1)]
            
            # Pick a random size from filtered options
            preferred_size = random.choice(filtered_sizes)
            
            # Try to place the tile with preferred size
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    if occupied[row][col]:
                        continue
                    
                    row_span, col_span = preferred_size
                    if row + row_span > self.grid_rows or col + col_span > self.grid_cols:
                        continue
                        
                    fits = True
                    for r in range(row, row + row_span):
                        for c in range(col, col + col_span):
                            if occupied[r][c]:
                                fits = False
                                break
                        if not fits:
                            break
                            
                    if fits:
                        # Mark cells as occupied
                        for r in range(row, row + row_span):
                            for c in range(col, col + col_span):
                                occupied[r][c] = True
                                
                        # Add the tile with animated transition
                        self.layout.addWidget(tile, row, col, row_span, col_span)
                        tile.show()
                        self.current_layout[self.tiles.index(tile)] = (row_span, col_span)
                        target_rect = self.calculate_target_rect(row, col, row_span, col_span)
                        
                        # For smoother transitions, start animation from current position
                        start_rect = tile.geometry()
                        self.start_animation(tile, start_rect, target_rect)
                        
                        placed = True
                        tile_idx += 1
                        print(f"Placed Tile {tile.tile_id} at ({row},{col}) with size {row_span}x{col_span}")
                        break
                        
                if placed:
                    break
                    
            if not placed:
                # Try other sizes if preferred size didn't work
                for row in range(self.grid_rows):
                    for col in range(self.grid_cols):
                        if occupied[row][col] or placed:
                            continue
                            
                        # Try all possible sizes in order of preference
                        for row_span, col_span in filtered_sizes:
                            if row + row_span > self.grid_rows or col + col_span > self.grid_cols:
                                continue
                                
                            fits = True
                            for r in range(row, row + row_span):
                                for c in range(col, col + col_span):
                                    if r >= self.grid_rows or c >= self.grid_cols or occupied[r][c]:
                                        fits = False
                                        break
                                if not fits:
                                    break
                                    
                            if fits:
                                # Mark cells as occupied
                                for r in range(row, row + row_span):
                                    for c in range(col, col + col_span):
                                        occupied[r][c] = True
                                        
                                # Add the tile
                                self.layout.addWidget(tile, row, col, row_span, col_span)
                                tile.show()
                                self.current_layout[self.tiles.index(tile)] = (row_span, col_span)
                                target_rect = self.calculate_target_rect(row, col, row_span, col_span)
                                
                                # For smoother transitions, start animation from current position
                                start_rect = tile.geometry()
                                self.start_animation(tile, start_rect, target_rect)
                                
                                placed = True
                                tile_idx += 1
                                print(f"Placed Tile {tile.tile_id} at ({row},{col}) with size {row_span}x{col_span}")
                                break
                                
                        if placed:
                            break
                            
                    if placed:
                        break
                        
                # If still not placed, move to next tile
                if not placed:
                    tile_idx += 1

        # Fill any remaining gaps with 1x1 tiles
        remaining_tiles = [t for t in tiles_to_place[tile_idx:] if t]
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if not occupied[row][col] and remaining_tiles:
                    tile = remaining_tiles.pop(0)
                    self.layout.addWidget(tile, row, col, 1, 1)
                    tile.show()
                    self.current_layout[self.tiles.index(tile)] = (1, 1)
                    target_rect = self.calculate_target_rect(row, col, 1, 1)
                    
                    # For smoother transitions, start animation from current position
                    start_rect = tile.geometry()
                    self.start_animation(tile, start_rect, target_rect)
                    
                    occupied[row][col] = True
                    print(f"Filled gap with Tile {tile.tile_id} at ({row},{col}) with size 1x1")
                    
                    if not remaining_tiles:
                        break
                        
            if not remaining_tiles:
                break

        # Add a much longer delay before resuming players for extremely smooth transitions
        # Wait for 10 seconds to allow animations to complete gracefully
        QTimer.singleShot(10000, self.parent_window.resume_visible_players)

    def trigger_full_screen_takeover(self):
        """Selects a random tile to take over the entire screen."""
        valid_tiles = [t for t in self.tiles if t and t.parentWidget()]
        if not valid_tiles:
            print(f"Animator ({self.parent_window.screen.name()}): No valid tiles for full-screen takeover.")
            return

        self.parent_window.pause_all_players()

        for tile in self.tiles:
            if tile and tile.parentWidget():
                self.layout.removeWidget(tile)
                tile.hide()

        self.full_screen_tile = random.choice(valid_tiles)
        self.layout.addWidget(self.full_screen_tile, 0, 0, self.grid_rows, self.grid_cols)
        self.full_screen_tile.show()
        target_rect = self.calculate_target_rect(0, 0, self.grid_rows, self.grid_cols)
        self.start_animation(self.full_screen_tile, self.full_screen_tile.geometry(), target_rect)
        print(f"Tile {self.full_screen_tile.tile_id} taking over full screen on {self.parent_window.screen.name()}")

        tile_index = self.tiles.index(self.full_screen_tile)
        player = self.parent_window.players[tile_index]
        if player and player.state() != QMediaPlayer.PlayingState:
            player.play()
        self.parent_window.retry_tile_stream(tile_index)

    def revert_from_full_screen(self):
        """Reverts from full-screen mode to a normal layout."""
        if not self.full_screen_tile:
            return

        self.layout.removeWidget(self.full_screen_tile)
        self.full_screen_tile.hide()
        self.full_screen_tile = None
        self.trigger_random_resize()

    def stop_timers_and_animations(self):
        """Stops the main timer and all currently running animations."""
        print(f"Animator ({self.parent_window.screen.name()}): Stopping timer and animations...")
        self.random_timer.stop()
        for tile in list(self.animations.keys()):
             if tile in self.animations:
                 self.animations[tile].stop()
        self.animations.clear()

# --- Video Tile Widget Class (Unchanged) ---
class VideoTile(QVideoWidget):
    def __init__(self, tile_id, parent=None):
        super().__init__(parent)
        self.tile_id = tile_id
        self.setObjectName(f"Tile_{tile_id}")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAspectRatioMode(Qt.KeepAspectRatio)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: black; border: none;")

        self.status_label = QLabel("Initializing...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; font-size: 10pt; padding: 3px;")
        self.status_label.setWordWrap(True)
        self.status_label.adjustSize()
        self.status_label.show()

    def resizeEvent(self, event):
        """Handles resizing of the tile, repositions the status label."""
        super().resizeEvent(event)
        self.reposition_status_label()

    def reposition_status_label(self):
        """Calculates and sets the geometry for the status label to center it."""
        if not self.status_label.isVisible(): return
        try:
            text_width = self.status_label.fontMetrics().horizontalAdvance(self.status_label.text())
            label_width = min(self.width() * 0.9, text_width + 20 )
            label_height = self.status_label.sizeHint().height()

            x = (self.width() - label_width) / 2
            y = (self.height() - label_height) / 2

            x = max(0, x); y = max(0, y)
            label_width = min(label_width, self.width())
            label_height = min(label_height, self.height())

            self.status_label.setGeometry(int(x), int(y), int(label_width), int(label_height))
        except Exception as e:
            print(f"Error in VideoTile reposition_status_label for {self.tile_id}: {e}")

    def show_status(self, text, is_error=False, duration_ms=3000):
        """Displays a status message overlay on the video tile."""
        try:
             self.status_label.setText(text)
             if is_error:
                 self.status_label.setStyleSheet("background-color: rgba(150, 0, 0, 200); color: white; font-size: 10pt; padding: 3px;")
             else:
                 self.status_label.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; font-size: 10pt; padding: 3px;")

             self.status_label.show()
             self.reposition_status_label()

             if duration_ms > 0:
                 QTimer.singleShot(duration_ms, self.safe_hide_status)
        except Exception as e:
            print(f"Error in show_status for Tile {self.tile_id}: {e}")

    def safe_hide_status(self):
        """Safely hides the status label, checking if the widget still exists."""
        try:
             if self and self.status_label:
                 self.status_label.hide()
        except RuntimeError:
             pass
        except Exception as e:
             print(f"Error hiding status label safely for Tile {self.tile_id}: {e}")
             

# --- Global Stream Tracking ---
class GlobalVideoAssigner:
    def __init__(self, all_links, local_videos=None):
        self.all_links = all_links
        self.local_videos = local_videos or []
        self.monitor_assignments = {}
        self.reserved_videos = set()
        self._lock = None
        
        # Filter out problematic local videos
        self.filter_local_videos()
    
    def get_unique_streams_for_monitor(self, screen_name, count):
        """Gets unique streams for a specific monitor that don't overlap with other monitors."""
        current_assignments = self.monitor_assignments.get(screen_name, {})
        all_used = set()
        for assignments in self.monitor_assignments.values():
            all_used.update(assignments.values())
        
        available = [link for link in self.all_links if link not in all_used]
        needed = count
        result = []
        
        if available:
            random.shuffle(available)
            take = min(needed, len(available))
            result.extend(available[:take])
            needed -= take
        
        if needed > 0:
            other_used = all_used - set(current_assignments.values())
            if other_used:
                other_available = [link for link in self.all_links if link in other_used]
                random.shuffle(other_available)
                take = min(needed, len(other_available))
                result.extend(other_available[:take])
                needed -= take
        
        if needed > 0:
            remaining = [link for link in self.all_links if link not in result]
            if remaining:
                random.shuffle(remaining)
                result.extend(remaining[:needed])
        
        return result
    
    def filter_local_videos(self):
        """Filters the local_videos list to remove problematic files."""
        if not self.local_videos:
            return
            
        valid_videos = []
        for video_path in self.local_videos:
            # Skip macOS metadata files (._) and hidden files
            basename = os.path.basename(video_path)
            if basename.startswith('._') or basename.startswith('.'):
                continue
                
            # Skip files that don't exist or are zero size
            try:
                if not os.path.exists(video_path) or os.path.getsize(video_path) <= 0:
                    continue
            except Exception:
                continue
                
            valid_videos.append(video_path)
        
        self.local_videos = valid_videos
        print(f"GlobalVideoAssigner: Filtered to {len(self.local_videos)} valid local videos")
    
    def get_local_video(self):
        """Returns a random local video file, tracking recently used videos to avoid repetition."""
        # First ensure we have valid videos
        self.filter_local_videos()
        
        if not self.local_videos:
            return None
            
        # Initialize recently_used_videos if it doesn't exist
        if not hasattr(self, 'recently_used_videos'):
            self.recently_used_videos = []
            
        # Get available videos that weren't recently used
        available_videos = [v for v in self.local_videos if v not in self.recently_used_videos]
        
        # If all videos have been recently used, reset and use all videos
        if not available_videos:
            self.recently_used_videos = []
            available_videos = self.local_videos
            
        if not available_videos:
            print("  Warning: No valid local videos available after filtering")
            return None
            
        # Select a random video from available options
        selected_video = random.choice(available_videos)
        
        # Add to recently used and keep list at reasonable size
        self.recently_used_videos.append(selected_video)
        if len(self.recently_used_videos) > min(len(self.local_videos) // 2, 20):
            self.recently_used_videos.pop(0)  # Remove oldest entry
            
        return selected_video
    
    def update_assignments(self, screen_name, new_assignments):
        """Updates the video assignments for a monitor."""
        self.monitor_assignments[screen_name] = new_assignments

# --- Global Stream Tracker ---
global global_assigner
global_assigner = None

# --- Video Wall Main Window Class ---
class VideoWall(QMainWindow):
    GRID_ROWS = 3
    GRID_COLS = 3
    NUM_TILES = GRID_ROWS * GRID_COLS
    
    # Configure MAX_ACTIVE_PLAYERS for appropriate balance of performance and streams
    # Higher value = more concurrent streams but potentially lower performance per stream
    MAX_ACTIVE_PLAYERS = 15  # Significantly increased to show more streams (priority on streams)
    
    # Performance settings
    VIDEO_BUFFER_SIZE = 8192  # Increased buffer size for smoother playback (8MB)
    LOW_LATENCY_MODE = False  # Set to False for more buffering but smoother playback
    HARDWARE_DECODE_PRIORITY = True  # Prioritize hardware decoding over software

    def __init__(self, m3u8_links, local_videos, screen, parent=None):
        super().__init__(parent)
        self.screen = screen
        self.setWindowTitle(f"Video Wall 3x3 {screen.name()} - Ultra-Slow Relaxed Edition (v1.4.2)")
        self.setGeometry(screen.geometry())
        self.showFullScreen()
        
        # Track fullscreen state
        self.is_fullscreen = True
        # Store original geometry to restore when toggling
        self.windowed_geometry = self.geometry()
        
        # Set tooltip with usage instructions
        self.setToolTip("Double-click to toggle fullscreen/windowed mode\n"
                        "F11 or Alt+F: Toggle fullscreen\n"
                        "Escape: Exit fullscreen or quit\n"
                        "Ctrl+Q: Quit application")

        central_widget = QWidget(self)
        central_widget.setAttribute(Qt.WA_TranslucentBackground, False)
        # Back to pure black background
        central_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(central_widget)

        self.layout = QGridLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.all_m3u8_links = m3u8_links or []
        self.local_videos = local_videos or []
        
        if not self.all_m3u8_links and not self.local_videos:
             QMessageBox.critical(self, "Error", "No M3U8 links or local videos provided.")
             QTimer.singleShot(0, self.close)
             return

        self.tiles = []
        self.players = []
        self.animator = None
        self.current_assignments = {}
        self.retry_attempts = {}
        self.tried_urls = {i: set() for i in range(self.NUM_TILES)}
        self.retry_timers = {}
        self.using_local_video = {i: False for i in range(self.NUM_TILES)}

        try:
             screens_list = QApplication.screens()
             screen_index = screens_list.index(screen) if screen in screens_list else -1
        except ValueError: screen_index = -1
        tile_id_offset = self.NUM_TILES * screen_index if screen_index != -1 else random.randint(1000, 5000)

        for i in range(self.NUM_TILES):
            tile_id = tile_id_offset + i
            tile = VideoTile(tile_id, central_widget)
            # Create media player with hardware acceleration enabled
            player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            
            # Enable hardware acceleration for macOS (VideoToolbox)
            player.setProperty("videoCodecOptions", {
                "hwaccel": "videotoolbox",         # Use VideoToolbox for hardware decoding
                "hwaccel_device": "default",       # Use default GPU device
                "decode_threads": 4,               # Use 4 threads for decoding
                "thread_type": "frame",            # Thread per frame for better parallelism
                "thread_count": 4                  # Thread count for software fallback
            })
            
            # Additional flag for Metal Pipeline Shading (MPS) 
            player.setProperty("videoGPUOptions", {
                "enable_mps": True,                # Enable Metal Performance Shaders
                "metal_device": "default",         # Use default Metal device
                "zero_copy": True                  # Enable zero-copy for better performance
            })
            
            # Apply performance tuning settings
            player.setProperty("bufferSize", self.VIDEO_BUFFER_SIZE)  # Larger buffer for smoother playback
            player.setProperty("lowLatency", self.LOW_LATENCY_MODE)   # Disable low latency for smoother playback
            player.setProperty("hardwarePriority", self.HARDWARE_DECODE_PRIORITY)  # Prioritize hardware decoding
            player.setNotifyInterval(1000)  # Notify position changes every 1 second (reduced overhead)
            
            player.setVideoOutput(tile)
            player.setMuted(True)

            player.error.connect(lambda err, p=player, t=tile, idx=i: self.handle_player_error(err, p, t, idx))
            player.mediaStatusChanged.connect(lambda status, p=player, t=tile, idx=i: self.handle_media_status(status, p, t, idx))

            self.players.append(player)
            self.tiles.append(tile)

        # Create grid layout first, then initialize animator
        self.create_grid_layout()
        
        # Initialize animator with explicit reference to ensure transitions work
        self.animator = TileAnimator(self.tiles, self.layout, self.GRID_ROWS, self.GRID_COLS, self, self)
        
        # Force an initial resize transition after loading videos to ensure dynamic layouts start working
        # Timing adjusted for a balanced pace
        QTimer.singleShot(500, self.assign_initial_videos)
        # Start first transition sooner (30 seconds) to verify it's working
        QTimer.singleShot(30000, lambda: self.force_initial_transition())  # 30 seconds

        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_and_refresh_streams)
        self.check_timer.start(3600000)  # 3600 seconds (1 hour) - check streams extremely infrequently
        
        self.black_tile_timer = QTimer(self)
        self.black_tile_timer.timeout.connect(self.aggressive_black_tile_check)
        self.black_tile_timer.start(1800000)  # 1800 seconds (30 minutes) for black tile detection
        
        # Add resource monitoring
        self.resource_check_timer = QTimer(self)
        self.resource_check_timer.timeout.connect(self.check_resource_usage)
        self.resource_check_timer.start(3600000)  # 3600 seconds (1 hour) for resource usage checks

        print(f"VideoWall window created for screen: {screen.name()}")

    def create_grid_layout(self):
        """Adds the video tiles to the QGridLayout."""
        print(f"Creating {self.GRID_ROWS}x{self.GRID_COLS} grid layout for {self.screen.name()}.")
        for i, tile in enumerate(self.tiles):
            row = i // self.GRID_COLS
            col = i % self.GRID_COLS
            self.layout.addWidget(tile, row, col, 1, 1)
            
    def force_initial_transition(self):
        """Forces an initial transition to kick-start the dynamic layouts."""
        print(f"INITIAL: Forcing initial transition on {self.screen.name()} to start dynamic layouts")
        
        # Verify animator exists
        if not hasattr(self, 'animator') or not self.animator:
            print(f"INITIAL ERROR: Animator missing or invalid for {self.screen.name()}")
            # Try to recreate animator
            try:
                self.animator = TileAnimator(self.tiles, self.layout, self.GRID_ROWS, self.GRID_COLS, self, self)
                print(f"INITIAL: Created new animator for {self.screen.name()}")
            except Exception as e:
                print(f"INITIAL ERROR: Failed to create animator: {e}")
                return
                
        # Now proceed with transition
        if self.animator:
            print(f"INITIAL: Animator found, attempting resize on {self.screen.name()}")
            # First try a resize operation to ensure dynamic layouts start working
            if hasattr(self.animator, 'trigger_random_resize'):
                print(f"INITIAL: Calling trigger_random_resize on {self.screen.name()}")
                self.animator.trigger_random_resize()
            # As a backup, try any random transition
            elif hasattr(self.animator, 'trigger_random_action'):
                print(f"INITIAL: Calling trigger_random_action on {self.screen.name()}")
                self.animator.trigger_random_action()
            else:
                print(f"INITIAL ERROR: Animator missing required methods on {self.screen.name()}")

    def get_next_available_streams(self, count, exclude_urls=None):
        """Gets unique streams for this monitor using the global assigner."""
        if not self.all_m3u8_links:
            return []
            
        if global_assigner is None:
            available = self.all_m3u8_links.copy()
            if exclude_urls:
                available = [url for url in available if url not in exclude_urls]
            random.shuffle(available)
            return available[:min(count, len(available))]
        
        streams = global_assigner.get_unique_streams_for_monitor(self.screen.name(), count)
        if exclude_urls:
            streams = [url for url in streams if url not in exclude_urls]
            while len(streams) < count:
                additional = global_assigner.get_unique_streams_for_monitor(self.screen.name(), count - len(streams))
                additional = [url for url in additional if url not in exclude_urls and url not in streams]
                streams.extend(additional)
        
        return streams

    def assign_initial_videos(self):
        """Assigns the first set of videos to visible tiles upon startup."""
        print(f"Assigning initial videos for {self.screen.name()}...")
        self.refresh_all_tile_videos()

    def refresh_all_tile_videos(self):
        """Refreshes video streams for visible tiles."""
        print(f"Refreshing videos for {self.screen.name()}...")
        visible_tiles = [tile for tile in self.tiles if tile and tile.isVisible()]
        
        # Get streams for all visible tiles - prioritize streams over local videos
        # Don't limit by MAX_ACTIVE_PLAYERS here, let the resource management handle that
        streams_to_assign = self.get_next_available_streams(len(visible_tiles))
        
        print(f"  Have {len(streams_to_assign)} streams available for {len(visible_tiles)} visible tiles")
        
        # If no source material available, exit
        if not streams_to_assign and not self.local_videos:
             print(f"  Cannot refresh videos for {self.screen.name()}, no streams or local videos available.")
             return
        
        new_assignments = {}
        for i in range(self.NUM_TILES):
            self.tried_urls[i].clear()
            self.retry_attempts[i] = 0  # Reset retry counts
        
        # First assign ALL tiles to streams, let the fallback mechanisms handle issues
        stream_idx = 0
        for i, tile in enumerate(self.tiles):
            if not tile or not tile.isVisible():
                if i in self.current_assignments:
                    del self.current_assignments[i]
                continue
                
            player = self.players[i]
            if not player:
                continue
            
            # ALWAYS try to use a stream first if available
            if streams_to_assign and stream_idx < len(streams_to_assign):
                # Use stream
                url = streams_to_assign[stream_idx]
                self.tried_urls[i].add(url)
                url_short = url.split('/')[-1][:25]
                tile.show_status(f"Loading stream: {url_short}...", duration_ms=8000)
                media = QMediaContent(QUrl(url))
                self.using_local_video[i] = False
                stream_idx += 1
                
                # Set up a fail-safe to switch to local video if loading takes too long
                if self.local_videos:
                    QTimer.singleShot(1800000, lambda idx=i: self.check_loading_and_fallback(idx))  # 30 minutes
            elif self.local_videos:
                # Use local video only if no streams left
                local_video = self.get_random_local_video()
                if not local_video:
                    continue
                url = local_video
                url_short = os.path.basename(url)[:25]
                tile.show_status(f"Loading local: {url_short}...", duration_ms=8000)
                media = QMediaContent(QUrl.fromLocalFile(url))
                self.using_local_video[i] = True
            else:
                # No suitable media available
                continue
                
            player.stop()
            player.setMedia(media)
            player.play()
            new_assignments[i] = url
        
        self.current_assignments = new_assignments
        if global_assigner:
            global_assigner.update_assignments(self.screen.name(), new_assignments)
        
        # Add a delayed check after everything loads to ensure some stream are visible
        # Much longer delay for extremely relaxed pace
        QTimer.singleShot(3600000, self.ensure_some_streams_showing)  # 1 hour
        
        print(f"  Finished refreshing videos for {self.screen.name()}.")
        
    def ensure_some_streams_showing(self):
        """Checks if any streams are showing, and if not, forces some streams to show."""
        # Count streams vs local videos
        stream_count = 0
        local_count = 0
        total_visible = 0
        
        # First, check if any streams have loaded successfully on any tile
        successfully_loaded_streams = []
        
        for i, tile in enumerate(self.tiles):
            if not tile or not tile.isVisible():
                continue
                
            total_visible += 1
            player = self.players[i]
            if not player:
                continue
                
            if self.using_local_video.get(i, True):  
                local_count += 1
            else:
                stream_count += 1
                # Check if this stream is successfully playing
                if (player.mediaStatus() in [QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia] and 
                    player.state() == QMediaPlayer.PlayingState):
                    url = self.current_assignments.get(i, None)
                    if url:
                        successfully_loaded_streams.append(url)
        
        print(f"  Status check: {stream_count} streams and {local_count} local videos showing")
        print(f"  Successfully loaded streams: {len(successfully_loaded_streams)}")
        
        # Calculate target - we want 100% streams if possible (maximum streams)
        target_stream_count = total_visible  # Try to have all tiles using streams
        
        # If we have fewer streams than target, convert more tiles
        if stream_count < target_stream_count and total_visible > 0 and self.all_m3u8_links:
            num_to_convert = target_stream_count - stream_count
            print(f"  Not enough streams showing! Need {num_to_convert} more streams")
            
            # Get list of visible tiles currently using local videos
            local_tiles = [i for i, tile in enumerate(self.tiles) 
                          if tile and tile.isVisible() and self.using_local_video.get(i, False)]
            
            # Shuffle and take some to convert
            if local_tiles:
                random.shuffle(local_tiles)
                tiles_to_convert = local_tiles[:num_to_convert]
                
                # Force these tiles to use streams
                for tile_idx in tiles_to_convert:
                    self.force_stream_on_tile(tile_idx)
                    
            # Schedule another check with much longer interval
            QTimer.singleShot(7200000, self.ensure_some_streams_showing)  # 2 hours
        else:
            # Schedule periodic checks with much longer interval
            QTimer.singleShot(14400000, self.ensure_some_streams_showing)  # 4 hours
        
    def check_loading_and_fallback(self, tile_index):
        """Check if a newly assigned stream is still loading and fall back to local if needed."""
        if tile_index >= len(self.players) or tile_index >= len(self.tiles):
            return
            
        player = self.players[tile_index]
        tile = self.tiles[tile_index]
        
        if not player or not tile or not tile.isVisible() or self.using_local_video.get(tile_index, False):
            return
            
        status = player.mediaStatus()
        # Instead of falling back to local videos, try another stream first
        if status in [QMediaPlayer.NoMedia, QMediaPlayer.InvalidMedia]:
            # These are definite error states - try another stream
            print(f"  Tile {tile.tile_id}: Stream in error state {status}, trying another stream")
            self.force_stream_on_tile(tile_index)
        elif status == QMediaPlayer.LoadingMedia:
            # Always give streams more time to load
            print(f"  Tile {tile.tile_id}: Stream still loading after timeout, will give it more time")
            # Schedule another check later
            QTimer.singleShot(1800000, lambda idx=tile_index: self.check_loading_and_fallback(idx))  # 30 minutes
        elif status == QMediaPlayer.StalledMedia:
            # Stalling is an intermittent issue - give it a chance or try another stream
            self.retry_attempts[tile_index] = self.retry_attempts.get(tile_index, 0) + 1
            # If we've tried a few times, try another stream instead
            if self.retry_attempts[tile_index] > 2:
                print(f"  Tile {tile.tile_id}: Stream stalled too many times, trying another stream")
                self.force_stream_on_tile(tile_index)
            else:
                print(f"  Tile {tile.tile_id}: Stream stalled, giving it more time")
                # Schedule another check
                QTimer.singleShot(1800000, lambda idx=tile_index: self.check_loading_and_fallback(idx))  # 30 minutes
                    
    def force_stream_on_tile(self, tile_index):
        """Force a specific tile to use a stream."""
        if not self.all_m3u8_links:
            print("No streams available")
            return
            
        if tile_index >= len(self.tiles) or not self.tiles[tile_index]:
            return
            
        tile = self.tiles[tile_index]
        player = self.players[tile_index]
        
        if not tile or not player:
            return
            
        # Get current URL
        current_url = self.current_assignments.get(tile_index, None)
        
        # Clear tried_urls to try all streams again
        if tile_index in self.tried_urls:
            self.tried_urls[tile_index].clear()
            
        # Choose streams to try
        streams_to_try = self.all_m3u8_links.copy()
        # Move some known good streams to the front
        # These are streams that we know are working in other tiles
        working_streams = []
        for idx, url in self.current_assignments.items():
            if idx != tile_index and not self.using_local_video.get(idx, True):
                working_streams.append(url)
                
        # Remove current URL from working streams
        if current_url in working_streams:
            working_streams.remove(current_url)
            
        # Prioritize working streams
        for stream in working_streams:
            if stream in streams_to_try:
                streams_to_try.remove(stream)
        
        # Put working streams at the front
        streams_to_try = working_streams + streams_to_try
        
        # Find a stream that hasn't been tried on this tile
        url = None
        for stream in streams_to_try:
            if stream not in self.tried_urls.get(tile_index, set()):
                url = stream
                break
                
        # If all streams have been tried, pick any stream
        if not url and streams_to_try:
            url = streams_to_try[0]
        
        if not url:
            print(f"  No stream available for Tile {tile.tile_id}, falling back to local")
            if self.local_videos:
                self.force_local_video_fallback(tile_index)
            return
            
        url_short = url.split('/')[-1][:25]
        print(f"Forcing stream on Tile {tile.tile_id}: {url_short}")
        tile.show_status(f"Forcing stream: {url_short}...", duration_ms=8000)
        media = QMediaContent(QUrl(url))
        self.using_local_video[tile_index] = False
        self.tried_urls[tile_index].add(url)
        
        player.stop()
        player.setMedia(media)
        player.play()
        
        self.current_assignments[tile_index] = url
        self.retry_attempts[tile_index] = 0
        
        # Continue to monitor this stream - first check extremely slowly
        QTimer.singleShot(1800000, lambda idx=tile_index: self.monitor_forced_stream(idx))  # 30 minutes
        
        if global_assigner:
            global_assigner.update_assignments(self.screen.name(), self.current_assignments)
            
    def monitor_forced_stream(self, tile_index):
        """Monitors a forced stream and ensures it stays visible unless definitively broken."""
        if tile_index >= len(self.players) or tile_index >= len(self.tiles):
            return
            
        player = self.players[tile_index]
        tile = self.tiles[tile_index]
        
        if not player or not tile or not tile.isVisible():
            return
            
        # If we're already using a local video, do nothing
        if self.using_local_video.get(tile_index, True):
            return
            
        status = player.mediaStatus()
        state = player.state()
        
        if status in [QMediaPlayer.NoMedia, QMediaPlayer.InvalidMedia]:
            # Error states - try another stream
            print(f"  Monitor: Tile {tile.tile_id} stream failed with status {status}, trying another stream")
            self.force_stream_on_tile(tile_index)
        elif status == QMediaPlayer.LoadingMedia:
            # Still loading - give it more time
            print(f"  Monitor: Tile {tile.tile_id} stream still loading, continuing to wait")
            # Increment retry attempts
            self.retry_attempts[tile_index] = self.retry_attempts.get(tile_index, 0) + 1
            # If it's been loading too long, try another stream
            if self.retry_attempts[tile_index] > 3:
                print(f"  Monitor: Tile {tile.tile_id} stream loading timeout, trying another stream")
                self.force_stream_on_tile(tile_index)
            else:
                QTimer.singleShot(3600000, lambda idx=tile_index: self.monitor_forced_stream(idx))  # 1 hour
        elif status == QMediaPlayer.BufferingMedia:
            # Still buffering - give it more time
            print(f"  Monitor: Tile {tile.tile_id} stream still buffering, continuing to wait")
            # Increment retry attempts
            self.retry_attempts[tile_index] = self.retry_attempts.get(tile_index, 0) + 1
            # If it's been buffering too long, try another stream
            if self.retry_attempts[tile_index] > 3:
                print(f"  Monitor: Tile {tile.tile_id} stream buffering timeout, trying another stream")
                self.force_stream_on_tile(tile_index)
            else:
                QTimer.singleShot(14400000, lambda idx=tile_index: self.monitor_forced_stream(idx))  # 4 hours
        elif status == QMediaPlayer.EndOfMedia:
            # Stream ended - try another one
            print(f"  Monitor: Tile {tile.tile_id} stream ended, trying another stream")
            self.force_stream_on_tile(tile_index)
        elif state == QMediaPlayer.StoppedState:
            # Player stopped - try another stream
            print(f"  Monitor: Tile {tile.tile_id} stream stopped, trying another stream")
            self.force_stream_on_tile(tile_index)
        elif status == QMediaPlayer.LoadedMedia or status == QMediaPlayer.BufferedMedia:
            if state != QMediaPlayer.PlayingState:
                # Stream loaded but not playing - start it
                print(f"  Monitor: Tile {tile.tile_id} stream loaded but not playing, starting playback")
                player.play()
            else:
                # Stream is playing! Success
                print(f"  Monitor: Tile {tile.tile_id} stream playing successfully")
                # Check again later to ensure it stays alive
                QTimer.singleShot(14400000, lambda idx=tile_index: self.monitor_forced_stream(idx))  # 4 hours
        else:
            # Unknown state - keep monitoring
            print(f"  Monitor: Tile {tile.tile_id} stream in status {status}, state {state}, continuing to monitor")
            QTimer.singleShot(300000, lambda idx=tile_index: self.monitor_forced_stream(idx))  # 5 minutes

    def get_random_local_video(self):
        """Returns a random local video file, preventing repetition."""
        # Initialize video history if not exists
        if not hasattr(self, 'used_local_videos'):
            self.used_local_videos = []
        
        # Re-filter the local_videos list to remove bad files
        valid_videos = []
        for video_path in self.local_videos:
            # Skip macOS metadata files (._) and hidden files
            basename = os.path.basename(video_path)
            if basename.startswith('._') or basename.startswith('.'):
                continue
                
            # Skip files that don't exist or are zero size
            if not os.path.exists(video_path) or os.path.getsize(video_path) <= 0:
                continue
                
            valid_videos.append(video_path)
        
        # Update self.local_videos with only valid videos
        self.local_videos = valid_videos
            
        if global_assigner and global_assigner.local_videos:
            # Use the global assigner's improved method
            return global_assigner.get_local_video()
        elif self.local_videos:
            # Local fallback with repetition prevention
            # Get videos that haven't been recently used
            available_videos = [v for v in self.local_videos if v not in self.used_local_videos]
            
            # If all videos have been used, reset and use any video
            if not available_videos:
                print("  All local videos have been played recently; resetting history")
                self.used_local_videos = []
                available_videos = self.local_videos
            
            if not available_videos:
                print("  Warning: No valid local videos available after filtering")
                return None
                
            # Choose a random video from available ones
            selected_video = random.choice(available_videos)
            
            # Track this video and maintain reasonable history size
            self.used_local_videos.append(selected_video)
            if len(self.used_local_videos) > min(len(self.local_videos) // 2, 10):
                self.used_local_videos.pop(0)  # Remove oldest entry
                
            return selected_video
        return None

    def retry_tile_stream(self, tile_index):
        """Improved retry logic with better stream validation and local video fallback."""
        if tile_index in self.retry_timers:
            print(f"  Retry for Tile {self.tiles[tile_index].tile_id} on {self.screen.name()} is throttled, skipping...")
            return

        print(f"  Attempting retry for Tile Index {tile_index} on {self.screen.name()}...")

        if tile_index < 0 or tile_index >= len(self.tiles) or tile_index >= len(self.players):
            print(f"    Retry failed: Invalid tile index {tile_index}.")
            return
        tile = self.tiles[tile_index]
        player = self.players[tile_index]
        if not tile or not player or not tile.parentWidget() or not tile.isVisible():
            print(f"    Retry failed: Tile or Player for index {tile_index} is invalid, removed, or not visible.")
            return

        failed_url = self.current_assignments.get(tile_index, None)
        if failed_url:
            print(f"    Failed URL was: {failed_url}")
            self.tried_urls[tile_index].add(failed_url)

        active_players = sum(1 for i, p in enumerate(self.players) if i in self.current_assignments and p.state() == QMediaPlayer.PlayingState)
        if active_players >= self.MAX_ACTIVE_PLAYERS:
            print(f"    Max active players ({self.MAX_ACTIVE_PLAYERS}) reached, pausing retry for Tile {tile.tile_id}.")
            tile.show_status("Max Streams Reached", is_error=True, duration_ms=5000)
            return

        # Check if we were using a stream and it failed
        was_using_stream = not self.using_local_video.get(tile_index, False)
        
        # First try to get a new stream if we weren't already using a local video
        if was_using_stream and self.all_m3u8_links:
            # Shuffle available streams to try different ones
            all_streams = self.all_m3u8_links.copy()
            random.shuffle(all_streams)
            available_streams = [url for url in all_streams if url not in self.tried_urls[tile_index]]

            if available_streams:
                new_url = available_streams[0]
                self.tried_urls[tile_index].add(new_url)
                new_url_short = new_url.split('/')[-1][:25]
                attempts = self.retry_attempts.get(tile_index, 0) + 1
                self.retry_attempts[tile_index] = attempts
                
                print(f"    Retrying Tile {tile.tile_id} with new stream: {new_url} (Attempt #{attempts})")
                tile.show_status(f"Retry #{attempts}: {new_url_short}...", duration_ms=8000)
                media = QMediaContent(QUrl(new_url))
                self.using_local_video[tile_index] = False

                player.stop()
                player.setMedia(media)
                player.play()

                self.current_assignments[tile_index] = new_url
                if global_assigner:
                    global_assigner.update_assignments(self.screen.name(), self.current_assignments)

                self.retry_timers[tile_index] = QTimer(self)
                self.retry_timers[tile_index].setSingleShot(True)
                self.retry_timers[tile_index].timeout.connect(lambda idx=tile_index: self.clear_retry_timer(idx))
                self.retry_timers[tile_index].start(5000)
                return
            
        # If we get here, either:
        # 1. We were using a stream and all streams have been tried
        # 2. We were already using a local video that failed
        
        # Fall back to local video
        if self.local_videos:
            local_video = self.get_random_local_video()
            if local_video:
                local_name = os.path.basename(local_video)
                print(f"    Falling back to local video for Tile {tile.tile_id}: {local_name}")
                tile.show_status(f"Local fallback: {local_name[:25]}...", duration_ms=8000)
                media = QMediaContent(QUrl.fromLocalFile(local_video))
                self.using_local_video[tile_index] = True
                
                player.stop()
                player.setMedia(media)
                player.play()
                
                self.current_assignments[tile_index] = local_video
                if global_assigner:
                    global_assigner.update_assignments(self.screen.name(), self.current_assignments)
                
                self.retry_timers[tile_index] = QTimer(self)
                self.retry_timers[tile_index].setSingleShot(True)
                self.retry_timers[tile_index].timeout.connect(lambda idx=tile_index: self.clear_retry_timer(idx))
                self.retry_timers[tile_index].start(5000)
                return
        
        # If we get here, we have no options left
        print(f"    Retry failed for Tile {tile.tile_id}: No streams or local videos available.")
        tile.show_status("No Media Available", is_error=True, duration_ms=10000)
        if tile_index in self.current_assignments:
            del self.current_assignments[tile_index]

    def clear_retry_timer(self, tile_index):
        """Clears the retry timer for a tile."""
        if tile_index in self.retry_timers:
            del self.retry_timers[tile_index]

    def pause_all_players(self):
        """Pauses all media players to reduce load."""
        for i, player in enumerate(self.players):
            if player and player.state() == QMediaPlayer.PlayingState:
                player.pause()
                print(f"Paused player for Tile {self.tiles[i].tile_id}")

    def resume_visible_players(self):
        """Resumes players for visible tiles, respecting the max active players limit.
        Prioritizes larger tiles and those in the center for better visual quality."""
        active_count = 0
        
        # Get all visible tile indexes with their size/position info
        visible_tiles_info = []
        for i, tile in enumerate(self.tiles):
            if not tile or not tile.isVisible():
                continue
                
            player = self.players[i]
            if not player or player.state() != QMediaPlayer.PausedState:
                continue
                
            # Get tile position and size for priority calculation
            pos = self.layout.indexOf(tile)
            if pos == -1:
                continue
                
            row, col, rowspan, colspan = self.layout.getItemPosition(pos)
            
            # Calculate priority score:
            # 1. Higher for streams vs local videos
            # 2. Higher for larger tiles (rowspan * colspan)
            # 3. Higher for tiles closer to center
            # This ensures streams and larger, more prominent tiles are prioritized
            center_row = self.GRID_ROWS / 2
            center_col = self.GRID_COLS / 2
            distance_from_center = abs(row - center_row) + abs(col - center_col)
            size_score = rowspan * colspan
            
            # Check if this is a stream (not a local video)
            is_stream = not self.using_local_video.get(i, False)
            stream_bonus = 100 if is_stream else 0  # Huge bonus for streams
            
            # Higher score = higher priority
            priority_score = stream_bonus + (size_score * 10) - distance_from_center
            
            visible_tiles_info.append((i, tile, priority_score))
        
        # Sort by priority score (highest first)
        visible_tiles_info.sort(key=lambda x: x[2], reverse=True)
        
        # Resume players in priority order, respecting MAX_ACTIVE_PLAYERS
        for i, tile, _ in visible_tiles_info:
            if active_count >= self.MAX_ACTIVE_PLAYERS:
                break
                
            player = self.players[i]
            if player and player.state() == QMediaPlayer.PausedState:
                # Apply performance optimization hint before playing
                if active_count == 0:
                    # First player gets highest priority
                    player.setProperty("decodePriority", "high")
                
                player.play()
                active_count += 1
                print(f"Resumed player for Tile {tile.tile_id} (priority)")
                
        print(f"Resumed {active_count} players with hardware acceleration")

    def check_and_refresh_streams(self):
        """Checks streams that may have failed after starting (stalled, ended)."""
        refreshed_count = 0
        for i, player in enumerate(self.players):
             if i >= len(self.tiles) or not self.tiles[i] or not player: continue
             tile = self.tiles[i]
             if not tile.isVisible():
                 continue
             state = player.state()
             status = player.mediaStatus()
             is_problem = state == QMediaPlayer.StoppedState or \
                          status in [QMediaPlayer.StalledMedia,
                                     QMediaPlayer.EndOfMedia,
                                     QMediaPlayer.NoMedia,
                                     QMediaPlayer.UnknownMediaStatus]

             if is_problem and i in self.current_assignments:
                old_url = self.current_assignments.get(i, "N/A")
                print(f"  Tile {tile.tile_id} ({self.screen.name()}): Health Check detected issue (State: {state}, Status: {status}). Refreshing media {old_url}...")
                
                # Immediately use local video if available and not already using one
                if self.local_videos and not self.using_local_video.get(i, False):
                    print(f"  Health check: Forcing local video fallback for Tile {tile.tile_id}")
                    self.force_local_video_fallback(i)
                else:
                    self.retry_tile_stream(i)
                    
                refreshed_count += 1

    def aggressive_black_tile_check(self):
        """Aggressively checks for black tiles and immediately uses local videos when needed."""
        for i, player in enumerate(self.players):
            if i >= len(self.tiles) or not self.tiles[i] or not player: continue
            tile = self.tiles[i]
            if not tile.isVisible():
                continue
            state = player.state()
            status = player.mediaStatus()
            
            is_black = False
            if status == QMediaPlayer.NoMedia:
                is_black = True
                print(f"  Black Tile {tile.tile_id}: No media")
            elif status == QMediaPlayer.InvalidMedia:
                is_black = True
                print(f"  Black Tile {tile.tile_id}: Invalid media")
            elif state == QMediaPlayer.StoppedState and i not in self.current_assignments:
                is_black = True
                print(f"  Black Tile {tile.tile_id}: Stopped with no assignment")
            elif status == QMediaPlayer.BufferingMedia:
                buffering_timeout = self.retry_attempts.get(i, 0)
                if buffering_timeout > 5:  # Increased threshold
                    is_black = True
                    print(f"  Black Tile {tile.tile_id}: Buffering timeout")
                else:
                    self.retry_attempts[i] = buffering_timeout + 1
            elif status == QMediaPlayer.LoadingMedia:
                loading_timeout = self.retry_attempts.get(i, 0)
                if loading_timeout > 8:  # Increased threshold
                    is_black = True
                    print(f"  Black Tile {tile.tile_id}: Loading timeout")
                else:
                    self.retry_attempts[i] = loading_timeout + 1
            
            if is_black:
                print(f"  Aggressive retrying for Tile {tile.tile_id} on {self.screen.name()}")
                
                # Count current local videos
                local_count = sum(1 for idx in range(self.NUM_TILES) if self.using_local_video.get(idx, False))
                local_percentage = local_count / len(self.tiles) if self.tiles else 0
                
                # If we're using too many local videos, try streams first
                if local_percentage > 0.5 and not self.using_local_video.get(i, False) and self.all_m3u8_links:
                    # Try another stream first
                    print(f"  Too many local videos ({local_percentage:.1%}) - trying to keep stream for Tile {tile.tile_id}")
                    self.force_stream_on_tile(i)
                elif self.local_videos:
                    # Otherwise use local fallback
                    print(f"  Forcing local video fallback for black Tile {tile.tile_id}")
                    self.force_local_video_fallback(i)
                else:
                    # No local fallback available, try another stream
                    self.retry_tile_stream(i)

    def handle_media_status(self, status, player, tile, tile_index):
        """Callback for QMediaPlayer's mediaStatusChanged signal."""
        if not tile or not tile.parentWidget() or not tile.isVisible(): return

        current_url = self.current_assignments.get(tile_index, "N/A")
        is_local = self.using_local_video.get(tile_index, False)
        
        if is_local:
            current_url_short = os.path.basename(current_url)[:25] if current_url != "N/A" else "N/A"
            prefix = "Local: "
        else:
            current_url_short = current_url.split('/')[-1][:25] if current_url != "N/A" else "N/A"
            prefix = "Stream: "

        if status == QMediaPlayer.LoadingMedia:
            tile.show_status(f"Loading {prefix}{current_url_short}...", duration_ms=8000)
            # Start a fail-safe timer to switch to local video if loading takes too long
            if not is_local and self.local_videos:
                QTimer.singleShot(8000, lambda idx=tile_index, s=status: self.check_and_fallback(idx, s))
        elif status == QMediaPlayer.LoadedMedia:
             if player.state() != QMediaPlayer.PlayingState: 
                 player.play()
             tile.show_status(f"Playing {prefix}{current_url_short}", duration_ms=2000)
             self.retry_attempts[tile_index] = 0
             self.tried_urls[tile_index].clear()
        elif status in [QMediaPlayer.InvalidMedia, QMediaPlayer.NoMedia]:
            print(f"ERROR: Tile {tile.tile_id} ({self.screen.name()}) - Invalid/No Media: {current_url}")
            tile.show_status(f"Invalid/No Media: {current_url_short}", is_error=True, duration_ms=5000)
            # Immediately fall back to local video if available
            if self.local_videos and not is_local:
                self.force_local_video_fallback(tile_index)
            else:
                QTimer.singleShot(300000, lambda idx=tile_index: self.retry_tile_stream(idx))  # 5 minutes delay
        elif status == QMediaPlayer.StalledMedia:
            print(f"WARN: Tile {tile.tile_id} ({self.screen.name()}) - Stalled Media: {current_url}")
            tile.show_status(f"Stalled: {current_url_short}", is_error=True, duration_ms=5000)
            # Quick fallback to local video if available
            if self.local_videos and not is_local:
                QTimer.singleShot(300000, lambda idx=tile_index: self.force_local_video_fallback(idx))  # 5 minutes delay
            else:
                QTimer.singleShot(300000, lambda idx=tile_index: self.retry_tile_stream(idx))  # 5 minutes delay
        elif status == QMediaPlayer.EndOfMedia:
            print(f"WARN: Tile {tile.tile_id} ({self.screen.name()}) - End of Media: {current_url}")
            tile.show_status(f"Ended: {current_url_short}", duration_ms=5000)
            # Immediately fall back to local video if available
            if self.local_videos and not is_local:
                self.force_local_video_fallback(tile_index)
            else:
                QTimer.singleShot(1000, lambda idx=tile_index: self.retry_tile_stream(idx))
        elif status == QMediaPlayer.BufferingMedia:
            attempts = self.retry_attempts.get(tile_index, 0)
            tile.show_status(f"Buffering: {current_url_short}... ({attempts})", duration_ms=4000)
            # If buffering for too long, switch to local video
            if attempts > 2 and self.local_videos and not is_local:
                QTimer.singleShot(3000, lambda idx=tile_index: self.force_local_video_fallback(idx))
        elif status == QMediaPlayer.BufferedMedia:
            tile.show_status(f"Buffered: {current_url_short}", duration_ms=1500)
            player.play()
            
    def check_and_fallback(self, tile_index, last_status):
        """Checks if media is still in the same status and falls back to local video if needed."""
        if tile_index >= len(self.players) or not self.tiles[tile_index]:
            return
            
        player = self.players[tile_index]
        if not player:
            return
            
        current_status = player.mediaStatus()
        
        # If still loading or in an error state, switch to local
        if (current_status == last_status or 
            current_status in [QMediaPlayer.InvalidMedia, QMediaPlayer.NoMedia, QMediaPlayer.StalledMedia]):
            if self.local_videos and not self.using_local_video.get(tile_index, False):
                print(f"  Fail-safe: Media still in {current_status} state. Switching to local video.")
                self.force_local_video_fallback(tile_index)
                
    def force_local_video_fallback(self, tile_index):
        """Force a specific tile to use a local video."""
        if not self.local_videos:
            print("No local videos available for fallback")
            return
            
        if tile_index >= len(self.tiles) or not self.tiles[tile_index]:
            return
            
        tile = self.tiles[tile_index]
        player = self.players[tile_index]
        
        if not tile or not player:
            return
            
        # Get the current local video if already using one
        current_local_video = None
        if self.using_local_video.get(tile_index, False):
            current_local_video = self.current_assignments.get(tile_index)
            print(f"Tile {tile.tile_id} already using local video: {os.path.basename(current_local_video) if current_local_video else 'unknown'}")
            
            # If we're already using a local video and it's playing normally, don't change it
            if (player.state() == QMediaPlayer.PlayingState and 
                player.mediaStatus() in [QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia]):
                print(f"  Local video is playing normally, not changing")
                return
            
        # Re-filter the local_videos list to remove bad files
        valid_videos = []
        for video_path in self.local_videos:
            # Skip macOS metadata files (._) and hidden files
            basename = os.path.basename(video_path)
            if basename.startswith('._') or basename.startswith('.'):
                continue
                
            # Skip files that don't exist or are zero size
            if not os.path.exists(video_path) or os.path.getsize(video_path) <= 0:
                continue
                
            valid_videos.append(video_path)
        
        # Update self.local_videos with only valid videos
        self.local_videos = valid_videos
                
        # Initialize specific tile history if needed
        if not hasattr(self, 'tile_video_history'):
            self.tile_video_history = {}
            
        if tile_index not in self.tile_video_history:
            self.tile_video_history[tile_index] = []
            
        # Get a new local video, excluding the current one and recently used ones for this tile
        available_videos = [v for v in self.local_videos 
                           if v != current_local_video and 
                           v not in self.tile_video_history[tile_index]]
                           
        # If no videos are available after filtering, reset history but still exclude current
        if not available_videos:
            print(f"  All local videos for Tile {tile.tile_id} have been played recently; resetting history")
            self.tile_video_history[tile_index] = []
            available_videos = [v for v in self.local_videos if v != current_local_video]
            
        # If still no videos (could happen if only 1 video exists), use any video
        if not available_videos:
            available_videos = self.local_videos
            
        local_video = random.choice(available_videos)
        
        # Update tile history
        self.tile_video_history[tile_index].append(local_video)
        if len(self.tile_video_history[tile_index]) > min(len(self.local_videos) // 2, 5):
            self.tile_video_history[tile_index].pop(0)  # Remove oldest
            
        # Apply the video    
        local_name = os.path.basename(local_video)
        print(f"Forcing local video fallback on Tile {tile.tile_id}: {local_name}")
        tile.show_status(f"Local fallback: {local_name[:25]}...", duration_ms=8000)
        media = QMediaContent(QUrl.fromLocalFile(local_video))
        self.using_local_video[tile_index] = True
        
        player.stop()
        player.setMedia(media)
        player.play()
        
        self.current_assignments[tile_index] = local_video
        if global_assigner:
            global_assigner.update_assignments(self.screen.name(), self.current_assignments)

    def handle_player_error(self, error, player, tile, tile_index):
        """Callback for QMediaPlayer's error signal."""
        if not tile or not tile.parentWidget() or not tile.isVisible(): return

        error_string = player.errorString()
        current_url = self.current_assignments.get(tile_index, "N/A")
        is_local = self.using_local_video.get(tile_index, False)
        
        if is_local:
            current_url_short = os.path.basename(current_url)[:25] if current_url != "N/A" else "N/A"
            print(f"ERROR: Tile {tile.tile_id} ({self.screen.name()}): PlayerError={error}, Msg='{error_string}', Local File='{current_url}'")
            # If local video has error, try another local video
            tile.show_status(f"Error {error}: {error_string[:50]}...", is_error=True, duration_ms=5000)
            if self.local_videos and len(self.local_videos) > 1:
                QTimer.singleShot(60000, lambda idx=tile_index: self.force_local_video_fallback(idx))  # 1 minute delay
            else:
                QTimer.singleShot(300000, lambda idx=tile_index: self.retry_tile_stream(idx))  # 5 minutes delay
        else:
            current_url_short = current_url.split('/')[-1][:25] if current_url != "N/A" else "N/A"
            print(f"ERROR: Tile {tile.tile_id} ({self.screen.name()}): PlayerError={error}, Msg='{error_string}', URL='{current_url}'")
            tile.show_status(f"Error {error}: {error_string[:50]}...", is_error=True, duration_ms=5000)
            
            # For stream errors, immediately fall back to local video if available
            if self.local_videos:
                QTimer.singleShot(60000, lambda idx=tile_index: self.force_local_video_fallback(idx))  # 1 minute delay
            else:
                QTimer.singleShot(300000, lambda idx=tile_index: self.retry_tile_stream(idx))  # 5 minutes delay

    def mouseDoubleClickEvent(self, event):
        """Toggles between fullscreen and windowed mode on double-click."""
        if self.is_fullscreen:
            # Switch to windowed mode
            self.showNormal()
            
            # Calculate a reasonable window size (75% of screen size)
            screen_size = self.screen.size()
            window_width = int(screen_size.width() * 0.75)
            window_height = int(screen_size.height() * 0.75)
            
            # Center the window on screen
            screen_geo = self.screen.geometry()
            x = screen_geo.x() + (screen_geo.width() - window_width) // 2
            y = screen_geo.y() + (screen_geo.height() - window_height) // 2
            
            # Set new geometry
            self.setGeometry(x, y, window_width, window_height)
            self.windowed_geometry = self.geometry()
            
            # Update state
            self.is_fullscreen = False
            
            # Provide feedback via console and window title
            status_msg = f"Switched to windowed mode for {self.screen.name()}"
            print(status_msg)
            
            # Temporarily update window title for feedback
            original_title = self.windowTitle()
            self.setWindowTitle("Video Wall - Windowed Mode")
            QTimer.singleShot(3000, lambda: self.setWindowTitle(original_title))
        else:
            # Switch back to fullscreen
            self.showFullScreen()
            self.is_fullscreen = True
            
            # Provide feedback via console and window title
            status_msg = f"Switched to fullscreen mode for {self.screen.name()}"
            print(status_msg)
            
            # Temporarily update window title for feedback
            original_title = self.windowTitle()
            self.setWindowTitle("Video Wall - Fullscreen Mode")
            QTimer.singleShot(3000, lambda: self.setWindowTitle(original_title))
            
        event.accept()
    
    def keyPressEvent(self, event):
        """Handles key presses for global window actions."""
        key = event.key()
        modifiers = event.modifiers()
        
        # Exit application with Escape or Ctrl+Q
        if key == Qt.Key_Escape and self.is_fullscreen:
            # When in fullscreen, Escape toggles to windowed mode instead of quitting
            self.showNormal()
            self.setGeometry(self.windowed_geometry)
            self.is_fullscreen = False
            
            # Provide feedback via console and window title
            status_msg = f"Switched to windowed mode for {self.screen.name()}"
            print(status_msg)
            
            # Temporarily update window title for feedback
            original_title = self.windowTitle()
            self.setWindowTitle("Video Wall - Windowed Mode")
            QTimer.singleShot(3000, lambda: self.setWindowTitle(original_title))
        elif key == Qt.Key_Escape and not self.is_fullscreen:
            # When in windowed mode, Escape quits
            print("Escape pressed in windowed mode, closing all windows...")
            QApplication.instance().quit()
        elif key == Qt.Key_Q and modifiers == Qt.ControlModifier:
            # Ctrl+Q always quits
            print("Ctrl+Q pressed, closing all windows...")
            QApplication.instance().quit()
        # Toggle fullscreen with F11 or Alt+F
        elif key == Qt.Key_F11 or (key == Qt.Key_F and modifiers == Qt.AltModifier):
            if self.is_fullscreen:
                self.showNormal()
                self.setGeometry(self.windowed_geometry)
                self.is_fullscreen = False
                
                # Provide feedback via console and window title
                status_msg = f"Switched to windowed mode for {self.screen.name()}"
                print(status_msg)
                
                # Temporarily update window title for feedback
                original_title = self.windowTitle()
                self.setWindowTitle("Video Wall - Windowed Mode")
                QTimer.singleShot(3000, lambda: self.setWindowTitle(original_title))
            else:
                self.showFullScreen()
                self.is_fullscreen = True
                
                # Provide feedback via console and window title
                status_msg = f"Switched to fullscreen mode for {self.screen.name()}"
                print(status_msg)
                
                # Temporarily update window title for feedback
                original_title = self.windowTitle()
                self.setWindowTitle("Video Wall - Fullscreen Mode")
                QTimer.singleShot(3000, lambda: self.setWindowTitle(original_title))
        elif key == Qt.Key_Space:
            paused_count = 0; playing_count = 0
            for p in self.players:
                 if not p: continue
                 try:
                      if p.state() == QMediaPlayer.PlayingState: playing_count += 1
                      elif p.state() == QMediaPlayer.PausedState: paused_count += 1
                 except RuntimeError: continue
            if playing_count > 0 :
                 print(f"Pausing players on {self.screen.name()}.")
                 for p in self.players:
                      if p:
                          try: p.pause()
                          except RuntimeError: pass
            else:
                 print(f"Playing players on {self.screen.name()}.")
                 for p in self.players:
                      if p:
                          try:
                              if p.mediaStatus() not in [QMediaPlayer.NoMedia, QMediaPlayer.InvalidMedia]: p.play()
                          except RuntimeError: pass
        elif key == Qt.Key_F:
             print(f"Manual stream health check triggered on {self.screen.name()}")
             self.check_and_refresh_streams()
        elif key == Qt.Key_S:
             print(f"Manual swap triggered on {self.screen.name()}")
             if self.animator: self.animator.trigger_random_swap()
        elif key == Qt.Key_R:
             print(f"R key pressed: Forcing random resize layout")
             if self.animator: self.animator.trigger_random_resize()
        elif key == Qt.Key_T:
             print(f"T key pressed: Forcing random transition")
             if self.animator: self.animator.trigger_random_action()
        elif key == Qt.Key_F11 or (key == Qt.Key_F and modifiers == Qt.ShiftModifier):
             print(f"F11 or Shift+F pressed: Forcing full-screen mode")
             if self.animator: self.animator.trigger_full_screen_takeover()
        elif key == Qt.Key_Right:
             print(f"Right Arrow pressed: Refreshing ALL monitors")
             # This screen
             self.refresh_all_tile_videos()
             
             # Broadcast to refresh all other video walls
             app = QApplication.instance()
             if app:
                 for window in app.topLevelWidgets():
                     if window != self and isinstance(window, VideoWall):
                         print(f"Broadcasting refresh to {window.screen.name()}")
                         window.refresh_all_tile_videos()
                         
        elif key == Qt.Key_L:
             print(f"L key pressed: Forcing local video fallback on a random tile")
             self.force_local_video_on_random_tile()
        super().keyPressEvent(event)
        
    def force_local_video_on_random_tile(self):
        """Forces a random visible tile to use a local video (for testing)."""
        if not self.local_videos:
            print("No local videos available")
            return
            
        visible_tiles = [i for i, tile in enumerate(self.tiles) if tile and tile.isVisible()]
        if not visible_tiles:
            return
            
        # Filter to tiles that aren't already using local video if possible
        stream_tiles = [i for i in visible_tiles if not self.using_local_video.get(i, False)]
        if stream_tiles:
            tile_index = random.choice(stream_tiles)
        else:
            tile_index = random.choice(visible_tiles)
            
        # Use the enhanced force_local_video_fallback method
        self.force_local_video_fallback(tile_index)

    def check_resource_usage(self):
        """Monitors system resources and manages player activity to optimize performance."""
        # Count active players
        active_players = 0
        hidden_players = 0
        streaming_players = 0
        local_players = 0
        
        for i, player in enumerate(self.players):
            if not player or i >= len(self.tiles) or not self.tiles[i]:
                continue
                
            if player.state() == QMediaPlayer.PlayingState:
                active_players += 1
                
                # Check if tile is hidden/visible
                if not self.tiles[i].isVisible():
                    hidden_players += 1
                    
                # Check if using stream or local video
                if not self.using_local_video.get(i, True):
                    streaming_players += 1
                else:
                    local_players += 1
        
        print(f"Resource check: {active_players} active players ({hidden_players} hidden, {streaming_players} streams, {local_players} local)")
        
        # With increased MAX_ACTIVE_PLAYERS, only pause players if we're significantly over the limit
        if active_players > self.MAX_ACTIVE_PLAYERS + 2:  # Allow a little buffer over the limit
            excess = active_players - self.MAX_ACTIVE_PLAYERS
            print(f"  Too many active players ({active_players}), need to pause {excess}")
            
            # Priority for pausing:
            # 1. Hidden players
            # 2. Local video players that are visible (prefer keeping streams active)
            # 3. Stream players that are visible (last resort)
            
            paused_count = 0
            
            # First, pause hidden players
            for i, player in enumerate(self.players):
                if paused_count >= excess:
                    break
                    
                if not player or i >= len(self.tiles) or not self.tiles[i]:
                    continue
                    
                tile = self.tiles[i]
                if player.state() == QMediaPlayer.PlayingState and not tile.isVisible():
                    print(f"  Pausing hidden player on Tile {tile.tile_id}")
                    player.pause()
                    paused_count += 1
            
            # Next, pause visible local video players to prioritize streams
            if paused_count < excess:
                for i, player in enumerate(self.players):
                    if paused_count >= excess:
                        break
                        
                    if not player or i >= len(self.tiles) or not self.tiles[i]:
                        continue
                        
                    tile = self.tiles[i]
                    if (player.state() == QMediaPlayer.PlayingState and 
                        tile.isVisible() and 
                        self.using_local_video.get(i, True)):
                        print(f"  Pausing visible local player on Tile {tile.tile_id}")
                        player.pause()
                        paused_count += 1
            
            # Finally, pause visible streaming players if still needed (try to avoid this)
            if paused_count < excess:
                for i, player in enumerate(self.players):
                    if paused_count >= excess:
                        break
                        
                    if not player or i >= len(self.tiles) or not self.tiles[i]:
                        continue
                        
                    tile = self.tiles[i]
                    if (player.state() == QMediaPlayer.PlayingState and 
                        tile.isVisible() and 
                        not self.using_local_video.get(i, True)):
                        print(f"  Pausing visible stream player on Tile {tile.tile_id}")
                        player.pause()
                        paused_count += 1
        
        # If we have room to play more players, resume some
        elif active_players < self.MAX_ACTIVE_PLAYERS - 1:  # Leave a small buffer
            available_slots = self.MAX_ACTIVE_PLAYERS - active_players
            
            # Priority for resuming:
            # 1. Visible stream players (prioritize streams with higher limit)
            # 2. Visible local video players
            # 3. Hidden players (lowest priority)
            
            resumed_count = 0
            
            # First, resume visible stream players
            for i, player in enumerate(self.players):
                if resumed_count >= available_slots:
                    break
                    
                if not player or i >= len(self.tiles) or not self.tiles[i]:
                    continue
                    
                tile = self.tiles[i]
                if (player.state() == QMediaPlayer.PausedState and 
                    tile.isVisible() and 
                    not self.using_local_video.get(i, True)):
                    print(f"  Resuming visible stream player on Tile {tile.tile_id}")
                    player.play()
                    resumed_count += 1
            
            # Next, resume visible local video players
            if resumed_count < available_slots:
                for i, player in enumerate(self.players):
                    if resumed_count >= available_slots:
                        break
                        
                    if not player or i >= len(self.tiles) or not self.tiles[i]:
                        continue
                        
                    tile = self.tiles[i]
                    if (player.state() == QMediaPlayer.PausedState and 
                        tile.isVisible() and 
                        self.using_local_video.get(i, True)):
                    
                        print(f"  Resuming visible local player on Tile {tile.tile_id}")
                        player.play()
                        resumed_count += 1
            
            # Finally, resume hidden players if needed (lower priority)
            if resumed_count < available_slots:
                for i, player in enumerate(self.players):
                    if resumed_count >= available_slots:
                        break
                        
                    if not player or i >= len(self.tiles) or not self.tiles[i]:
                        continue
                        
                    tile = self.tiles[i]
                    if (player.state() == QMediaPlayer.PausedState and 
                        not tile.isVisible()):
                        print(f"  Resuming hidden player on Tile {tile.tile_id}")
                        player.play()
                        resumed_count += 1

    def closeEvent(self, event):
        """Handles the window close event for clean shutdown."""
        print(f"Closing window on {self.screen.name()}...")
        self.check_timer.stop()
        self.black_tile_timer.stop()
        self.resource_check_timer.stop()  # Stop the resource check timer
        if self.animator: self.animator.stop_timers_and_animations()
        print("  Stopping media players...")
        for i, player in enumerate(self.players):
            if player:
                try:
                    player.setVideoOutput(None); player.stop()
                    self.players[i] = None
                except RuntimeError: self.players[i] = None
                except Exception as e: print(f"  Error stopping player {i}: {e}"); self.players[i] = None
        self.tiles.clear()
        print("  Cleanup complete.")
        event.accept()

# --- Main Execution Block ---
def test_stream(url, callback):
    """Test if a stream is working and call callback with result"""
    print(f"Testing stream: {url}")
    
    # Create test player with hardware acceleration enabled
    test_player = QMediaPlayer()
    
    # Enable hardware acceleration for macOS (VideoToolbox)
    test_player.setProperty("videoCodecOptions", {"hwaccel": "videotoolbox"})
    test_player.setProperty("videoGPUOptions", {"enable_mps": True})
    
    media = QMediaContent(QUrl(url))
    test_player.setMedia(media)
    
    # Track how many checks we've done
    check_count = [0]
    max_checks = 10  # Try up to 10 times (5 seconds)
    
    # Set up a timer to check status
    def check_status():
        status = test_player.mediaStatus()
        state = test_player.state()
        
        check_count[0] += 1
        print(f"  Status: {status}, State: {state}, Check: {check_count[0]}/{max_checks}")
        
        if status in [QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia, QMediaPlayer.BufferingMedia]:
            print(f"  SUCCESS: Stream loaded: {url}")
            callback(url, True)
            test_player.stop()
        elif status in [QMediaPlayer.InvalidMedia, QMediaPlayer.NoMedia] and check_count[0] >= max_checks:
            # Only mark as failed after multiple checks
            print(f"  FAIL: Stream invalid after {check_count[0]} attempts: {url}")
            callback(url, False) 
            test_player.stop()
        elif check_count[0] >= max_checks:
            # If we've checked many times but the stream is still loading, consider it valid
            # This handles slow streams that take time to initialize
            print(f"  POTENTIALLY VALID: Stream still loading after {check_count[0]} checks: {url}")
            callback(url, True)  # Mark as success to include it
            test_player.stop()
        else:
            # Still loading, check again
            QTimer.singleShot(500, check_status)
    
    # Start playing and check status
    test_player.play()
    QTimer.singleShot(1000, check_status)
    
    return test_player  # Return to keep it from being garbage collected

if __name__ == "__main__":
    # Start with a version announcement
    print("=" * 80)
    print("Video Wall v1.4.2 (Ultra-Slow Relaxed Edition) with Hardware Acceleration")
    print("Animation-optimized version - includes dynamic layouts")
    print("=" * 80)
    
    app = QApplication(sys.argv)
    
    # Enable hardware acceleration for Qt
    app.setAttribute(Qt.AA_UseOpenGLES, True)
    app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
    app.setAttribute(Qt.AA_UseDesktopOpenGL, True)
    app.setApplicationName("Dynamic Video Wall - Local Video Fallback")
    
    # Set up performance and hardware acceleration optimizations
    # Configure Qt multimedia backend to use VideoToolbox/MPS on macOS
    import platform
    if platform.system() == "Darwin":  # macOS
        # Set environment variables for hardware acceleration
        os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "AVFMediaPlayer"  # Use AVFoundation backend
        os.environ["QT_OPENGL"] = "software"  # Use software OpenGL for compatibility
        # Configure high performance video decoding
        os.environ["QT_AVFOUNDATION_VIDEOTOOLBOX_ENABLED"] = "1"  # Enable VideoToolbox
        print("macOS detected: Hardware acceleration (VideoToolbox & MPS) enabled")

    # Initialize variables
    m3u8_file = None
    m3u8_links = []
    working_streams = []
    use_local_videos = True  # Default to using local videos
    local_folder = None
    skip_stream_testing = True
    
    # Ask user if they want to use M3U8 streams or just local videos
    use_m3u8 = QMessageBox.question(
        None, 
        "Video Source",
        "Would you like to load an M3U8 playlist file with streaming sources?\n\n"
        "Select 'Yes' to choose an M3U8 file.\n"
        "Select 'No' to use only local video files.",
        QMessageBox.Yes | QMessageBox.No
    )
    
    # Handle M3U8 file selection if requested
    if use_m3u8 == QMessageBox.Yes:
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Link Files (*.txt *.m3u *.m3u8)")
        file_dialog.setWindowTitle("Select M3U8 Links File")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files: 
                m3u8_file = selected_files[0]
                m3u8_links = get_all_m3u8_links(m3u8_file) or []
                
                # Check if we found any links
                if not m3u8_links:
                    QMessageBox.warning(
                        None,
                        "No Links Found",
                        "No valid links were found in the selected file.\n"
                        "The application will continue with local videos only."
                    )
    
    # Show the configuration dialog for local videos
    config_dialog = LocalVideoDialog()
    if config_dialog.exec_() != QDialog.Accepted:
        print("Dialog canceled. Exiting.")
        sys.exit(0)
    
    dialog_results = config_dialog.get_results()
    use_local_videos = dialog_results["use_local_videos"]
    local_folder = dialog_results["folder_path"]
    skip_stream_testing = dialog_results["skip_stream_testing"]
    
    # Test streams if needed
    if m3u8_links and not skip_stream_testing:
        # Only test streams if user wants to
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Testing streams...")
        msg.setInformativeText("Please wait while we test a few streams to ensure they're working")
        msg.setWindowTitle("Stream Testing")
        msg.show()
        app.processEvents()
        
        test_streams = m3u8_links[:min(5, len(m3u8_links))]
        test_results = {}
        test_players = []
        
        def stream_tested(url, success):
            test_results[url] = success
            if success:
                working_streams.append(url)
            
            # If all tests complete
            if len(test_results) == len(test_streams):
                msg.hide()
                num_working = sum(1 for success in test_results.values() if success)
                if num_working == 0:
                    QMessageBox.warning(
                        None,
                        "Stream Testing Results",
                        f"No streams are working! We'll use local videos if available."
                    )
                else:
                    QMessageBox.information(
                        None,
                        "Stream Testing Results",
                        f"{num_working} out of {len(test_streams)} test streams are working."
                    )
        
        for url in test_streams:
            player = test_stream(url, stream_tested)
            test_players.append(player)  # Keep reference to prevent garbage collection
            
        app.processEvents()
    elif m3u8_links:
        # Skip testing - assume all streams are valid
        print("Skipping stream testing - assuming all streams are valid")
        working_streams = m3u8_links.copy()  # Consider all streams as working
    
    local_videos = []
    if use_local_videos and local_folder:
        local_videos = get_video_files_recursively(local_folder)
        if not local_videos:
            response = QMessageBox.question(
                None, 
                "No Videos Found", 
                "No video files were found in the selected folder. Continue without local videos?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.No:
                sys.exit(0)
    
    # Check if we have either streams or local videos
    if not m3u8_links and not local_videos:
        QMessageBox.critical(None, "Error", "No M3U8 links or local videos available. Application will exit.")
        sys.exit(1)
    
    if not m3u8_links:
        print("No M3U8 links loaded. Running with local videos only.")
        # Make sure the user has selected local videos if no streams
        if not local_videos:
            QMessageBox.critical(None, "Error", "No local videos selected. Please select a folder with video files.")
            sys.exit(1)
    if not local_videos:
        print("No local videos loaded. Running with M3U8 streams only.")
    
    # If we have working streams, prioritize them
    if working_streams:
        print(f"Prioritizing {len(working_streams)} known working streams")
        # Move working streams to front of list
        for url in reversed(working_streams):
            if url in m3u8_links:
                m3u8_links.remove(url)
                m3u8_links.insert(0, url)
    
    global_assigner = GlobalVideoAssigner(m3u8_links, local_videos)

    screens = QApplication.screens()
    if not screens:
        QMessageBox.critical(None, "Error", "No screens detected. Application will exit.")
        sys.exit(1)

    print(f"Detected {len(screens)} screens.")
    video_walls = []
    app.setQuitOnLastWindowClosed(True)

    for screen in screens:
        print(f"Creating wall for screen: {screen.name()} | Geometry: {screen.geometry()}")
        try:
            wall = VideoWall(m3u8_links, local_videos, screen)
            video_walls.append(wall)
        except Exception as e:
             print(f"FATAL ERROR creating wall for screen {screen.name()}: {e}")
             traceback.print_exc()
             QMessageBox.critical(None, "Initialization Error", f"Failed to create video wall for screen {screen.name()}:\n{e}")

    if not video_walls:
        QMessageBox.critical(None, "Error", "Failed to create any video wall windows. Application will exit.")
        sys.exit(1)

    print("Starting Qt event loop...")
    exit_code = app.exec_()
    print(f"Application finished with exit code: {exit_code}")
    sys.exit(exit_code)