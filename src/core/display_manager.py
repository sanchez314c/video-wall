"""
Display manager for VideoWall.
"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout
from PyQt5.QtCore import Qt

from src.core.animator import TileAnimator
from src.ui.video_tile import VideoTile
from src.core.stream_tracker import GlobalVideoAssigner
from src.config.settings import DEFAULT_GRID_ROWS, DEFAULT_GRID_COLS

class DisplayManager:
    """
    Manages display configuration and screen setup for VideoWall.
    """
    def __init__(self, video_wall):
        """
        Initialize the display manager.
        
        Args:
            video_wall (VideoWall): The parent VideoWall instance
        """
        self.video_wall = video_wall
        self.screen = video_wall.screen
        self.grid_rows = DEFAULT_GRID_ROWS
        self.grid_cols = DEFAULT_GRID_COLS
        self.grid_layout = None
        self.central_widget = None
        self.tiles = []
        self.animator = None
        
        # Set up initial layout
        self._setup_layout()
        
    def _setup_layout(self):
        """Set up the grid layout and central widget."""
        # Create central widget
        self.central_widget = QWidget(self.video_wall)
        self.central_widget.setAttribute(Qt.WA_TranslucentBackground, False)
        self.central_widget.setStyleSheet("background-color: black;")
        self.video_wall.setCentralWidget(self.central_widget)

        # Create grid layout
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)
        
    def create_tiles(self, num_tiles):
        """
        Create video tiles for the display.
        
        Args:
            num_tiles (int): Number of tiles to create
            
        Returns:
            list: List of created VideoTile objects
        """
        # Clear existing tiles
        self.tiles = []
        
        # Calculate tile ID offset based on screen index
        screens_list = self.video_wall.app.screens()
        screen_index = screens_list.index(self.screen) if self.screen in screens_list else -1
        tile_id_offset = num_tiles * screen_index if screen_index != -1 else 1000
        
        # Create tiles
        for i in range(num_tiles):
            tile_id = tile_id_offset + i
            tile = VideoTile(tile_id, self.central_widget)
            self.tiles.append(tile)
            
        return self.tiles
        
    def initialize_grid(self, animator=True):
        """
        Initialize the grid layout with tiles.
        
        Args:
            animator (bool, optional): Whether to create a TileAnimator
            
        Returns:
            TileAnimator: The created animator, if requested
        """
        num_tiles = self.grid_rows * self.grid_cols
        
        # Create tiles if not already created
        if len(self.tiles) != num_tiles:
            self.create_tiles(num_tiles)
            
        # Add tiles to grid
        tile_index = 0
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if tile_index < len(self.tiles):
                    self.grid_layout.addWidget(self.tiles[tile_index], row, col)
                    tile_index += 1
                    
        # Create animator if requested
        if animator:
            self.animator = TileAnimator(
                self.tiles, 
                self.grid_layout, 
                self.grid_rows, 
                self.grid_cols, 
                self.video_wall
            )
            return self.animator
            
        return None
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        if self.video_wall.is_fullscreen:
            # Switch to windowed mode
            self.video_wall.showNormal()
            self.video_wall.setGeometry(self.video_wall.windowed_geometry)
            self.video_wall.is_fullscreen = False
        else:
            # Switch to fullscreen mode
            self.video_wall.windowed_geometry = self.video_wall.geometry()
            self.video_wall.showFullScreen()
            self.video_wall.is_fullscreen = True