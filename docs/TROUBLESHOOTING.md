# VideoWall Troubleshooting Guide

## Table of Contents
- [Installation Issues](#installation-issues)
- [Runtime Problems](#runtime-problems)
- [Performance Issues](#performance-issues)
- [Display and Multi-Monitor Issues](#display-and-multi-monitor-issues)
- [Streaming and Network Issues](#streaming-and-network-issues)
- [Build and Distribution Issues](#build-and-distribution-issues)
- [Debugging Techniques](#debugging-techniques)

## Installation Issues

### PyQt5 Installation Fails

#### Symptom
```
ERROR: Could not find a version that satisfies the requirement PyQt5
```

#### Solutions

**macOS:**
```bash
# Install via Homebrew (recommended)
brew install pyqt5
brew install pyqt5-sip

# Or install specific version via pip
pip install PyQt5==5.15.7 PyQt5-sip==12.9.1
```

**Linux (Ubuntu/Debian):**
```bash
# Install system packages first
sudo apt-get update
sudo apt-get install python3-pyqt5 python3-pyqt5.qtmultimedia

# Then install via pip if needed
pip install PyQt5
```

**Python Version Issues:**
```bash
# Check Python version
python --version

# If using Python 3.9+, may need specific PyQt5 version
pip install PyQt5==5.15.7
```

### Missing Multimedia Dependencies

#### Symptom
```
ModuleNotFoundError: No module named 'PyQt5.QtMultimedia'
```

#### Solutions

**macOS:**
```bash
# Install Qt multimedia
brew install pyqt5-multimedia

# Or install complete PyQt5
pip install PyQt5[QtMultimedia]
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt5.qtmultimedia
sudo apt-get install libqt5multimedia5 libqt5multimediawidgets5

# Fedora/RHEL
sudo dnf install python3-qt5-multimedia
```

### Permission Errors

#### Symptom
```
PermissionError: [Errno 13] Permission denied
```

#### Solutions
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use user install
pip install --user -r requirements.txt
```

## Runtime Problems

### Application Won't Start

#### Symptom
Application exits immediately without error message

#### Debugging Steps
```bash
# Run with verbose output
python -m src --debug

# Check Python path
python -c "import sys; print(sys.path)"

# Verify imports
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
python -c "from src.core.video_wall import VideoWall; print('VideoWall import OK')"
```

#### Common Causes
- Missing dependencies
- Incorrect Python path
- Display server issues (Linux)

### Black Screen Instead of Video

#### Symptom
Video tiles show but remain black

#### Solutions

**1. Check Video Format Support:**
```python
# Test supported formats
python -c "
from PyQt5.QtMultimedia import QMediaPlayer
print('Supported formats:', QMediaPlayer.supportedMimeTypes())
"
```

**2. Install Codecs:**
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav
```

**3. Test with Known Good Video:**
```bash
# Download test video
wget https://example.com/test-video.mp4
python -m src --video-path . --test-video test-video.mp4
```

### Audio Not Working

#### Symptom
Video plays but no audio output

#### Solutions

**1. Check System Audio:**
```bash
# macOS
osascript -e 'get volume settings'

# Linux
amixer sget Master
```

**2. Test Audio Output:**
```python
# Test Qt audio
python -c "
from PyQt5.QtMultimedia import QMediaPlayer
player = QMediaPlayer()
print('Audio available:', player.isAudioAvailable())
"
```

**3. Check Video Audio Tracks:**
```bash
# Use ffprobe to check audio tracks
ffprobe -v quiet -print_format json -show_streams your-video.mp4
```

## Performance Issues

### High CPU Usage

#### Symptom
CPU usage > 80% during video playback

#### Solutions

**1. Enable Hardware Acceleration:**
```bash
python -m src --hwa-enabled
```

**2. Reduce Video Count:**
```python
# Edit src/config/settings.py
MAX_ACTIVE_PLAYERS = 6  # Reduce from default 15
```

**3. Optimize Video Files:**
```bash
# Re-encode videos for efficiency
ffmpeg -i input.mp4 -c:v libx264 -preset fast -crf 23 output.mp4
```

### Memory Leaks

#### Symptom
Memory usage continuously increases over time

#### Debugging
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python | grep video-wall'

# Check with Python memory profiler
pip install memory-profiler
python -m memory_profiler src/main.py
```

#### Solutions

**1. Reduce Buffer Size:**
```python
# Edit src/config/settings.py
VIDEO_BUFFER_SIZE = 8000  # Reduce from 15000
```

**2. Enable Garbage Collection:**
```python
# Add to main.py
import gc
gc.collect()  # Call periodically
```

### Stuttering Playback

#### Symptom
Video playback is choppy or freezes

#### Solutions

**1. Check System Resources:**
```bash
# macOS
top -o cpu -o mem

# Linux
htop
```

**2. Optimize Video Settings:**
```python
# Edit src/config/settings.py
VIDEO_BUFFER_SIZE = 20000  # Increase buffer
ANIMATION_DURATION_MS = 10000  # Reduce animation frequency
```

**3. Use Hardware Acceleration:**
```bash
python -m src --hwa-enabled
```

## Display and Multi-Monitor Issues

### Only One Monitor Detected

#### Symptom
VideoWall only uses primary monitor

#### Debugging
```bash
# Check detected displays
python -c "
from PyQt5.QtWidgets import QApplication
app = QApplication([])
print('Screens:', app.screens())
for i, screen in enumerate(app.screens()):
    print(f'Screen {i}: {screen.size()}')
"
```

#### Solutions

**1. Check OS Display Settings:**
- Ensure all monitors are connected and recognized
- Check display arrangement in system preferences
- Try disconnecting and reconnecting monitors

**2. X11 Configuration (Linux):**
```bash
# Check Xrandr output
xrandr

# Force display detection
xrandr --auto
```

**3. Restart Application:**
Sometimes a restart is needed after display changes

### Incorrect Display Resolution

#### Symptom
Videos appear blurry or wrong size

#### Solutions

**1. Check Display DPI:**
```python
# Test display DPI
python -c "
from PyQt5.QtWidgets import QApplication
app = QApplication([])
screen = app.primaryScreen()
print('DPI:', screen.logicalDotsPerInch())
print('Physical DPI:', screen.physicalDotsPerInch())
"
```

**2. Enable High DPI Support:**
```python
# Add to main.py before QApplication creation
import os
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
```

## Streaming and Network Issues

### M3U8 Streams Not Loading

#### Symptom
Streaming videos show as black or error

#### Debugging
```bash
# Test stream URL
curl -I "your-stream-url.m3u8"

# Test with VLC or other player
vlc "your-stream-url.m3u8"
```

#### Solutions

**1. Check Network Connectivity:**
```bash
# Test network
ping 8.8.8.8

# Check DNS
nslookup streaming-server.com
```

**2. Verify Stream Format:**
```bash
# Check M3U8 content
curl "your-stream-url.m3u8"

# Should contain .ts file URLs
```

**3. Configure Stream Timeout:**
```python
# Edit src/config/settings.py
STREAM_TIMEOUT_MS = 10000  # Increase timeout
```

### Stream Buffering Issues

#### Symptom
Streams constantly buffer or pause

#### Solutions

**1. Increase Buffer Size:**
```python
# Edit src/config/settings.py
VIDEO_BUFFER_SIZE = 30000  # 30 seconds
```

**2. Check Bandwidth:**
```bash
# Test network speed
speedtest-cli

# Or use curl for simple test
curl -o /dev/null http://speedtest.net/10mb.zip
```

**3. Use Local Fallback:**
Configure local videos as fallback in `config/m3u8-hosts.m3u8`

## Build and Distribution Issues

### PyInstaller Build Fails

#### Symptom
```
ModuleNotFoundError: No module named 'PyQt5.sip'
```

#### Solutions

**1. Install Missing Dependencies:**
```bash
pip install PyQt5-sip
```

**2. Use Provided Spec Files:**
```bash
# Linux
pyinstaller VideoWall-linux.spec --clean --noconfirm

# macOS
pyinstaller VideoWall.spec --clean --noconfirm
```

**3. Check Hidden Imports:**
Ensure spec file includes all necessary hidden imports for PyQt5

### Linux Build Qt Plugin Issues

#### Symptom
Application crashes with Qt plugin errors

#### Solutions

**1. Bundle Qt Plugins:**
```python
# In spec file, add:
datas=[
    ('/path/to/qt/plugins', 'qt/plugins'),
]
```

**2. Set Qt Plugin Path:**
```python
# Add to main.py
import os
os.environ['QT_PLUGIN_PATH'] = 'qt/plugins'
```

### Docker Build Issues

#### Symptom
Qt dependencies missing in Docker container

#### Solutions

**1. Use Provided Dockerfile:**
```bash
docker build -f Dockerfile.linux -t videowall .
```

**2. Install Qt Dependencies:**
```dockerfile
RUN apt-get update && apt-get install -y \
    libqt5multimedia5 \
    libqt5multimediawidgets5 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a
```

## Debugging Techniques

### Enable Debug Mode
```bash
python -m src --debug
```

This provides:
- Detailed console logging
- Status overlay with performance metrics
- Error messages and warnings
- Stream status information

### Check Logs
```bash
# Monitor log file in real-time
tail -f video_wall.log

# Search for errors
grep -i error video_wall.log
```

### Profile Performance
```python
# Add profiling to main.py
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... application code ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Test Individual Components
```python
# Test video loading
python -c "
from src.core.video_loader import VideoLoader
loader = VideoLoader()
videos = loader.load_videos('/path/to/videos')
print(f'Loaded {len(videos)} videos')
"

# Test display detection
python -c "
from src.core.display_manager import DisplayManager
dm = DisplayManager()
print(f'Detected {len(dm.get_displays())} displays')
"
```

### Network Debugging
```bash
# Monitor network traffic
tcpdump -i any port 80 or port 443

# Test DNS resolution
nslookup streaming-server.com

# Check firewall rules
sudo iptables -L
```

## Getting Additional Help

### Collect Debug Information
```bash
# Create debug report
python -m src --debug > debug.log 2>&1

# Include system information
uname -a > system-info.txt
python --version >> system-info.txt
pip list >> system-info.txt
```

### Submit Bug Report
When reporting issues, include:
1. Operating system and version
2. Python version
3. PyQt5 version
4. Complete error messages
5. Steps to reproduce
6. Debug logs (if available)

### Community Support
- GitHub Issues: For bug reports and feature requests
- GitHub Discussions: For questions and community support
- Wiki: Additional troubleshooting tips from community

---

For additional help, see the [FAQ.md](FAQ.md) or open an issue on GitHub.