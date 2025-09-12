# Installation Guide

## System Requirements

- **Operating System**: macOS 10.15+ (Catalina or later)
- **Python**: 3.7 or newer
- **Display**: At least one monitor, multiple monitors recommended
- **Hardware**: Recommended minimum 2.0 GHz dual-core processor, 4GB RAM
- **Network**: Broadband internet connection for streaming (optional)

## Installation Methods

### 1. macOS App (Recommended)

1. Download the latest release from the [Releases page](https://github.com/yourusername/videowall/releases)
2. Open the DMG file
3. Drag VideoWall to your Applications folder
4. Launch from Applications or Spotlight

### 2. From Source

#### Prerequisites

Install Python 3.7+ if not already installed:
```bash
# Using Homebrew
brew install python
```

#### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/videowall.git
cd videowall
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

### 3. Using pip

```bash
pip install videowall
```

## Running VideoWall

### From macOS App
Simply click the VideoWall icon in your Applications folder.

### From Command Line
```bash
videowall
```

Or:
```bash
python -m videowall
```

## Troubleshooting

### Common Issues

#### No video playback
- Ensure proper multimedia codecs are installed
- Check network connection for streaming
- Verify video file formats are supported

#### Performance issues
- Reduce the number of active streams
- Use local videos instead of streams
- Check system resources with Activity Monitor

#### M3U8 stream issues
- Verify the stream URLs are valid
- Check if the streams are accessible from your network
- Try using the skip stream testing option in the configuration dialog

### GStreamer Issues on macOS

If you're having issues with video playback on macOS, you may need to install GStreamer:

```bash
brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly
```

Then, set the GStreamer environment variables:

```bash
export GST_PLUGIN_PATH="/usr/local/lib/gstreamer-1.0"
export GST_DEBUG=1
```

Or use the provided `run_minimal.sh` script which sets these variables for you.