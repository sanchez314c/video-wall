# VideoWall Frequently Asked Questions

## General Questions

### Q: What video formats are supported?
A: VideoWall supports all formats supported by Qt Multimedia framework:
- **Common formats**: MP4, WebM, MOV, AVI, MKV
- **Codecs**: H.264, H.265, VP8, VP9
- **Streaming**: M3U8 (HLS), RTSP (limited)

Check supported formats with: `python -c "from PyQt5.QtMultimedia import QMediaPlayer; print(QMediaPlayer.supportedMimeTypes())"`

### Q: How many videos can play simultaneously?
A: The default limit is 15 active players, but practical limits depend on:
- **Hardware**: GPU capabilities and VRAM
- **Resolution**: Higher resolutions use more resources
- **Codec**: Hardware-accelerated codecs are more efficient

Typical performance:
- **Integrated graphics**: 4-6 videos at 1080p
- **Dedicated GPU**: 9+ videos at 1080p
- **Apple Silicon**: Excellent performance with hardware acceleration

### Q: Does VideoWall work on Windows?
A: Currently, VideoWall is optimized for macOS and Linux. Windows support is planned but not yet implemented. The build system and dependencies are currently Unix-focused.

## Installation and Setup

### Q: Installation fails with PyQt5 errors
A: PyQt5 installation can be tricky on some systems:

**macOS:**
```bash
# Install via Homebrew
brew install pyqt5

# Or use pip with specific version
pip install PyQt5==5.15.7
```

**Linux (Ubuntu/Debian):**
```bash
# Install system packages first
sudo apt-get install python3-pyqt5 python3-pyqt5.qtmultimedia

# Then install via pip
pip install PyQt5
```

### Q: Videos don't play, just black screens
A: This usually indicates missing multimedia codecs or plugins:

**macOS:**
- Install additional codecs: `brew install ffmpeg`
- Try with hardware acceleration: `python -m src --hwa-enabled`

**Linux:**
```bash
# Install GStreamer plugins
sudo apt-get install gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav

# Install Qt multimedia plugins
sudo apt-get install libqt5multimedia5-plugins
```

### Q: Only one monitor is detected
A: VideoWall should automatically detect all monitors. If not:

1. **Check OS detection**: Ensure all monitors show up in system display settings
2. **X11 configuration** (Linux): Check `xrandr` output
3. **Restart application**: Sometimes a restart is needed after connecting displays
4. **Check display arrangement**: Some OS configurations require specific monitor arrangements

## Performance Issues

### Q: Video playback is stuttering/lagging
A: Performance optimization tips:

1. **Enable hardware acceleration**:
   ```bash
   python -m src --hwa-enabled
   ```

2. **Reduce video count**:
   - Edit `src/config/settings.py`
   - Decrease `MAX_ACTIVE_PLAYERS`

3. **Lower video quality**:
   - Use lower resolution videos
   - Reduce bitrate in video files

4. **Check system resources**:
   - Monitor CPU and GPU usage
   - Ensure sufficient RAM

### Q: Memory usage keeps increasing
A: This can indicate a memory leak or insufficient buffer management:

1. **Reduce buffer size** in settings:
   ```python
   VIDEO_BUFFER_SIZE = 10000  # Reduce from default 15000
   ```

2. **Restart periodically** for long-running installations

3. **Check video file sizes** - very large files can consume more memory

## Streaming and M3U8

### Q: M3U8 streams not working
A: M3U8 streaming requires proper configuration:

1. **Check stream URLs**: Ensure URLs are accessible
   ```bash
   curl -I "your-stream-url.m3u8"
   ```

2. **Verify network connectivity**
3. **Check firewall/proxy settings**
4. **Test with known working streams** from `config/m3u8-hosts.m3u8`

### Q: Streams keep buffering
A: Buffering issues with streaming:

1. **Increase buffer size** in settings:
   ```python
   VIDEO_BUFFER_SIZE = 30000  # Increase to 30 seconds
   ```

2. **Check network bandwidth**
3. **Try lower quality streams** if available
4. **Consider local video fallback** for reliability

## Configuration and Customization

### Q: How do I change the layout animation speed?
A: Edit `src/config/settings.py`:
```python
ANIMATION_DURATION_MS = 4000  # 4 seconds instead of 8
```

### Q: Can I customize the layout patterns?
A: Yes! Layout patterns are defined in `src/core/layout_manager.py`. You can:
- Modify existing patterns
- Add new layout algorithms
- Change the order of animations

### Q: How do I add custom video effects?
A: Video effects can be added in `src/core/animator.py`:
1. Create new animation methods
2. Register them in the animation system
3. Add UI controls in `src/ui/dialogs.py`

## Build and Distribution

### Q: Linux build fails with Qt errors
A: Common Linux build issues:

1. **Missing Qt development packages**:
   ```bash
   sudo apt-get install qt5-default qttools5-dev-tools
   ```

2. **PyInstaller Qt plugin issues**:
   - Use the provided `VideoWall-linux.spec`
   - Ensure Qt plugins are bundled correctly

3. **Docker build issues**:
   - Check Dockerfile.linux for dependencies
   - Ensure proper Qt5 multimedia installation

### Q: macOS build creates huge app bundle
A: Optimize macOS builds:

1. **Use .spec file exclusions** to remove unnecessary files
2. **Strip debug symbols** from binaries
3. **Use UPX compression** in PyInstaller settings
4. **Exclude development dependencies**

## Troubleshooting

### Q: Application crashes on startup
A: Check these common issues:

1. **Python version compatibility** - ensure Python 3.8+
2. **Missing dependencies** - run `pip install -r requirements.txt`
3. **Display issues** - try running with `--no-hwa` flag
4. **Check logs** - look for error messages in console output

### Q: No sound from videos
A: Audio troubleshooting:

1. **Check system audio** - ensure audio works in other applications
2. **Volume settings** - VideoWall respects system volume
3. **Audio codec support** - some video formats may have unsupported audio codecs
4. **M3U8 streams** - some streams may not have audio tracks

### Q: How to debug issues?
A: Enable debug mode:
```bash
python -m src --debug
```

This provides:
- Detailed console output
- Status overlay with performance metrics
- Error messages and warnings
- Stream status information

## Getting Help

### Q: Where can I get additional support?
A: Support resources:
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed debugging
- **Community**: Join discussions in GitHub Discussions
- **Wiki**: Additional tips and community contributions

### Q: How can I contribute to VideoWall?
A: We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code contribution guidelines
- Bug reporting process
- Feature request procedures
- Development setup instructions

---

Still have questions? Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide or open an issue on GitHub.