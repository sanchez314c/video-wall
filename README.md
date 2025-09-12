# VideoWall

A dynamic multi-monitor video wall application with animated layouts and real-time video playback.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

## Features

- 🎬 **Multi-Video Playback**: Display up to 9 videos simultaneously in a 3x3 grid
- 🎨 **Dynamic Layouts**: Automatic animated transitions between different layout patterns
- 🖥️ **Multi-Monitor Support**: Spans across multiple displays automatically
- 🎭 **Animation Effects**: Smooth scaling, rotation, and position animations
- 🎮 **Hardware Acceleration**: Automatic GPU acceleration support (Metal, CUDA, ROCm)
- 📁 **Local & Stream Support**: Play local video files or M3U8 streams
- ⚡ **Real-time Performance**: Optimized for smooth playback

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt5
- FFmpeg (for video codec support)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/VideoWall.git
cd VideoWall

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### System Requirements

- **macOS**: 10.14+ (Metal support)
- **Linux**: Ubuntu 18.04+ (VAAPI/VDPAU support)
- **Windows**: Windows 10+ (DirectShow support)
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Hardware video acceleration recommended

## Usage

### Basic Usage

```bash
# Run from source
python -m src

# Or run directly
python main.py
```

### Select Video Folder

1. When the application starts, a file dialog will appear
2. Select a folder containing video files (MP4, MOV, AVI, MKV supported)
3. The video wall will start with animated layouts

### Keyboard Shortcuts

- **→** (Right Arrow): Manual refresh with new layout
- **Esc**: Exit fullscreen / Quit application
- **F11**: Toggle fullscreen
- **Ctrl+Q**: Quit application

## Layout Patterns

The application randomly cycles through various layout patterns:

- **Grid**: Traditional 3x3 grid layout
- **Feature**: One large video with smaller tiles
- **Columns**: Vertical column arrangement
- **Rows**: Horizontal row arrangement
- **Spiral**: Spiral pattern animation
- **Diagonal**: Diagonal arrangement
- **Random**: Completely random positions

Layouts change automatically every 8 seconds with smooth animations.

## Configuration

Edit `src/config/settings.py` to customize:

```python
# Grid size
DEFAULT_GRID_ROWS = 3
DEFAULT_GRID_COLS = 3

# Animation timing
ANIMATION_DURATION_MS = 8000  # Layout change interval

# Performance
VIDEO_BUFFER_SIZE = 15000  # Buffer size in milliseconds
MAX_ACTIVE_PLAYERS = 15     # Maximum concurrent videos
```

## Project Structure

```
VideoWall/
├── src/
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── core/                 # Core functionality
│   │   ├── animator.py       # Animation system
│   │   ├── app.py           # Application initialization
│   │   ├── display_manager.py
│   │   ├── layout_manager.py
│   │   ├── video_loader.py
│   │   ├── video_manager.py
│   │   └── video_wall.py    # Main window
│   ├── ui/                   # User interface
│   │   ├── dialogs.py
│   │   └── video_tile.py
│   ├── utils/                # Utilities
│   │   └── file_utils.py
│   └── config/               # Configuration
│       └── settings.py
├── resources/                # Assets
│   └── icons/
├── tests/                    # Unit tests
├── docs/                     # Documentation
├── requirements.txt
├── setup.py
└── README.md
```

## Performance Tips

- Start with fewer videos if experiencing lag
- Use hardware-accelerated video codecs (H.264)
- Close other applications to free resources
- Ensure videos are locally stored (not network drives)
- Lower resolution videos (720p) perform better than 4K

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

### Code Style

```bash
# Format code
black src/

# Lint code
pylint src/
```

## Building

### Create Standalone Application

```bash
# Using PyInstaller
pyinstaller --onefile --windowed main.spec

# Output will be in dist/VideoWall
```

## Troubleshooting

### Videos Not Playing
- Ensure FFmpeg is installed
- Check video codec compatibility
- Verify file permissions

### Performance Issues
- Reduce grid size in settings
- Check GPU acceleration is enabled
- Monitor CPU/GPU usage

### Application Crashes
- Check debug.log for errors
- Verify PyQt5 installation
- Update graphics drivers

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- PyQt5 for the robust multimedia framework
- FFmpeg for video codec support
- Contributors and testers

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/yourusername/VideoWall/issues)
- Check [documentation](docs/) for detailed guides