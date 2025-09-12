"""
Main application entry point.
"""
import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from src.core.video_wall import VideoWall
from src.ui.dialogs import LocalVideoDialog
from src.utils.file_utils import get_all_m3u8_links, get_video_files_recursively
from src.config.settings import ICON_PATH

# Get the base path for bundled data
if hasattr(sys, '_MEIPASS'):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def main():
    """
    Initialize and run the VideoWall application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='VideoWall - Multi-screen video display application')
    parser.add_argument('--hwa-enabled', action='store_true', 
                       help='Enable hardware acceleration (default: CPU only)')
    args, qt_args = parser.parse_known_args()
    
    # Store HWA setting globally
    os.environ['VIDEOWALL_HWA_ENABLED'] = '1' if args.hwa_enabled else '0'
    
    # Create Qt application with remaining args
    app = QApplication(sys.argv[:1] + qt_args)
    
    # Set application icon
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    
    # Get M3U8 links
    m3u8_path = os.path.join(BASE_PATH, "m3u8-hosts.m3u8")
    m3u8_links = get_all_m3u8_links(m3u8_path) if os.path.exists(m3u8_path) else []
    
    # Debug output
    if m3u8_links:
        print(f"Loaded {len(m3u8_links)} M3U8 streams from {m3u8_path}")
        for i, link in enumerate(m3u8_links[:3], 1):
            print(f"  Stream {i}: {link[:60]}...")
    else:
        print(f"No M3U8 streams loaded from {m3u8_path}")
    
    # Show configuration dialog
    dialog = LocalVideoDialog()
    result = dialog.exec_()
    
    if result == 0:  # User canceled
        return 0
        
    config = dialog.get_results()
    
    # Get local videos if enabled
    local_videos = []
    if config["use_local_videos"] and config["folder_path"]:
        local_videos = get_video_files_recursively(config["folder_path"])
    
    # Print HWA status
    if args.hwa_enabled:
        print("Hardware acceleration: ENABLED")
    else:
        print("Hardware acceleration: DISABLED (CPU only)")
    
    # Create video wall for each screen
    screens = app.screens()
    video_walls = []
    
    for screen in screens:
        wall = VideoWall(app, m3u8_links, local_videos, screen)
        video_walls.append(wall)
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())