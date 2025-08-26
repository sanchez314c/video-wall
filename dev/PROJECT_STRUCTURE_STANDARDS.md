# VideoWall Project Structure & Standards

Complete documentation of the VideoWall application's file structure, naming conventions, architectural patterns, and development standards. This document serves as the definitive guide for understanding and maintaining the codebase.

## Project File Structure

```
VideoWall/
├── src/                           # Source code directory (Python package)
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # Application entry point with CLI argument parsing
│   │
│   ├── core/                     # Core application logic
│   │   ├── __init__.py
│   │   ├── app.py                # Main application class and Qt app setup
│   │   ├── video_wall.py         # VideoWall orchestrator managing all components
│   │   ├── video_manager.py      # Stream/video playback coordination
│   │   ├── video_loader.py       # Media loading and hardware detection
│   │   ├── display_manager.py    # Multi-monitor detection and management
│   │   ├── layout_manager.py     # Grid layout calculations
│   │   ├── stream_tracker.py     # M3U8 stream health monitoring
│   │   └── animator.py           # Tile animation and transitions
│   │
│   ├── ui/                       # User interface components
│   │   ├── __init__.py
│   │   ├── video_tile.py         # Individual video tile widget
│   │   ├── dialogs.py            # Configuration dialogs (LocalVideoDialog)
│   │   └── status_overlay.py     # Debug/status overlay widget
│   │
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── file_utils.py         # File operations and M3U8 parsing
│   │   └── stream_utils.py       # Stream validation and processing
│   │
│   └── config/                   # Configuration management
│       ├── __init__.py
│       └── settings.py           # Application constants and defaults
│
├── assets/                       # Application assets
│   ├── icon.icns                # macOS application icon
│   ├── icon.ico                 # Windows application icon
│   └── icon.png                 # Cross-platform icon (256x256)
│
├── dist/                         # Compiled binaries (generated)
│   ├── macos-intel/             # macOS Intel build
│   │   └── VideoWall.app/       # macOS application bundle
│   │       └── Contents/
│   │           ├── Info.plist   # App metadata
│   │           ├── MacOS/       # Binary executable
│   │           └── Resources/   # App resources and icon
│   ├── macos-arm64/             # macOS ARM64 build
│   ├── windows/                 # Windows build
│   │   └── VideoWall.exe        # Windows executable
│   ├── linux/                   # Linux build
│   │   └── VideoWall            # Linux binary
│   ├── installers/              # Platform installers
│   │   ├── VideoWall-1.0.0-intel.dmg    # macOS Intel installer
│   │   ├── VideoWall-1.0.0-arm64.dmg    # macOS ARM64 installer
│   │   ├── VideoWall-1.0.0-setup.exe    # Windows installer
│   │   └── VideoWall-1.0.0.AppImage     # Linux AppImage
│   └── build-info.json          # Build metadata
│
├── build/                        # PyInstaller build artifacts (generated)
│   └── VideoWall/               # Temporary build files
│
├── venv/                        # Python virtual environment (generated)
│   ├── bin/                    # Virtual env executables
│   ├── lib/                    # Installed packages
│   └── include/                # Header files
│
├── legacy/                      # Previous implementations (reference only)
│   ├── standalone-pyqt5-video-wall-with-effects.py
│   ├── stream-based-dynamic-video-wall-m3u8.py
│   └── video_utils.py
│
├── dev/                         # Development documentation
│   ├── compile-build-python.md # Build system documentation
│   ├── CLAUDE.md               # AI assistant guidelines
│   ├── PROJECT_STRUCTURE_STANDARDS.md  # This document
│   └── VERSION_MAP.md          # Version history
│
├── docs/                        # User documentation
│   └── STREAMS_CONFIGURATION.md # Stream setup guide
│
├── tests/                       # Test suite (if implemented)
│   ├── __init__.py
│   ├── test_video_manager.py
│   ├── test_display_manager.py
│   └── test_stream_tracker.py
│
├── scripts/                     # Build and utility scripts
│   ├── compile-build-dist.sh   # Main build script
│   ├── run-python-source.sh    # Run from source
│   └── run-python.sh           # Run compiled binary
│
├── m3u8-hosts.m3u8             # M3U8 stream URLs configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
└── VideoWall.spec             # PyInstaller spec (generated)
```

## File Naming Conventions

### Python Files
- **Module files**: `snake_case.py` (e.g., `video_manager.py`)
- **Class names**: `PascalCase` (e.g., `VideoWall`, `LocalVideoDialog`)
- **Function names**: `snake_case` (e.g., `load_stream()`, `get_random_stream()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ACTIVE_PLAYERS`, `VIDEO_BUFFER_SIZE`)
- **Private methods**: `_leading_underscore` (e.g., `_handle_player_error()`)

