# VideoWall Quick Start Guide

## What is VideoWall?

VideoWall is a sophisticated multi-display video wall application built with PyQt5, designed for creating hardware-accelerated video installations on macOS and Linux. The application supports both M3U8 streaming and local video playback across multiple monitors with professional-grade features and animated layouts.

## System Requirements

- **Operating System**: macOS 10.14+ or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Graphics**: Hardware acceleration support recommended
- **Memory**: 4GB RAM minimum (8GB+ recommended for multiple videos)
- **Display**: Multiple monitors supported (automatic detection)

## Installation in 5 Minutes

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/video-wall.git
cd video-wall
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python -m src
```

That's it! VideoWall will start and automatically detect all connected displays.

## First Time Setup

### Adding Video Content

1. **Local Videos**: Place video files in any accessible folder
2. **Streaming Content**: Edit `config/m3u8-hosts.m3u8` to add M3U8 stream URLs

### Basic Configuration

The default configuration works out of the box:
- **Grid Layout**: 3x3 video grid
- **Animation**: 8-second cycle between layouts
- **Hardware Acceleration**: Disabled by default (enable with `--hwa-enabled`)

## Running with Options

### Basic Usage
```bash
# Run with default settings
python -m src

# Run with hardware acceleration
python -m src --hwa-enabled

# Run with specific video folder
python -m src --video-path /path/to/videos
```

### Advanced Options
```bash
# Custom grid size
python -m src --grid-rows 2 --grid-cols 2

# Disable animations
python -m src --no-animations

# Debug mode
python -m src --debug
```

## What You'll See

1. **Multi-Span Display**: VideoWall automatically spans all connected monitors
2. **Animated Layouts**: Videos cycle through different layout patterns every 8 seconds
3. **Stream Fallback**: If M3U8 streams fail, local videos automatically play
4. **Status Overlay**: Debug information shows current status (in debug mode)

## Common First Tasks

### Add Your Own Videos
1. Copy video files to a folder (e.g., `my_videos/`)
2. Run: `python -m src --video-path my_videos/`
3. Videos will automatically load and play

### Configure Streaming
1. Open `config/m3u8-hosts.m3u8`
2. Add streaming URLs (one per line)
3. Restart VideoWall

### Adjust Layout
1. Edit `src/config/settings.py`
2. Change `DEFAULT_GRID_ROWS` and `DEFAULT_GRID_COLS`
3. Restart VideoWall

## Troubleshooting

### Videos Not Playing
- Check video format compatibility (MP4, WebM, MOV supported)
- Verify hardware acceleration drivers (if using `--hwa-enabled`)
- Check console output for error messages

### Single Monitor Only
- Ensure all monitors are connected and detected by OS
- Check display settings in system preferences
- Restart VideoWall after connecting displays

### Performance Issues
- Reduce number of simultaneous videos
- Lower video resolution/bitrate
- Enable hardware acceleration: `--hwa-enabled`

## Next Steps

- Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system understanding
- See [FAQ.md](FAQ.md) for common issues
- Review [CONFIGURATION.md](#) for advanced settings

## Need Help?

- Check the [FAQ](FAQ.md) for common solutions
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed debugging
- Open an issue on GitHub for support requests

Enjoy your VideoWall installation!