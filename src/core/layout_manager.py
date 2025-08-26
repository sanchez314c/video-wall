"""
Layout management for the VideoWall application.
"""
import random
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import QTimer

from src.config.settings import MIN_VISIBLE_TILES, MAX_VISIBLE_TILES


class LayoutManager:
    """
    Manages the layout of video tiles in the grid.
    Enforces MIN_VISIBLE_TILES to MAX_VISIBLE_TILES visible at all times.
    """

    def __init__(self, display_manager):
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
        Retries until visible tile count is within MIN/MAX bounds.
        """
        max_attempts = 5
        for attempt in range(max_attempts):
            pattern = self._try_layout()
            visible = self._count_visible_tiles()

            if MIN_VISIBLE_TILES <= visible <= MAX_VISIBLE_TILES:
                print(f"Layout '{pattern}': {visible} visible tiles (attempt {attempt + 1})")
                return pattern
            else:
                print(f"Layout '{pattern}' produced {visible} tiles (need {MIN_VISIBLE_TILES}-{MAX_VISIBLE_TILES}), retrying...")

        # Fallback: force a clean grid of 1x1 tiles, showing exactly MAX_VISIBLE_TILES
        self._apply_fallback_grid()
        visible = self._count_visible_tiles()
        print(f"Fallback grid: {visible} visible tiles")
        return 'fallback_grid'

    def _try_layout(self):
        """Attempt a single random layout. Returns the pattern name."""
        layout_patterns = [
            'varied',
            'feature',
            'columns',
            'rows',
            'mixed',
            'asymmetric'
        ]
        pattern = random.choice(layout_patterns)

        # Remove all tiles from the layout
        for tile in self.tiles:
            if tile and tile.parentWidget():
                self.grid_layout.removeWidget(tile)
                tile.hide()

        # Initialize tracking of occupied cells
        self.occupied_cells = [[False] * self.grid_cols for _ in range(self.grid_rows)]

        # Get tile sizes for this pattern (all capped at 2x2 max)
        possible_sizes = self._get_possible_sizes(pattern)

        if pattern == 'feature':
            self._apply_feature_layout(possible_sizes)
        else:
            self._apply_standard_layout(possible_sizes)

        return pattern

    def _count_visible_tiles(self):
        """Count how many tiles are currently visible."""
        return sum(1 for t in self.tiles if t and t.isVisible())

    def _apply_fallback_grid(self):
        """Force a clean grid with exactly MAX_VISIBLE_TILES as 1x1."""
        for tile in self.tiles:
            if tile and tile.parentWidget():
                self.grid_layout.removeWidget(tile)
                tile.hide()

        self.occupied_cells = [[False] * self.grid_cols for _ in range(self.grid_rows)]

        tiles_to_place = self.tiles.copy()
        random.shuffle(tiles_to_place)
        placed = 0

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if placed >= MAX_VISIBLE_TILES or placed >= len(tiles_to_place):
                    break
                tile = tiles_to_place[placed]
                self.grid_layout.addWidget(tile, row, col, 1, 1)
                tile.show()
                self.current_layout[self.tiles.index(tile)] = (1, 1)
                self.occupied_cells[row][col] = True
                placed += 1
            if placed >= MAX_VISIBLE_TILES:
                break

    def _get_possible_sizes(self, pattern):
        """
        Get possible tile sizes based on the layout pattern.
        All sizes capped at 2x2 max to ensure 6-12 visible tiles.
        """
        if pattern == 'varied':
            return [(2, 2), (1, 2), (2, 1), (1, 1), (1, 1), (1, 1)]
        elif pattern == 'feature':
            return [(2, 2), (1, 2), (2, 1), (1, 1)]
        elif pattern == 'columns':
            return [(2, 1), (1, 1), (1, 1)]
        elif pattern == 'rows':
            return [(1, 2), (1, 1), (1, 1)]
        elif pattern == 'mixed':
            return [(2, 2), (1, 2), (2, 1), (1, 1)]
        else:  # asymmetric
            return [(2, 2), (2, 1), (1, 2), (1, 1)]

    def _apply_feature_layout(self, possible_sizes):
        """Apply a layout with one prominent 2x2 feature tile."""
        tiles_to_place = self.tiles.copy()
        random.shuffle(tiles_to_place)

        if len(tiles_to_place) > 0:
            feature_tile = tiles_to_place[0]
            row_span, col_span = 2, 2

            # Random position for the feature tile (must fit)
            max_row = self.grid_rows - row_span
            max_col = self.grid_cols - col_span
            row = random.randint(0, max_row)
            col = random.randint(0, max_col)

            for r in range(row, row + row_span):
                for c in range(col, col + col_span):
                    self.occupied_cells[r][c] = True

            self.grid_layout.addWidget(feature_tile, row, col, row_span, col_span)
            feature_tile.show()
            self.current_layout[self.tiles.index(feature_tile)] = (row_span, col_span)
            tiles_to_place.pop(0)

        self._place_remaining_tiles(tiles_to_place, possible_sizes)

    def _apply_standard_layout(self, possible_sizes):
        """Apply a standard layout pattern."""
        tiles_to_place = self.tiles.copy()
        random.shuffle(tiles_to_place)
        self._place_remaining_tiles(tiles_to_place, possible_sizes)

    def _place_remaining_tiles(self, tiles_to_place, possible_sizes):
        """
        Place tiles in the grid, stopping at MAX_VISIBLE_TILES.
        """
        tile_idx = 0
        visible_count = self._count_visible_tiles()

        while tile_idx < len(tiles_to_place) and visible_count < MAX_VISIBLE_TILES:
            tile = tiles_to_place[tile_idx]
            if not tile:
                tile_idx += 1
                continue

            placed = False

            filtered_sizes = self._filter_sizes_that_fit(possible_sizes)
            if not filtered_sizes:
                filtered_sizes = [(1, 1)]

            preferred_size = random.choice(filtered_sizes)
            placed = self._try_place_tile_with_size(tile, preferred_size)

            if not placed:
                for size in filtered_sizes:
                    if self._try_place_tile_with_size(tile, size):
                        placed = True
                        break

            if placed:
                visible_count += 1

            tile_idx += 1

        # Fill remaining gaps up to MAX_VISIBLE_TILES
        unplaced = [t for t in tiles_to_place[tile_idx:] if t]
        self._fill_gaps(unplaced, MAX_VISIBLE_TILES - visible_count)

    def _filter_sizes_that_fit(self, possible_sizes):
        """Filter tile sizes that can fit in the remaining space."""
        filtered_sizes = []
        for row_span, col_span in possible_sizes:
            for row in range(self.grid_rows - row_span + 1):
                for col in range(self.grid_cols - col_span + 1):
                    if self._check_fit(row, col, row_span, col_span):
                        filtered_sizes.append((row_span, col_span))
                        break
                if (row_span, col_span) in filtered_sizes:
                    break
        return filtered_sizes

    def _check_fit(self, row, col, row_span, col_span):
        """Check if a tile of given size can fit at the specified position."""
        if row + row_span > self.grid_rows or col + col_span > self.grid_cols:
            return False
        for r in range(row, row + row_span):
            for c in range(col, col + col_span):
                if self.occupied_cells[r][c]:
                    return False
        return True

    def _try_place_tile_with_size(self, tile, size):
        """Try to place a tile with the given size anywhere in the grid."""
        row_span, col_span = size

        for row in range(self.grid_rows - row_span + 1):
            for col in range(self.grid_cols - col_span + 1):
                if self._check_fit(row, col, row_span, col_span):
                    for r in range(row, row + row_span):
                        for c in range(col, col + col_span):
                            self.occupied_cells[r][c] = True

                    self.grid_layout.addWidget(tile, row, col, row_span, col_span)
                    tile.show()
                    self.current_layout[self.tiles.index(tile)] = (row_span, col_span)
                    return True
        return False

    def _fill_gaps(self, remaining_tiles, max_to_fill):
        """Fill remaining gaps with 1x1 tiles, up to max_to_fill."""
        remaining_tiles = [t for t in remaining_tiles if t]
        filled = 0

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                if not self.occupied_cells[row][col] and remaining_tiles and filled < max_to_fill:
                    tile = remaining_tiles.pop(0)
                    self.grid_layout.addWidget(tile, row, col, 1, 1)
                    tile.show()
                    self.current_layout[self.tiles.index(tile)] = (1, 1)
                    self.occupied_cells[row][col] = True
                    filled += 1