### Configuration Files
- **M3U8 playlist**: `m3u8-hosts.m3u8` (hyphenated, lowercase)
- **Requirements**: `requirements.txt` (standard Python convention)
- **Documentation**: `UPPERCASE.md` for importance, `lowercase.md` for regular docs
- **Scripts**: `hyphenated-name.sh` (e.g., `compile-build-dist.sh`)

### Build Artifacts
- **Application name**: `VideoWall` (PascalCase, no spaces)
- **Version format**: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)
- **Platform identifiers**: `macos-intel`, `macos-arm64`, `windows`, `linux`
- **Installer naming**: `[AppName]-[version]-[platform].[ext]`
  - Example: `VideoWall-1.0.0-intel.dmg`

## Code Organization Principles

### Module Responsibilities

#### Core Layer (`src/core/`)
Handles business logic and application orchestration:

- **`app.py`**: Application initialization, argument parsing, Qt setup
- **`video_wall.py`**: Central coordinator, manages all components
- **`video_manager.py`**: Individual tile content management
- **`video_loader.py`**: Media loading strategies, codec detection
- **`display_manager.py`**: Screen detection, geometry calculations
- **`layout_manager.py`**: Grid mathematics, tile positioning
- **`stream_tracker.py`**: Health monitoring, retry logic
- **`animator.py`**: Visual effects, transitions

#### UI Layer (`src/ui/`)
User interface components and widgets:

- **`video_tile.py`**: QVideoWidget wrapper with overlay support
- **`dialogs.py`**: User interaction dialogs
- **`status_overlay.py`**: Debug information display

#### Utils Layer (`src/utils/`)
Reusable utility functions:

- **`file_utils.py`**: File I/O, path operations
- **`stream_utils.py`**: URL validation, stream parsing

#### Config Layer (`src/config/`)
Application settings and constants:

- **`settings.py`**: Centralized configuration values

### Class Structure

```python
class VideoWall:
    """
    Main orchestrator class managing the entire video wall.
    
    Attributes:
        app (QApplication): Qt application instance
        m3u8_links (list): Available stream URLs
        local_videos (list): Local video file paths
        screen (QScreen): Target display screen
        display_manager (DisplayManager): Screen management
        layout_manager (LayoutManager): Grid calculations
        video_manager (VideoManager): Content playback
    """
    
    def __init__(self, app, m3u8_links, local_videos, screen):
        """Initialize with dependency injection pattern."""
        pass
    
    def initialize_display(self):
        """Set up fullscreen window on target display."""
        pass
    
    def start_playback(self):
        """Begin video wall operation."""
        pass
```

## Import Hierarchy

### Standard Import Order
1. Standard library imports
2. Third-party imports (PyQt5, requests)
3. Local application imports

### Example:
```python
import os
import sys
import random
from typing import List, Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtMultimedia import QMediaPlayer

from src.core.video_manager import VideoManager
from src.config.settings import MAX_ACTIVE_PLAYERS
from src.utils.file_utils import get_video_files_recursively
```

## Configuration Management

### Settings Hierarchy
1. **Constants** in `src/config/settings.py` (compile-time)
2. **Command-line arguments** via argparse (runtime)
3. **Environment variables** via `os.environ` (runtime)
4. **M3U8 configuration** in `m3u8-hosts.m3u8` (runtime)

### Key Configuration Values
```python
# Display Settings
DEFAULT_GRID_ROWS = 3
DEFAULT_GRID_COLS = 3
TILE_MARGIN = 2

# Performance Settings
MAX_ACTIVE_PLAYERS = 15
VIDEO_BUFFER_SIZE = 15000  # milliseconds
LOW_LATENCY_MODE = False

# Hardware Settings
HARDWARE_DECODE_PRIORITY = ["videotoolbox", "cuda", "vaapi"]
HARDWARE_ACCEL_STRATEGY = "alternate"

# UI Settings
FULLSCREEN_MODE = True
ENABLE_TILE_ANIMATOR = True
```

## Build System

### Scripts Overview

#### `compile-build-dist.sh`
Main build orchestrator:
- Creates virtual environment
- Installs dependencies
- Runs PyInstaller
- Creates platform installers
- Generates build metadata

#### `run-python-source.sh`
Development runner:
- Activates virtual environment
- Installs dependencies if needed
- Runs from source with hot reload

#### `run-python.sh`
Production runner:
- Detects platform
- Locates appropriate binary
- Handles platform-specific launch

### Build Outputs

#### macOS
- `.app` bundle with proper Info.plist
- Code signed (if certificates available)
- DMG installer with drag-to-Applications

#### Windows
- Single `.exe` file
- Optional NSIS installer
- Embedded icon and metadata

