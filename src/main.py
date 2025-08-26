#!/usr/bin/env python3
"""
VideoWall - Main entry point for the application.
This file allows the app to be run directly without using the module syntax.
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    from src.core.app import main
    main()