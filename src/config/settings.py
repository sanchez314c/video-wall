"""
Configuration settings for VideoWall.

All app-wide constants. Imported across the codebase via
`from src.config.settings import <NAME>`.
"""

import os
import sys

# Default grid configuration
DEFAULT_GRID_ROWS = 4
DEFAULT_GRID_COLS = 4

# Visible tile constraints
MIN_VISIBLE_TILES = 6
MAX_VISIBLE_TILES = 12

# Player concurrency cap (enforced by VideoManager)
MAX_ACTIVE_PLAYERS = 15

# Latency mode: when True, VideoLoader sets QMediaPlayer.setNotifyInterval(50ms)
# instead of default 1000ms. Higher CPU cost.
LOW_LATENCY_MODE = False

# Timing configurations (milliseconds)
ANIMATION_DURATION_MS = 8000
STREAM_CHECK_INTERVAL_MS = 30000
VIDEO_LOADING_TIMEOUT_MS = 15000

# Resource paths — PyInstaller-aware via sys._MEIPASS
if hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESOURCE_DIR = os.path.join(BASE_DIR, "resources")
ICON_PATH = os.path.join(RESOURCE_DIR, "icons", "icon.png")
