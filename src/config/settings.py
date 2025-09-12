"""
Configuration settings for VideoWall.
"""
import os
import sys

# Default grid configuration
DEFAULT_GRID_ROWS = 3
DEFAULT_GRID_COLS = 3

# Performance settings
VIDEO_BUFFER_SIZE = 15000  # 15 seconds of buffer in milliseconds
LOW_LATENCY_MODE = False
HARDWARE_DECODE_PRIORITY = True
MAX_ACTIVE_PLAYERS = 15

# Hardware acceleration strategy
# Options: "all" (all hardware), "none" (all software), 
#          "alternate" (every other), "balanced" (50/50 random),
#          "adaptive" (based on video properties)
HARDWARE_ACCEL_STRATEGY = "alternate"

# Timing configurations
ANIMATION_DURATION_MS = 8000
STREAM_CHECK_INTERVAL_MS = 30000
VIDEO_LOADING_TIMEOUT_MS = 15000  # 15 seconds timeout for video loading

# Default configuration
DEFAULT_CONFIG = {
    "grid_rows": DEFAULT_GRID_ROWS,
    "grid_cols": DEFAULT_GRID_COLS,
    "use_local_videos": True,
    "skip_stream_testing": True,
    "max_active_players": 15,
}

# Resource paths
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESOURCE_DIR = os.path.join(BASE_DIR, "resources")
ICON_PATH = os.path.join(RESOURCE_DIR, "icon.png")