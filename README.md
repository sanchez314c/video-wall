# VideoWall

A sophisticated multi-display video wall application built with PyQt5, designed for creating hardware-accelerated video installations on macOS and Linux. The application supports both M3U8 streaming and local video playback across multiple monitors with professional-grade features and animated layouts.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)

## ✨ Features

- 🎬 **Multi-Video Playback**: Display up to 15 simultaneous videos with hardware acceleration
- 🖥️ **Multi-Monitor Support**: Automatic detection and spanning across all connected displays
- 🎨 **Dynamic Layouts**: Smooth animated transitions between professional layout patterns
- 🌐 **Streaming Support**: M3U8/HLS streaming with automatic local fallback
- 🎭 **Animation System**: Professional transitions with configurable timing
- ⚡ **Hardware Acceleration**: Metal (macOS), VAAPI/VDPAU (Linux) support
- 📊 **Real-time Monitoring**: Stream health tracking and performance metrics
- 🔧 **Professional Configuration**: Extensive customization options

## 🚀 Quick Start

### Prerequisites
- **Operating System**: macOS 10.14+ or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Graphics**: Hardware acceleration support recommended
- **Memory**: 4GB RAM minimum (8GB+ recommended)

### Installation in 5 Minutes

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/video-wall.git
cd video-wall

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python -m src
```

That's it! VideoWall will start and automatically detect all connected displays.

### First Time Setup

1. **Add Videos**: Place video files in any accessible folder or configure M3U8 streams in `config/m3u8-hosts.m3u8`
2. **Run Application**: `python -m src`
3. **Enjoy**: Videos will automatically load and play with animated layouts

## 📖 Documentation

### For New Users
- **[Quick Start Guide](docs/QUICK_START.md)** - Get running in 5 minutes
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[FAQ](docs/FAQ.md)** - Common questions and solutions

### For Developers
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Development Guide](docs/DEVELOPMENT.md)** - Development setup and workflow
- **[API Documentation](docs/API.md)** - Integration and extension guide

### For Operations
- **[Build & Compile](docs/BUILD_COMPILE.md)** - Build system and distribution
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment strategies
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Debugging and problem resolution

### Complete Documentation Index
See **[docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)** for a complete list of all documentation.

## 🎮 Usage

### Basic Commands

```bash
# Run with default settings
python -m src

# Run with hardware acceleration
python -m src --hwa-enabled

# Run with specific video folder
python -m src --video-path /path/to/videos

# Custom grid size
python -m src --grid-rows 2 --grid-cols 2

# Debug mode with status overlay
python -m src --debug
```

### Keyboard Shortcuts

- **→** (Right Arrow): Manual refresh with new layout
- **Esc**: Exit fullscreen / Quit application
- **F11**: Toggle fullscreen
- **Ctrl+Q**: Quit application
- **D**: Toggle debug overlay (when in debug mode)

## 🎨 Layout Patterns

VideoWall features professional layout animations that cycle every 8 seconds:

- **Grid Layout**: Traditional 3x3 video grid
- **Feature Layout**: One large video with smaller tiles
- **Columns**: Vertical column arrangements
- **Rows**: Horizontal row arrangements
- **Spiral**: Spiral pattern animations
- **Diagonal**: Diagonal arrangements
- **Random**: Dynamic positioning with smooth transitions

## ⚙️ Configuration

### Basic Configuration

Edit `src/config/settings.py`:

```python
# Grid size
DEFAULT_GRID_ROWS = 3
DEFAULT_GRID_COLS = 3

# Animation timing
ANIMATION_DURATION_MS = 8000  # Layout change interval

# Performance settings
VIDEO_BUFFER_SIZE = 15000  # Buffer size in milliseconds
MAX_ACTIVE_PLAYERS = 15     # Maximum concurrent videos
```

### Streaming Configuration

Edit `config/m3u8-hosts.m3u8`:
```
# Add streaming URLs (one per line)
https://example.com/stream1.m3u8
https://example.com/stream2.m3u8
```

## 🏗️ Project Structure

```
video-wall/
├── src/                    # Source code
│   ├── core/              # Core application logic
│   ├── ui/                # User interface components
│   ├── utils/             # Utility functions
│   └── config/            # Configuration modules
├── docs/                  # Comprehensive documentation
├── scripts/               # Build and utility scripts
├── config/                # Configuration files
├── build_resources/       # Build assets (icons, etc.)
└── tests/                 # Test suite
```

## 🚀 Performance Tips

### Optimize Video Playback
- Enable hardware acceleration: `python -m src --hwa-enabled`
- Use H.264 encoded videos for best compatibility
- Lower video resolution (720p) for better performance
- Store videos locally (not network drives)

### System Optimization
- Close unnecessary applications
- Ensure sufficient RAM (8GB+ recommended)
- Update graphics drivers
- Use SSD storage for video files

## 🛠️ Development

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black src/
isort src/

# Linting
pylint src/
```

### Build Application

```bash
# macOS
pyinstaller VideoWall.spec --clean --noconfirm

# Linux
bash build-linux.sh

# Docker build
docker build -f Dockerfile.linux -t videowall .
```

## 🤝 Contributing

We welcome contributions! See **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** for guidelines.

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt5** for robust multimedia framework
- **Qt Community** for excellent documentation and tools
- **FFmpeg** for video codec support
- **Contributors** and testers who help improve VideoWall

## 📞 Support

For issues and questions:

- 🐛 **Bug Reports**: [Open an issue](https://github.com/yourusername/video-wall/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/video-wall/discussions)
- 📚 **Documentation**: [Complete docs](docs/)
- 🚀 **Quick Help**: [FAQ](docs/FAQ.md)

---

**VideoWall** - Professional video wall solutions for digital signage, exhibitions, and installations.