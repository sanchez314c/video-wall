"""
Layout management for the VideoWall application.
"""
import random
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import QTimer

class LayoutManager:
    """
    Manages the layout of video tiles in the grid.
    """
    
    def __init__(self, display_manager):
        """
        Initialize the layout manager.
        
        Args:
            display_manager (DisplayManager): The display manager instance
        """
        self.display_manager = display_manager
        self.grid_layout = display_manager.grid_layout
        self.grid_rows = display_manager.grid_rows
        self.grid_cols = display_manager.grid_cols
        self.tiles = display_manager.tiles
        self.current_layout = [(1, 1)] * len(self.tiles)
        self.occupied_cells = None
        
    def apply_random_layout(self):
        """
        Apply a random layout pattern to the grid.
        
        Returns:
            str: The name of the layout pattern applied
        """
        # Select a layout pattern
        layout_patterns = [
            'varied',        # Mix of different size tiles
            'feature',       # One dominant feature tile with smaller ones
            'columns',       # Column-based layout
            'rows',          # Row-based layout
            'grid',          # Standard grid (2x2, 3x3, etc.)
            'asymmetric'     # Asymmetric design
        ]
        pattern = random.choice(layout_patterns)
        
        # Remove all tiles from the layout
        for tile in self.tiles:
            if tile and tile.parentWidget():
                self.grid_layout.removeWidget(tile)
                tile.hide()
        
        # Initialize tracking of occupied cells
        self.occupied_cells = [[False] * self.grid_cols for _ in range(self.grid_rows)]
        
        # Define tile size options based on pattern
        possible_sizes = self._get_possible_sizes(pattern)
        
        # Handle feature layout specially
        if pattern == 'feature':
            self._apply_feature_layout(possible_sizes)
        else:
            # Apply the selected layout pattern
            self._apply_standard_layout(possible_sizes)
        
        return pattern
    
    def _get_possible_sizes(self, pattern):
        """
        Get possible tile sizes based on the layout pattern.
        
        Args:
            pattern (str): The layout pattern
            
        Returns:
            list: List of possible (row_span, col_span) tuples
        """
        if pattern == 'varied':
            return [(2, 2), (1, 3), (3, 1), (1, 1), (2, 1), (1, 2)]
        elif pattern == 'feature':
            return [(3, 3), (2, 2), (1, 1)]  # Allow for one big feature tile
        elif pattern == 'columns':
            return [(4, 1), (3, 1), (2, 1), (1, 1)]  # Vertical column layouts
        elif pattern == 'rows':
            return [(1, 4), (1, 3), (1, 2), (1, 1)]  # Horizontal row layouts
        elif pattern == 'grid':
            # Pick a specific grid size for consistency
            grid_size = random.choice([(2, 2), (4, 4), (3, 2), (2, 3)])
            row_size, col_size = grid_size
            return [(row_size, col_size)]
        else:  # asymmetric
            return [(2, 3), (3, 2), (2, 1), (1, 2), (1, 1)]
    
    def _apply_feature_layout(self, possible_sizes):
        """
        Apply a layout with one prominent feature tile.
        
        Args:
            possible_sizes (list): List of possible tile sizes
        """
        tiles_to_place = self.tiles.copy()
        random.shuffle(tiles_to_place)
        
        # Place a large feature tile first
        if len(tiles_to_place) > 0:
            feature_tile = tiles_to_place[0]
            feature_size = (3, 3) if self.grid_rows >= 4 and self.grid_cols >= 4 else (2, 2)
            row, col = 0, 0
            row_span, col_span = feature_size
            
            # Mark cells as occupied
            for r in range(row, row + row_span):
                for c in range(col, col + col_span):
                    if r < self.grid_rows and c < self.grid_cols:
                        self.occupied_cells[r][c] = True
                        
            # Add the feature tile
            self.grid_layout.addWidget(feature_tile, row, col, row_span, col_span)
            feature_tile.show()
            self.current_layout[self.tiles.index(feature_tile)] = (row_span, col_span)
            
            # Remove the feature tile from tiles to place
            tiles_to_place.pop(0)
        
        # Place the rest of the tiles using standard approach
        self._place_remaining_tiles(tiles_to_place, possible_sizes)
    
    def _apply_standard_layout(self, possible_sizes):
        """
        Apply a standard layout pattern.
        
        Args:
            possible_sizes (list): List of possible tile sizes
        """
        tiles_to_place = self.tiles.copy()
        random.shuffle(tiles_to_place)
        self._place_remaining_tiles(tiles_to_place, possible_sizes)
    
    def _place_remaining_tiles(self, tiles_to_place, possible_sizes):
        """
        Place tiles in the grid.
        
        Args:
            tiles_to_place (list): List of tiles to place
            possible_sizes (list): List of possible tile sizes
        """
        tile_idx = 0
        while tile_idx < len(tiles_to_place) and tiles_to_place[tile_idx]:
            tile = tiles_to_place[tile_idx]
            placed = False
            
            # Filter possible sizes based on remaining space
            filtered_sizes = self._filter_sizes_that_fit(possible_sizes)
            
            # If no sizes fit, use 1x1
            if not filtered_sizes:
                filtered_sizes = [(1, 1)]
            
            # Try to place the tile with a random size from filtered options
            preferred_size = random.choice(filtered_sizes)
            placed = self._try_place_tile_with_size(tile, preferred_size)
            
            if not placed:
                # Try all possible sizes if preferred size didn't work
                for size in filtered_sizes:
                    if self._try_place_tile_with_size(tile, size):
                        placed = True
                        break
            
            # Move to next tile
            tile_idx += 1
        
        # Fill any remaining gaps with 1x1 tiles
        self._fill_gaps(tiles_to_place[tile_idx:])
    
    def _filter_sizes_that_fit(self, possible_sizes):
        """
        Filter tile sizes that can fit in the remaining space.
        
        Args:
            possible_sizes (list): List of possible (row_span, col_span) tuples
            
        Returns:
            list: Filtered list of tile sizes that can fit
        """
        filtered_sizes = []
        for row_span, col_span in possible_sizes:
            # Check if this size can fit anywhere
            for row in range(self.grid_rows - row_span + 1):
                for col in range(self.grid_cols - col_span + 1):
                    if self._check_fit(row, col, row_span, col_span):
                        filtered_sizes.append((row_span, col_span))
                        break
                if (row_span, col_span) in filtered_sizes:
                    break
        
        return filtered_sizes
    
    def _check_fit(self, row, col, row_span, col_span):
        """
        Check if a tile of given size can fit at the specified position.
        
        Args:
            row (int): Starting row
            col (int): Starting column
            row_span (int): Number of rows
            col_span (int): Number of columns
            
        Returns:
            bool: True if the tile fits, False otherwise
        """
        # Check bounds
        if row + row_span > self.grid_rows or col + col_span > self.grid_cols:
            return False
        
        # Check if all cells are unoccupied
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                if self.occupied_cells[r][c]:
                    return False
        
        return True
    
    def _try_place_tile_with_size(self, tile, size):
        """
        Try to place a tile with the given size anywhere in the grid.
        
        Args:
            tile: The tile to place
            size (tuple): (row_span, col_span) size to use
            
        Returns:
            bool: True if placed successfully, False otherwise
        """
        row_span, col_span = size
        
        for row in range(self.grid_rows - row_span + 1):
            for col in range(self.grid_cols - col_span + 1):
                if self._check_fit(row, col, row_span, col_span):
                    # Mark cells as occupied
                    for r in range(row, row + row_span):
                        for c in range(col, col + col_span):
                            self.occupied_cells[r][c] = True
                    
                    # Add the tile
                    self.grid_layout.addWidget(tile, row, col, row_span, col_span)
                    tile.show()
                    self.current_layout[self.tiles.index(tile)] = (row_span, col_span)
                    
                    return True
        
        return False
    
    def _fill_gaps(self, remaining_tiles):
        """
        Fill any remaining gaps with 1x1 tiles.
        
        Args:
            remaining_tiles (list): Tiles that haven't been placed yet
        """
        remaining_tiles = [t for t in remaining_tiles if t]
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if not self.occupied_cells[row][col] and remaining_tiles:
                    tile = remaining_tiles.pop(0)
                    self.grid_layout.addWidget(tile, row, col, 1, 1)
                    tile.show()
                    self.current_layout[self.tiles.index(tile)] = (1, 1)
                    self.occupied_cells[row][col] = True
                    
                    if not remaining_tiles:
                        break
            
            if not remaining_tiles:
                break