# Setup Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8+ | 3.10+ recommended |
| PyQt5 | 5.15+ | Includes Qt Multimedia |
| GStreamer 1.0 | Any recent | Linux only, system package |
| ffmpeg | Any | Optional, for screen recording only |

No virtual environment is required but recommended. Conda works fine too.

## Linux Setup

### 1. Install System Dependencies

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install \
  python3 python3-pip python3-venv \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav \
  ffmpeg

# Fedora / RHEL
sudo dnf install python3 python3-pip gstreamer1-plugins-base gstreamer1-plugins-good ffmpeg
```

GStreamer is required on Linux. Without it, Qt's multimedia backend can't decode H.264 or HLS streams — videos will get stuck on "Loading".

### 2. Clone and Install Python Packages

```bash
git clone https://github.com/sanchez314c/video-wall.git
cd video-wall
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run

```bash
./run-source-linux.sh
# or
python -m src.core.app
```

### 4. (Optional) Build Standalone Binary

```bash
pip install pyinstaller
pyinstaller VideoWall.spec --clean --noconfirm
# Binary: dist/VideoWall/VideoWall
```

To install system-wide:
```bash
sudo cp -r dist/VideoWall /opt/VideoWall
sudo ln -s /opt/VideoWall/VideoWall /usr/local/bin/videowall
```

Desktop launcher entry (save to `/usr/share/applications/videowall.desktop`):
```ini
[Desktop Entry]
Name=VideoWall
Exec=/usr/local/bin/videowall
Icon=/opt/VideoWall/_internal/resources/icons/icon.png
Type=Application
Categories=Video;
```

## macOS Setup

### 1. Install Python

```bash
brew install python3
```

### 2. Clone and Install

```bash
git clone https://github.com/sanchez314c/video-wall.git
cd video-wall
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run

```bash
./run-source-macos.sh
# or
python -m src.core.app
```

GStreamer is not required on macOS — Qt uses AVFoundation/Metal as the media backend.

## Conda Setup (Alternative)

```bash
conda create -n video-wall python=3.10
conda activate video-wall
pip install -r requirements.txt
python -m src.core.app
```

If PyQt5 imports fail inside conda, try:
```bash
pip install --force-reinstall PyQt5 PyQt5-Qt5 PyQt5-sip
```

## Stream Configuration

Edit `m3u8-hosts.m3u8` in the project root before launching:

```
# Lines starting with # are comments and are ignored
https://your-server.com/stream1/index.m3u8
https://your-server.com/stream2/index.m3u8
rtsp://... # RTSP URLs work too if Qt backend supports them
```

The app loads this file at startup. URLs must be HTTP/HTTPS or a protocol supported by your Qt media backend. Lines without a protocol prefix get `https://` prepended automatically.

## Environment Variables

| Variable | Values | Description |
|---|---|---|
| `VIDEOWALL_HWA_ENABLED` | `0` or `1` | Set by `--hwa-enabled` flag. Logs HWA status. |
| `QT_QPA_PLATFORM` | `xcb`, `wayland` | Qt platform plugin. Defaults to `xcb` on Linux. |
| `GST_PLUGIN_SYSTEM_PATH` | path(s) | GStreamer plugin search paths. Auto-set on Linux if not present. |
| `DISPLAY` | `:0`, etc. | Required for screen recording (x11grab). |

## CLI Arguments

```
python -m src.core.app [options]

Options:
  --hwa-enabled    Enable hardware acceleration hint for Qt multimedia backend
```

All other arguments are passed through to `QApplication`.

## Troubleshooting

### Videos stuck on "Loading" (Linux packaged binary)

The binary can't find GStreamer plugins. Verify the plugins are installed:

```bash
gst-inspect-1.0 playbin
gst-inspect-1.0 h264parse
```

If those fail, install the missing packages (see step 1 above). The app auto-sets `GST_PLUGIN_SYSTEM_PATH` on startup for common paths — check console output for `[VideoWall] Set GST_PLUGIN_SYSTEM_PATH:` to confirm.

### PyQt5 import fails

```bash
# Check installation
python3 -c "import PyQt5; print(PyQt5.__version__)"

# Reinstall if broken
pip install --force-reinstall PyQt5 PyQt5-Qt5 PyQt5-sip
```

### No displays detected / wrong monitor count

The app reads `QApplication.screens()` after `QApplication` is created. Plug in all monitors and set them active in display settings before launching. Monitors hot-plugged after launch are not detected.

### Screen recording produces no file

Check that `ffmpeg` is on PATH:
```bash
which ffmpeg
ffmpeg -version
```

Also confirm `DISPLAY` is set:
```bash
echo $DISPLAY
```

Screen recording uses x11grab which only works on X11, not Wayland. If you're on Wayland, switch to X11 session or record using a different tool.

### App crashes on launch (Electron sandbox error)

On some Linux setups:
```bash
sudo sysctl -w kernel.unprivileged_userns_clone=1
```

Or launch with the sandbox disabled if running the packaged binary:
```bash
/opt/VideoWall/VideoWall --no-sandbox
```

### Streams all fail / fall back to local video immediately

Common causes:
1. Stream URLs in `m3u8-hosts.m3u8` are offline or require auth
2. Network proxy blocking HLS segments
3. `VIDEO_LOADING_TIMEOUT_MS` too short for slow connections — increase it in `settings.py`

Run with the "Skip Stream Testing" checkbox unchecked in the startup dialog to see detailed stream validation output in console.
