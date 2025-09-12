#!/usr/bin/env python3

####################################################################################
#                                                                                  #
#  ██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗███████╗███████╗                   #
#  ██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝██║██╔════╝██╔════╝                   #
#  ██║   ██║   ██║   ██║██║     ██║   ██║   ██║█████╗  ███████╗                   #
#  ██║   ██║   ██║   ██║██║     ██║   ██║   ██║██╔══╝  ╚════██║                   #
#  ╚██████╔╝   ██║   ██║███████╗██║   ██║   ██║███████╗███████║                   #
#   ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝   ╚═╝╚══════╝╚══════╝                   #
#                                                                                  #
####################################################################################
#
# Script Name: video_utils.py
#
# Author: Jason Paul Michaels <jason@example.com>
#
# Date Created: 2025-05-24
#
# Last Modified: 2025-05-24
#
# Version: 1.0.0
#
# Description: Shared utility library for video wall applications providing
#              cross-platform compatibility, standardized functions, and
#              common video processing operations.
#
# Usage: from video_utils import *
#
# Dependencies: Python 3.6+, pathlib, tkinter
#
# GitHub: https://github.com/jasonpaulmichaels/videowall
#
# Features:
#    - Cross-platform file handling
#    - Standardized logging setup
#    - Video format detection
#    - Directory selection dialogs
#    - Process priority management
#    - Universal path handling
#
####################################################################################

"""
Video Wall Utilities Library
============================

Shared utilities for video wall applications providing cross-platform
compatibility and standardized functions for video processing, file
management, and user interface operations.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Video extensions supported across all platforms
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.m4v', '.mpg', '.mpeg', '.wmv', '.flv', '.webm', '.m3u8')

def setup_logging(name: str = "video-wall", level: int = logging.INFO) -> logging.Logger:
    """
    Set up standardized logging for video wall applications.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'{name}.log', mode='a')
        ]
    )
    return logging.getLogger(name)

def get_video_files(directory: str) -> List[str]:
    """
    Get all video files from a directory using pathlib for cross-platform compatibility.
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of video file paths
    """
    videos = []
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            logging.error(f"Directory does not exist: {directory}")
            return videos
            
        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                videos.append(str(file_path.absolute()))
                
        logging.info(f"Found {len(videos)} video files in {directory}")
        return sorted(videos)
        
    except Exception as e:
        logging.error(f"Error scanning directory {directory}: {e}")
        return videos

def select_video_directory() -> Optional[str]:
    """
    Show directory selection dialog with error handling.
    
    Returns:
        Selected directory path or None if cancelled
    """
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        directory = filedialog.askdirectory(
            title="Select Video Directory",
            initialdir=str(Path.home())
        )
        
        root.destroy()
        
        if directory:
            logging.info(f"Selected directory: {directory}")
            return directory
        else:
            logging.info("No directory selected")
            return None
            
    except Exception as e:
        logging.error(f"Error in directory selection: {e}")
        return None

def select_multiple_directories() -> List[str]:
    """
    Allow selection of multiple video directories.
    
    Returns:
        List of selected directory paths
    """
    directories = []
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # Ask user about selection method
        choice = messagebox.askyesno(
            "Selection Method",
            "Do you want to select multiple directories?\n\n"
            "Yes = Multiple directories\n"
            "No = Single directory"
        )
        
        if choice:
            # Multiple directories
            while True:
                directory = filedialog.askdirectory(
                    title=f"Select Video Directory ({len(directories)+1})",
                    initialdir=str(Path.home())
                )
                
                if directory:
                    directories.append(directory)
                    
                    if not messagebox.askyesno(
                        "Add Another?",
                        f"Added: {directory}\n\nDo you want to add another directory?"
                    ):
                        break
                else:
                    break
        else:
            # Single directory
            directory = filedialog.askdirectory(
                title="Select Video Directory",
                initialdir=str(Path.home())
            )
            if directory:
                directories.append(directory)
        
        root.destroy()
        return directories
        
    except Exception as e:
        logging.error(f"Error in multiple directory selection: {e}")
        return []

def validate_video_count(videos: List[str], minimum: int = 1) -> bool:
    """
    Validate that enough videos are available.
    
    Args:
        videos: List of video file paths
        minimum: Minimum number of videos required
        
    Returns:
        True if enough videos, False otherwise
    """
    if len(videos) < minimum:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Insufficient Videos",
                f"Found {len(videos)} videos, but need at least {minimum}.\n"
                f"Please select a directory with more video files."
            )
            root.destroy()
        except:
            print(f"Error: Found {len(videos)} videos, need at least {minimum}")
        return False
    return True

def set_process_priority():
    """
    Set appropriate process priority for video processing.
    """
    try:
        if sys.platform == 'darwin':  # macOS
            os.nice(10)  # Lower priority
        elif sys.platform == 'win32':  # Windows
            import psutil
            p = psutil.Process()
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        # Linux systems handle this automatically
    except Exception as e:
        logging.warning(f"Could not set process priority: {e}")

def get_safe_file_path(filepath: str) -> str:
    """
    Ensure file path is safe and properly encoded for the platform.
    
    Args:
        filepath: Original file path
        
    Returns:
        Safe file path
    """
    try:
        path = Path(filepath)
        return str(path.resolve())
    except Exception as e:
        logging.error(f"Error processing file path {filepath}: {e}")
        return filepath