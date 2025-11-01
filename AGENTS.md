# AGENTS.md

This file provides guidance to AI assistants (Claude Code, GitHub Copilot, etc.) when working with code in this repository.

## Project Overview

VideoWall is a sophisticated multi-display video wall application built with PyQt5, designed for creating hardware-accelerated video installations on macOS and Linux. The application supports both M3U8 streaming and local video playback across multiple monitors with professional-grade features and animated layouts.

## Development Commands

### Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode (optional)
pip install -e .
```

### Running the Application

```bash
# Run from source (recommended for development)
python -m src

# Run directly
python src/main.py

# Run with hardware acceleration flag
python -m src --hwa-enabled

# Alternative run scripts
./run-source-macos.sh    # macOS specific
./run-source-linux.sh    # Linux specific
```

### Building for Distribution

```bash
# Build for Linux (using Docker on macOS/Linux)
bash build-linux.sh

# Build for Linux (Alpine - smaller image)
bash build-linux-alpine.sh

# Manual Linux build (native Linux system)
pyinstaller VideoWall-linux.spec --clean --noconfirm

# Create Linux package
bash create-linux-package.sh

# Build for macOS (using PyInstaller)
pyinstaller VideoWall.spec --clean --noconfirm

# Build for macOS ARM64 (Apple Silicon)
pyinstaller VideoWall-arm64.spec --clean --noconfirm
```

### Testing and Quality

```bash
# Run tests (when test suite is implemented)
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Code formatting (if tools are configured)
black src/
isort src/

# Linting (if configured)
flake8 src/
```

## Architecture Overview

### Core Application Structure

The application follows a modular PyQt5 architecture with clear separation of concerns:

**Main Entry Points:**
- `src/main.py` - Direct execution entry point
- `src/__main__.py` - Module execution entry point (`python -m src`)
- `src/core/app.py` - Application initialization and argument parsing

**Core Components:**
- **`src/core/video_wall.py`** - Main application window and central coordinator
- **`src/core/video_manager.py`** - Multi-video playback coordination and management
- **`src/core/display_manager.py`** - Multi-monitor detection and configuration
- **`src/core/layout_manager.py`** - Dynamic grid layout and positioning logic
- **`src/core/animator.py`** - Smooth animation and transition effects
- **`src/core/video_loader.py`** - Video file loading and caching system
- **`src/core/stream_tracker.py`** - M3U8 stream monitoring with fallback handling

**UI Components:**
- **`src/ui/video_tile.py`** - Individual video tile widget implementation
- **`src/ui/dialogs.py`** - File selection and configuration dialogs
- **`src/ui/status_overlay.py`** - Debug status display overlay

**Utilities:**
- **`src/utils/file_utils.py`** - File system operations and video file discovery
- **`src/utils/stream_utils.py`** - M3U8 playlist parsing and stream handling

**Configuration:**
- **`src/config/settings.py`** - Application settings and constants
- **`config/m3u8-hosts.m3u8`** - M3U8 stream URLs configuration

### Key Design Patterns

1. **Observer Pattern**: Stream status updates and display change notifications
2. **Factory Pattern**: Video tile creation based on content type (local vs streaming)
3. **Strategy Pattern**: Different playback strategies for local files vs M3U8 streams
4. **Singleton Pattern**: Display manager and configuration manager instances

### Video Playback Architecture

- **Hardware Acceleration**: Optional GPU acceleration via `--hwa-enabled` flag
- **Multi-Player Management**: Up to 9 simultaneous video players in 3x3 grid
- **Stream Fallback**: Automatic switching between M3U8 streams and local content
- **Buffer Management**: Configurable video buffer size (default 15000ms)

### Layout Animation System

The application features dynamic layout transitions that cycle every 8 seconds:
- Grid layout (traditional 3x3)
- Feature layout (one large video with smaller tiles)
- Columns and rows arrangements
- Spiral and diagonal patterns
- Random positioning with smooth animations

## Platform-Specific Considerations

### macOS
- Retina display support with high-DPI scaling
- Metal framework integration for hardware acceleration
- Native .app bundle creation with py2app
- Icon path: `build_resources/icons/icon.icns`

### Linux
- GStreamer multimedia framework integration
- VAAPI/VDPAU hardware acceleration support
- Docker-based cross-platform building
- Qt5 plugin bundling for multimedia codecs
- Icon path: `build_resources/icons/icon.png`

### Dependencies by Platform

**Common:**
- Python 3.8+
- PyQt5 >= 5.15.0
- requests >= 2.25.0

**Linux-specific:**
```bash
# System packages required
sudo apt-get install libqt5multimedia5 libqt5multimediawidgets5 \
    libqt5widgets5 libqt5gui5 libqt5core5a libqt5network5
```

## Configuration Files

### Application Settings
- Grid size: `DEFAULT_GRID_ROWS = 3`, `DEFAULT_GRID_COLS = 3`
- Animation timing: `ANIMATION_DURATION_MS = 8000`
- Video buffer: `VIDEO_BUFFER_SIZE = 15000`
- Max players: `MAX_ACTIVE_PLAYERS = 15`

### M3U8 Stream Configuration
- Location: `config/m3u8-hosts.m3u8`
- Format: One URL per line
- Automatic fallback to local content on stream failure

## Build System Details

### PyInstaller Configuration
- **Spec files**: Platform-specific (VideoWall.spec, VideoWall-linux.spec, VideoWall-arm64.spec)
- **Hidden imports**: Comprehensive PyQt5 module inclusion
- **Data files**: M3U8 configuration and icon resources
- **Runtime hooks**: Qt plugin path configuration

### Docker Building
- **Base images**: Python 3.11 slim (Debian) or Alpine
- **Qt dependencies**: Full PyQt5 multimedia stack
- **Output**: Standalone Linux executable in `dist/Linux/`

## Common Development Tasks

### Adding New Video Effects
1. Implement effect in `src/core/animator.py`
2. Register in animation system
3. Add UI controls in `src/ui/dialogs.py`

### Supporting New Video Formats
1. Verify Qt multimedia support via `QMediaPlayer.supportedMimeTypes()`
2. Add format validation in `src/utils/file_utils.py`
3. Update file filters in dialogs

### Debugging Video Playback Issues
1. Check Qt multimedia plugin installation
2. Verify hardware acceleration drivers
3. Test with known-good video files
4. Check `video_wall.log` for error messages

### Performance Optimization
1. Limit concurrent streams based on hardware capabilities
2. Optimize video resolution and bitrate
3. Use hardware acceleration when available
4. Monitor memory usage with multiple videos

## Important Notes

- The `run-source-linux.sh` script appears to be for an Electron-based application and may be outdated
- Build scripts create timestamped backups automatically before editing
- All file edits should follow the backup policy (create timestamped backups)
- The application handles both local video files and M3U8 streaming sources
- Multi-monitor support is automatic - the application spans all available displays