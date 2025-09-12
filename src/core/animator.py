"""
Animation controller for VideoWall tiles.
"""
import random
from PyQt5.QtCore import QObject, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtMultimedia import QMediaPlayer

from src.config.settings import ANIMATION_DURATION_MS

class TileAnimator(QObject):
    """
    Controls the animation of video tiles, including resizing,
    swapping, and full-screen transitions.
    """
    
    def __init__(self, tiles, layout, grid_rows, grid_cols, parent_window, parent=None):
        """
        Initialize the animator.
        
        Args:
            tiles (list): List of VideoTile objects
            layout (QGridLayout): Layout that contains the tiles
            grid_rows (int): Number of rows in the grid
            grid_cols (int): Number of columns in the grid
            parent_window: Parent window containing the video tiles
            parent (QObject, optional): Parent object
        """
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
        print(f"Animator initialized. Starting random interval timer.")
        self.start_random_timer()
        
    def get_tile_position(self, tile):
        """
        Attempts to find the grid row and column of a given tile widget.
        
        Args:
            tile (VideoTile): The tile to find the position of
            
        Returns:
            tuple: (row, col) position tuple, or None if not found
        """
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
            print(f"Animator: Reverting from full-screen mode")
            self.revert_from_full_screen()
        else:
            # Use the pre-selected transition type from previous timer
            transition_type = getattr(self, 'upcoming_transition_type', 'resize')
            
            # Execute the selected transition
            if transition_type == 'swap':
                print(f"Animator: Triggering Tile Swap")
                self.trigger_random_swap()
            elif transition_type == 'full_screen':
                print(f"Animator: Triggering Full-Screen Takeover")
                self.trigger_full_screen_takeover()
            elif transition_type == 'resize':
                print(f"Animator: Triggering Tile Resize")
                self.parent_window.refresh_all_videos()
            elif transition_type == 'refresh':
                print(f"Animator: Triggering Full Video Refresh")
                if self.parent_window:
                    self.parent_window.refresh_all_videos()

        # Start the next timer with a new transition type
        self.start_random_timer()

    def trigger_random_swap(self):
        """Selects two valid random tiles from the grid and initiates an animated swap."""
        if self.full_screen_tile:
            return
            
        valid_tiles = [t for t in self.tiles if t and t.parentWidget()]
        if len(valid_tiles) < 2:
            print(f"Animator: Not enough valid tiles ({len(valid_tiles)}) to perform swap.")
            return
            
        try:
            tile1, tile2 = random.sample(valid_tiles, 2)
        except ValueError:
            print(f"Animator: Error sampling tiles for swap.")
            return

        pos1 = self.get_tile_position(tile1)
        pos2 = self.get_tile_position(tile2)

        if pos1 and pos2:
            row1, col1 = pos1
            row2, col2 = pos2
            print(f"Animator: Swapping Tile {tile1.tile_id} ({row1},{col1}) with Tile {tile2.tile_id} ({row2},{col2})")
            self.animate_swap(tile1, tile2, row1, col1, row2, col2)
        else:
            print(f"Animator: Failed to get positions for swap (Pos1: {pos1}, Pos2: {pos2}). Aborting swap.")

    def start_random_timer(self):
        """Sets the random timer to trigger at much longer intervals for an extremely relaxed pace."""
        # More frequent intervals - 30-90 seconds for readily visible transitions
        possible_intervals_ms = [30000, 45000, 60000, 90000]
        interval_ms = random.choice(possible_intervals_ms)
        print(f"Animator: Next random action in {interval_ms / 1000} seconds.")
        
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
        """
        Handles the visual animation of swapping two tiles.
        
        Args:
            tile1 (VideoTile): First tile to swap
            tile2 (VideoTile): Second tile to swap
            row1 (int): Row of first tile
            col1 (int): Column of first tile
            row2 (int): Row of second tile
            col2 (int): Column of second tile
        """
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
        """
        Creates and starts a geometry animation for a tile with dramatically slower transitions.
        
        Args:
            tile (VideoTile): Tile to animate
            start_geom (QRect): Starting geometry
            end_rect (QRect): Ending geometry
        """
        if not tile or not tile.parentWidget():
             print(f"Warning: Attempted to animate invalid tile {getattr(tile, 'tile_id', 'N/A')}")
             return

        if tile in self.animations:
            self.animations[tile].stop()

        # Create the geometry animation
        animation = QPropertyAnimation(tile, b"geometry", self)
        
        # Set a more moderate duration for animations
        animation.setDuration(ANIMATION_DURATION_MS)  # 8 seconds for smooth transitions
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
        """
        Callback function when an animation completes.
        
        Args:
            tile (VideoTile): Tile whose animation has completed
        """
        tile_id = getattr(tile, 'tile_id', 'N/A')
        if tile in self.animations:
            del self.animations[tile]

    def calculate_target_rect(self, row, col, row_span=1, col_span=1):
        """
        Calculates the absolute screen rectangle for a given grid cell with spans.
        
        Args:
            row (int): Row in the grid
            col (int): Column in the grid
            row_span (int, optional): Number of rows to span
            col_span (int, optional): Number of columns to span
            
        Returns:
            QRect: Rectangle in absolute coordinates
        """
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

    def trigger_full_screen_takeover(self):
        """Selects a random tile to take over the entire screen."""
        valid_tiles = [t for t in self.tiles if t and t.parentWidget()]
        if not valid_tiles:
            print(f"Animator: No valid tiles for full-screen takeover.")
            return

        self.parent_window.video_manager.pause_all_players()

        for tile in self.tiles:
            if tile and tile.parentWidget():
                self.layout.removeWidget(tile)
                tile.hide()

        self.full_screen_tile = random.choice(valid_tiles)
        self.layout.addWidget(self.full_screen_tile, 0, 0, self.grid_rows, self.grid_cols)
        self.full_screen_tile.show()
        target_rect = self.calculate_target_rect(0, 0, self.grid_rows, self.grid_cols)
        self.start_animation(self.full_screen_tile, self.full_screen_tile.geometry(), target_rect)
        print(f"Tile {self.full_screen_tile.tile_id} taking over full screen")

        tile_index = self.tiles.index(self.full_screen_tile)
        player = self.parent_window.video_manager.players[tile_index]
        if player and player.state() != QMediaPlayer.PlayingState:
            player.play()
        
        # Try to recover stream if needed
        self.parent_window.video_manager.retry_tile_stream(tile_index)

    def revert_from_full_screen(self):
        """Reverts from full-screen mode to a normal layout."""
        if not self.full_screen_tile:
            return

        self.layout.removeWidget(self.full_screen_tile)
        self.full_screen_tile.hide()
        self.full_screen_tile = None
        
        # Trigger a full layout refresh
        self.parent_window.refresh_all_videos()

    def stop_timers_and_animations(self):
        """Stops the main timer and all currently running animations."""
        print(f"Animator: Stopping timer and animations...")
        self.random_timer.stop()
        for tile in list(self.animations.keys()):
             if tile in self.animations:
                 self.animations[tile].stop()
        self.animations.clear()