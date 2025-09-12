#!/usr/bin/env python3

####################################################################################
#                                                                                  #
#  ██╗   ██╗██╗      ██████╗    ██╗   ██╗████████╗██╗██╗     ███████╗             #
#  ██║   ██║██║     ██╔════╝    ██║   ██║╚══██╔══╝██║██║     ██╔════╝             #
#  ██║   ██║██║     ██║         ██║   ██║   ██║   ██║██║     ███████╗             #
#  ╚██╗ ██╔╝██║     ██║         ██║   ██║   ██║   ██║██║     ╚════██║             #
#   ╚████╔╝ ███████╗╚██████╗    ╚██████╔╝   ██║   ██║███████╗███████║             #
#    ╚═══╝  ╚══════╝ ╚═════╝     ╚═════╝    ╚═╝   ╚═╝╚══════╝╚══════╝             #
#                                                                                  #
####################################################################################
#
# Script Name: vlc_utils.py
#
# Author: Jason Paul Michaels <jason@example.com>
#
# Date Created: 2025-05-24
#
# Last Modified: 2025-05-24
#
# Version: 1.0.0
#
# Description: Cross-platform VLC configuration utilities for video wall systems.
#              Provides optimized VLC settings, platform-specific configurations,
#              and hardware acceleration setup.
#
# Usage: from vlc_utils import *
#
# Dependencies: Python 3.6+, python-vlc, VLC Media Player
#
# GitHub: https://github.com/jasonpaulmichaels/videowall
#
# Features:
#    - Platform-specific VLC optimization
#    - Hardware acceleration configuration
#    - Cross-platform window embedding
#    - Performance tuning presets
#    - Audio/video codec selection
#
####################################################################################

"""
VLC Utilities for Video Wall Systems
====================================

Cross-platform VLC configuration and optimization utilities designed for
video wall applications. Provides intelligent platform detection and
hardware acceleration setup for optimal performance.
"""

import sys
import logging
from typing import List

logger = logging.getLogger(__name__)

def get_vlc_args() -> List[str]:
    """
    Get platform-specific VLC arguments for optimal performance.
    
    Returns:
        List of VLC command line arguments
    """
    base_args = [
        '--quiet',
        '--no-video-title-show',
        '--no-snapshot-preview',
        '--aspect-ratio=fill',
        '--zoom=1',
        '--aout=none',  # Disable audio output
        '--no-audio',   # Completely disable audio
        '--no-osd',     # No on-screen display
        '--no-spu',     # No subtitles
        '--no-stats',   # No statistics
        '--no-sub-autodetect-file'  # Don't auto-load subtitles
    ]
    
    if sys.platform == "darwin":  # macOS
        return base_args + [
            '--vout=macosx',  # Use native macOS video output
            '--avcodec-hw=videotoolbox',  # Use VideoToolbox for hardware decoding
        ]
    elif sys.platform == "linux":  # Linux
        return base_args + [
            '--no-xlib',
            '--vout=opengl',  # Use OpenGL video output
            '--hwdec=auto',   # Enable hardware decoding
            '--hwdec-voutchroma=vaapi',  # Use VAAPI for AMD/Intel
            '--avcodec-hw=any',  # Allow any hardware decoder
            '--video-filter=deinterlace',  # Add deinterlacing
            '--deinterlace-mode=blend',
        ]
    elif sys.platform == "win32":  # Windows
        return base_args + [
            '--vout=directx',  # Use DirectX video output
            '--avcodec-hw=dxva2',  # Use DXVA2 for hardware decoding
        ]
    else:
        # Fallback for other platforms
        return base_args + ['--vout=opengl']

def setup_vlc_player_window(player, widget):
    """
    Set up VLC player window for the current platform.
    
    Args:
        player: VLC media player instance
        widget: Qt widget to embed video in
    """
    try:
        if sys.platform == "darwin":  # macOS
            player.set_nsobject(int(widget.winId()))
        elif sys.platform == "linux":  # Linux
            player.set_xwindow(widget.winId())
        elif sys.platform == "win32":  # Windows
            player.set_hwnd(widget.winId())
        else:
            logger.warning("Unknown platform, using default VLC setup")
    except Exception as e:
        logger.error(f"Error setting up VLC player window: {e}")

def configure_vlc_player(player):
    """
    Configure VLC player with optimal settings.
    
    Args:
        player: VLC media player instance
    """
    try:
        # Set volume to 0 (muted)
        player.audio_set_volume(0)
        
        # Auto scale video
        player.video_set_scale(0)
        
        # Set aspect ratio
        player.video_set_aspect_ratio("16:9")
        
    except Exception as e:
        logger.error(f"Error configuring VLC player: {e}")