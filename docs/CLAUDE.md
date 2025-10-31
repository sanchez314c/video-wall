# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VideoWall is a sophisticated multi-display video wall application built with PyQt5, designed for creating hardware-accelerated video installations on macOS and Linux. The project supports both M3U8 streaming and local video playback across multiple monitors with professional-grade features.

## Architecture

### Core Components

The application follows a modular architecture with clear separation of concerns:

- **`src/core/`** - Core application logic
  - `app.py` - Main application entry point and Qt application setup
  - `video_wall.py` - Central video wall management and coordination
  - `video_manager.py` - Video playback and stream management
  - `display_manager.py` - Multi-monitor detection and configuration
  - `layout_manager.py` - Grid layout and tile positioning logic
  - `stream_tracker.py` - M3U8 stream monitoring and fallback handling
  - `animator.py` - Animation and transition effects
  - `video_loader.py` - Video file loading and caching

- **`src/ui/`** - User interface components
  - `video_tile.py` - Individual video tile widget implementation
  - `dialogs.py` - Configuration and settings dialogs
  - `status_overlay.py` - Status display and debugging overlay

- **`src/utils/`** - Utility functions
  - `stream_utils.py` - M3U8 parsing and stream handling
  - `file_utils.py` - File system operations and path management

- **`src/config/`** - Configuration management
  - `settings.py` - Application settings and preferences

- **`legacy/`** - Previous implementations and experiments (reference only, not part of main application)

### Key Design Patterns

1. **Observer Pattern**: Used for stream status updates and display changes
2. **Factory Pattern**: Video tile creation based on content type
3. **Strategy Pattern**: Different playback strategies for local vs streaming content
4. **Singleton Pattern**: Display manager and configuration manager

## Development Commands

### Setup and Installation

```bash
# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running the Application

```bash
# Run from source
python -m src

# Or using the installed command (after pip install -e .)
videowall

# Run with debug output
python -m src --debug

# Run with specific configuration
python -m src --config config.json
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_video_manager.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Sort imports
isort src/ tests/

# Run linting
flake8 src/ tests/

# Type checking (if mypy is configured)
mypy src/
```

### Building

```bash
# Build macOS app (on macOS only)
python scripts/setup.py py2app

# Build distribution packages
python -m build

# Create source distribution
python setup.py sdist

# Create wheel distribution
python setup.py bdist_wheel
```

## Key Technical Considerations

### PyQt5 Video Handling

- The application uses `QMediaPlayer` and `QVideoWidget` for video playback
- Hardware acceleration is enabled through Qt's multimedia framework
- Each video tile runs in its own widget to prevent blocking

### Multi-Monitor Support

- Uses `QDesktopWidget` to detect available screens
- Maintains screen geometry mappings for proper positioning
- Handles dynamic display connection/disconnection

### M3U8 Streaming

- Parses M3U8 playlists to extract stream URLs
- Implements automatic fallback to local content on stream failure
- Uses `requests` library for HTTP operations with proper timeout handling

### Performance Optimization

- Video tiles are only created for visible content
- Implements lazy loading for local video files
- Uses Qt's signal/slot mechanism for efficient event handling
- Memory management through proper widget cleanup

### Error Handling

- Comprehensive try/catch blocks around media operations
- Fallback mechanisms for stream failures
- Logging system for debugging (check `video_wall.log`)

## Common Development Tasks

### Adding a New Video Effect

1. Create new effect class in `src/core/animator.py`
2. Register effect in `EffectRegistry`
3. Add UI controls in `src/ui/dialogs.py`
4. Update configuration schema in `src/config/settings.py`

### Supporting a New Video Format

1. Check Qt's supported formats via `QMediaPlayer.supportedMimeTypes()`
2. Add format validation in `src/utils/file_utils.py`
3. Update file filters in `src/ui/dialogs.py`

### Implementing Custom Layout

1. Extend `LayoutManager` in `src/core/layout_manager.py`
2. Implement `calculate_positions()` method
3. Add layout option to UI in `src/ui/dialogs.py`

### Adding Network Control

1. Implement REST API endpoints in new `src/api/` module
2. Use Qt's network classes (`QTcpServer`, `QTcpSocket`)
3. Add authentication and security measures

## Project-Specific Conventions

### File Naming

- Python files use `snake_case.py`
- Resource files in `src/resources/`
- Icons in `src/resources/icons/`
- Styles in `src/resources/styles/`

### Code Style

- Follow PEP 8 with 100 character line limit (configured in pyproject.toml)
- Use type hints where beneficial
- Docstrings for all public methods and classes

### Git Workflow

- Main branch for stable releases
- Feature branches for new development
- Legacy code preserved in `legacy/` for reference

### Configuration Files

- User settings stored in `~/.videowall/config.json`
- Default settings in `src/config/settings.py`
- Environment variables supported via `.env` file

## Debugging Tips

### Common Issues

1. **Black screen on video tile**: Check video format compatibility and file path
2. **Stream not playing**: Verify M3U8 URL accessibility and network connection
3. **Layout issues**: Check display detection in Display Manager
4. **Performance problems**: Reduce number of simultaneous streams or lower resolution

### Debug Mode

Run with `--debug` flag to enable:
- Verbose logging to console and file
- Status overlay showing FPS and resource usage
- Test pattern generation for display verification

### Log Files

- Application log: `video_wall.log` in project root
- Qt debug output: Set `QT_LOGGING_RULES="qt.*=true"`

## Dependencies and Requirements

### Core Dependencies

- **PyQt5**: Main UI framework (>= 5.15.0)
- **requests**: HTTP operations for streaming (>= 2.25.0)
- **Python**: Version 3.7 or higher

### Development Dependencies

- **pytest**: Testing framework (>= 6.0.0)
- **pytest-qt**: Qt testing utilities (>= 3.3.0)
- **black**: Code formatting (>= 20.8b1)
- **flake8**: Linting (>= 3.8.0)
- **isort**: Import sorting (>= 5.7.0)

### Platform-Specific

- **macOS**: py2app for building .app bundles
- **Linux**: Ensure Qt multimedia plugins are installed
- **Windows**: Not officially supported but may work with modifications

## Performance Considerations

- Each video tile consumes ~50-100MB RAM depending on resolution
- GPU acceleration significantly reduces CPU usage
- Network streams require stable bandwidth (5-10 Mbps per HD stream)
- Recommended maximum: 9 tiles for 1080p content on modern hardware

## Security Notes

- M3U8 URLs are fetched without authentication by default
- No DRM support currently implemented
- Local file access restricted to user-accessible paths
- Consider network isolation for public installations