#### Linux
- Standalone binary
- AppImage for distribution
- Desktop file for integration

## Error Handling Strategy

### Graceful Degradation
1. **Stream fails** → Try alternate stream → Fall back to local video
2. **No content** → Display status message → Keep tile visible
3. **Display disconnected** → Reconfigure layout → Continue on remaining screens

### Logging Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General application flow
- **WARNING**: Recoverable issues
- **ERROR**: Non-fatal errors requiring attention
- **CRITICAL**: Fatal errors causing shutdown

### Error Recovery
```python
try:
    player.setMedia(QMediaContent(QUrl(stream_url)))
    player.play()
except Exception as e:
    logger.error(f"Stream playback failed: {e}")
    self._fallback_to_local_video(tile_index)
```

## Testing Standards

### Test Structure
```
tests/
├── unit/           # Isolated component tests
├── integration/    # Component interaction tests
└── fixtures/       # Test data and mocks
```

### Test Naming
- Test files: `test_[module_name].py`
- Test classes: `Test[ClassName]`
- Test methods: `test_[method_name]_[scenario]`

Example:
```python
class TestVideoManager:
    def test_load_stream_valid_url(self):
        """Test loading a valid M3U8 stream."""
        pass
    
    def test_load_stream_invalid_url(self):
        """Test handling of invalid stream URLs."""
        pass
```

## Performance Guidelines

### Memory Management
- Limit simultaneous QMediaPlayer instances
- Implement tile recycling for long-running installations
- Clear unused media content explicitly

### CPU Optimization
- Use hardware acceleration when available
- Implement frame skipping for overloaded systems
- Batch UI updates using QTimer

### Network Efficiency
- Cache M3U8 playlists
- Implement exponential backoff for retries
- Use connection pooling for HTTP requests

## Security Considerations

### Input Validation
- Sanitize M3U8 URLs before parsing
- Validate file paths against directory traversal
- Limit resource consumption per stream

### Runtime Security
- No execution of external commands without validation
- Restrict file system access to user directories
- Implement rate limiting for network requests

## Version Control

### Branch Strategy
- `main`: Stable releases only
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation

### Commit Messages
Format: `[type]: [description]`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code restructuring
- `test`: Test additions/changes
- `chore`: Build/maintenance tasks

Example: `feat: Add CUDA acceleration support for Linux`

## Platform-Specific Considerations

### macOS
- Requires code signing for distribution
- Metal acceleration via VideoToolbox
- App Transport Security for HTTPS streams

### Linux
- X11/Wayland compatibility
- Package manager integration
- Video codec availability varies by distribution

### Windows
- Not officially supported but functional
- Requires Visual C++ redistributables
- Different path separators in configuration

## Development Workflow

### Setup
1. Clone repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure streams: Edit `m3u8-hosts.m3u8`

### Development Cycle
1. Make changes in feature branch
2. Test locally: `./run-python-source.sh`
3. Run tests: `pytest`
4. Build: `./compile-build-dist.sh`
5. Test binary: `./run-python.sh`
6. Create pull request

### Release Process
1. Update version in `src/config/settings.py`
2. Update CHANGELOG.md
3. Tag release: `git tag v1.0.0`
4. Build all platforms
5. Create GitHub release with artifacts

## Debugging Tools

### Built-in Debugging
- `--debug` flag enables verbose logging
- Status overlay shows performance metrics
- Log file: `videowall.log`

### Qt Debugging
```bash
export QT_LOGGING_RULES="qt.*=true"
export QT_DEBUG_PLUGINS=1
```

### Python Debugging
```python
import pdb; pdb.set_trace()  # Breakpoint
```

## Documentation Standards

### Docstring Format (Google Style)
```python
def load_stream(self, url: str, player: QMediaPlayer) -> bool:
    """
    Load an M3U8 stream into a media player.
    
    Args:
        url: The M3U8 stream URL to load
        player: Target QMediaPlayer instance
        
    Returns:
        bool: True if loading succeeded, False otherwise
        
    Raises:
        NetworkError: If stream is unreachable
        FormatError: If stream format is invalid
    """
```

### README Sections
1. Project description
2. Features
3. Requirements
4. Installation
5. Usage
6. Configuration
7. Troubleshooting
8. Contributing
9. License

## Maintenance Guidelines

### Regular Tasks
- Update dependencies monthly
- Security audit quarterly
- Performance profiling before releases
- Documentation review with major changes

### Deprecation Policy
1. Mark as deprecated with warnings
2. Provide migration path
3. Support for 2 minor versions
4. Remove in next major version

This document represents the complete structural and organizational standards for the VideoWall project. All contributions should adhere to these guidelines to maintain consistency and quality.