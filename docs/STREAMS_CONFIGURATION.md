# VideoWall Stream Configuration Guide

## How to Set Video M3U8 Streams

The VideoWall application supports both M3U8 streams and local video files.

### Method 1: M3U8 Streams File (Recommended)

1. **Edit the streams file**: Open `m3u8-hosts.m3u8` in any text editor
2. **Add your stream URLs**: Add one URL per line
   ```
   https://stream1.example.com/live/playlist.m3u8
   https://stream2.example.com/live/playlist.m3u8
   http://192.168.1.100:8080/camera.m3u8
   ```
3. **Save the file**: The app will automatically load these streams on startup

#### Supported Stream Formats:
- HLS streams (.m3u8)
- HTTP/HTTPS URLs
- Local network streams
- IP camera streams

#### Example Stream Sources:
- **Test Stream**: `https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8`
- **IP Cameras**: Most modern IP cameras support RTSP or HLS streaming
- **Live TV**: Many IPTV services provide M3U8 URLs
- **Security Systems**: NVR systems often provide M3U8 endpoints

### Method 2: Local Video Files

When the app starts, you'll see a configuration dialog where you can:
1. Choose a folder containing video files
2. Enable/disable local video playback
3. The app will scan for: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`, `.3gp`

### Method 3: Mixed Mode

The app can use both streams and local videos simultaneously:
- Streams will be prioritized for tiles when available
- Local videos act as fallback content
- If a stream fails, it automatically switches to local video

## Running the Application

### With default settings (CPU only):
```bash
./run-python.sh
```

### With hardware acceleration:
```bash
./run-python.sh --hwa-enabled
```

### From source:
```bash
./run-python-source.sh
# or with hardware acceleration
./run-python-source.sh --hwa-enabled
```

## Troubleshooting Streams

### Stream Not Playing?
1. **Check URL format**: Ensure it's a valid M3U8 URL
2. **Test in browser**: Try opening the M3U8 URL in Safari or VLC
3. **Check network**: Ensure the stream source is accessible
4. **Firewall/Security**: Some streams require authentication or have CORS restrictions

### Performance Issues?
- Try CPU-only mode first (default)
- Reduce the number of simultaneous streams
- Use local videos for better performance
- Check your network bandwidth

### Common Stream Sources

#### Free Test Streams:
- Mux Test Stream: `https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8`
- Big Buck Bunny: `https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8`

#### Getting Streams from IP Cameras:
Most IP cameras provide RTSP URLs that need conversion to HLS/M3U8:
1. Find your camera's RTSP URL (check manufacturer docs)
2. Use FFmpeg to convert RTSP to HLS
3. Or use camera software that provides M3U8 endpoints

## File Structure
```
VideoWall/
├── m3u8-hosts.m3u8             # Your stream URLs go here
├── assets/                      # App icons
├── src/                         # Source code
└── dist/                        # Compiled applications
```

## Notes
- The app randomly selects streams for each tile
- Failed streams automatically retry with different URLs
- Local videos are used as fallback when streams fail
- The tile animator creates dynamic layouts that change periodically