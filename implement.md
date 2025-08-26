# Video Wall — Implementation Notes

## Current State (as of 2026-03-14)

The project is a fully functional, production-ready video wall application. It has been built, tested, and deployed as a system binary on Linux.

### What's Built and Working

- Multi-monitor video wall (one fullscreen window per display)
- M3U8/HLS stream playback via Qt Multimedia + GStreamer backend
- Local video fallback when streams fail or time out
- 6 dynamic layout patterns with automatic cycling (5-30s intervals)
- Smooth tile geometry animations via `QPropertyAnimation`
- Stream health monitoring with 30-second check interval
- 15-second per-tile loading timeout with automatic retry/fallback logic
- Screen recording via ffmpeg x11grab (R key toggle, saves to Desktop)
- Dark Neo Glass UI theme — centralized token system in `theme.py`
- Frameless config dialog with custom drag titlebar
- PyInstaller binary build for Linux (`dist/VideoWall/VideoWall`)
- GStreamer plugin path auto-detection for packaged binaries
- System install at `/opt/VideoWall/` with symlink at `/usr/local/bin/videowall`
- Ubuntu `.desktop` file for app launcher integration

### Deployment

- Binary: `/opt/VideoWall/VideoWall`
- Symlink: `/usr/local/bin/videowall`
- Version: 1.6.4
- Built with: Python 3.10, PyQt5 5.15.11, conda environment `video-wall`

---

## Ideas / Future Enhancements

- Audio routing — currently all players are muted. Could add an option to unmute one tile at a time (the "featured" tile)
- Wayland support — screen recording is x11grab only. Needs a pipewire/wlr-screencopy alternative
- Web-based remote control — HTTP endpoint to trigger layout changes or swap specific streams without restarting
- Dynamic stream playlist reload — watch `m3u8-hosts.m3u8` for changes and reload without restart
- Per-tile stream pinning — ability to lock specific streams to specific tile positions
- Stream source categories — group streams by type/topic and allow layout patterns to cluster related streams
- GPU acceleration metrics — expose current HWA status and decode performance in the debug overlay
- Configuration file support — move runtime settings (grid size, intervals) out of `settings.py` into a JSON/TOML config the user can edit without touching source
- Windows build — the spec file exists (`VideoWall.spec`) and the code is theoretically cross-platform, but it hasn't been validated on Windows
