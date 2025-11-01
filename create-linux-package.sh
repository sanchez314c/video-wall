#!/bin/bash

# Create a deployable Linux package for VideoWall
# This creates a tarball with all necessary files and installation instructions

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Get directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create Linux package directory
PKG_DIR="VideoWall-Linux-x64"
rm -rf "$PKG_DIR"
mkdir -p "$PKG_DIR"

print_status "Creating Linux package for VideoWall..."

# Create a Linux spec file that produces a portable binary
cat > VideoWall-linux-portable.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for VideoWall - Linux portable version
Produces a binary that should work on most Linux distributions
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the directory of the spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Analysis phase
a = Analysis(
    ['src/main.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        ('config/m3u8-hosts.m3u8', '.'),
        ('build_resources/icons/icon.png', 'icons/'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.QtNetwork',
        'PyQt5.QtOpenGL',
        'sip',
        'src.core.app',
        'src.core.video_player',
        'src.core.stream_loader',
        'src.utils.config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE creation - Linux version
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoWall',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    icon='build_resources/icons/icon.png' if os.path.exists('build_resources/icons/icon.png') else None,
)

# Collect all dependencies
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoWall',
)
EOF

# Try to build with the current Python (for users who will run this on Linux)
print_status "Creating Linux build script..."
cat > "$PKG_DIR/build-on-linux.sh" << 'EOF'
#!/bin/bash

# Build VideoWall on Linux
# Run this script on a Linux machine to build the binary

set -e

echo "Building VideoWall for Linux..."

# Check if running on Linux
if [ "$(uname)" != "Linux" ]; then
    echo "Error: This script must be run on Linux"
    exit 1
fi

# Install dependencies (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "Installing dependencies with apt..."
    sudo apt-get update
    sudo apt-get install -y \
        python3-pyqt5 \
        python3-pyqt5.qtmultimedia \
        python3-pip \
        build-essential
fi

# Install dependencies (Fedora/CentOS)
if command -v dnf &> /dev/null; then
    echo "Installing dependencies with dnf..."
    sudo dnf install -y \
        python3-qt5 \
        python3-pip \
        gcc
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install pyinstaller PyQt5 PyQt5Multimedia requests

# Build
echo "Building with PyInstaller..."
pyinstaller VideoWall-linux-portable.spec --clean --noconfirm

# Create package
echo "Creating package..."
tar -czf VideoWall-Linux-x64.tar.gz dist/VideoWall/

echo "Build complete! Package: VideoWall-Linux-x64.tar.gz"
EOF

chmod +x "$PKG_DIR/build-on-linux.sh"

# Create installation script
cat > "$PKG_DIR/install.sh" << 'EOF'
#!/bin/bash

# Installation script for VideoWall on Linux
# Run this after extracting the VideoWall binary package

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "Installing VideoWall for Linux..."

# Check if running on Linux
if [ "$(uname)" != "Linux" ]; then
    print_error "This installer is for Linux only"
    exit 1
fi

# Detect package manager
if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt"
    print_info "Detected Debian/Ubuntu-based system"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    print_info "Detected Fedora/CentOS-based system"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
    print_info "Detected Arch-based system"
else
    print_warning "Unknown package manager. You may need to install dependencies manually."
fi

# Install system dependencies
case $PKG_MANAGER in
    apt)
        print_info "Installing Qt5 dependencies..."
        sudo apt-get update
        sudo apt-get install -y \
            libqt5multimedia5 \
            libqt5multimediawidgets5 \
            libqt5widgets5 \
            libqt5gui5 \
            libqt5core5a \
            libqt5network5 \
            libqt5svg5 \
            libqt5opengl5 \
            libqt5printsupport5
        ;;
    dnf)
        print_info "Installing Qt5 dependencies..."
        sudo dnf install -y \
            qt5-qtmultimedia \
            qt5-qtbase-gui \
            qt5-qtbase \
            qt5-qtnetworkauth \
            qt5-qtsvg
        ;;
    pacman)
        print_info "Installing Qt5 dependencies..."
        sudo pacman -S --noconfirm \
            qt5-multimedia \
            qt5-base \
            qt5-networkauth \
            qt5-svg
        ;;
esac

# Install optional dependencies for better video support
print_warning "Installing optional GStreamer dependencies for better video support..."
case $PKG_MANAGER in
    apt)
        sudo apt-get install -y \
            gstreamer1.0-libav \
            gstreamer1.0-plugins-ugly \
            gstreamer1.0-plugins-bad || true
        ;;
    dnf)
        sudo dnf install -y \
            gstreamer1-libav \
            gstreamer1-plugins-ugly \
            gstreamer1-plugins-bad-freeworld || true
        ;;
esac

# Create desktop entry
print_info "Creating desktop shortcut..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/VideoWall.desktop << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=VideoWall
Comment=Multi-stream video wall application
Exec=$(pwd)/VideoWall/run-VideoWall.sh
Icon=$(pwd)/VideoWall/icons/icon.png
Terminal=false
Categories=AudioVideo;Video;
EOL

update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

print_success "Installation complete!"
print_info "To run VideoWall:"
print_info "  1. Navigate to the VideoWall directory"
print_info "  2. Run: ./run-VideoWall.sh"
print_info ""
print_info "Or use the application menu shortcut"
EOF

chmod +x "$PKG_DIR/install.sh"

# Create run script
cat > "$PKG_DIR/run-VideoWall.sh" << 'EOF'
#!/bin/bash

# Run VideoWall on Linux

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set environment variables
export QT_PLUGIN_PATH="$SCRIPT_DIR/plugins:$QT_PLUGIN_PATH"
export LD_LIBRARY_PATH="$SCRIPT_DIR:$LD_LIBRARY_PATH"

# Run the application
if [ -f "$SCRIPT_DIR/VideoWall" ]; then
    cd "$SCRIPT_DIR"
    ./VideoWall "$@"
else
    echo "Error: VideoWall binary not found"
    echo "Please build VideoWall first using: ./build-on-linux.sh"
    exit 1
fi
EOF

chmod +x "$PKG_DIR/run-VideoWall.sh"

# Create README
cat > "$PKG_DIR/README.md" << 'EOF'
# VideoWall - Linux Version

VideoWall is a multi-stream video wall application that displays multiple M3U8 streams simultaneously.

## Quick Start

### Option 1: Build from Source
1. Install dependencies:
   ```bash
   # Ubuntu/Debian:
   sudo apt-get install python3-pyqt5 python3-pyqt5.qtmultimedia

   # Or run the install script:
   ./install.sh
   ```

2. Build the application:
   ```bash
   ./build-on-linux.sh
   ```

3. Run:
   ```bash
   ./run-VideoWall.sh
   ```

### Option 2: Use Pre-built Binary
If you have a pre-built binary:
1. Run the installer to set up dependencies:
   ```bash
   ./install.sh
   ```

2. Run the application:
   ```bash
   ./run-VideoWall.sh
   ```

## System Requirements

- Linux (x86_64)
- Qt5 (version 5.12 or higher)
- PyQt5
- PyQt5Multimedia
- GStreamer (for optimal video playback)

## Dependencies Installation

### Ubuntu/Debian:
```bash
sudo apt-get install libqt5multimedia5 libqt5multimediawidgets5 \
  libqt5widgets5 libqt5gui5 libqt5core5a libqt5network5 \
  gstreamer1.0-libav gstreamer1.0-plugins-ugly
```

### Fedora/CentOS:
```bash
sudo dnf install qt5-qtmultimedia qt5-qtbase-gui \
  qt5-base qt5-qtnetworkauth qt5-qtsvg
```

### Arch Linux:
```bash
sudo pacman -S qt5-multimedia qt5-base qt5-networkauth qt5-svg
```

## Configuration

The application loads M3U8 streams from:
- `m3u8-hosts.m3u8` (in the application directory)

To customize streams, edit this file with your M3U8 URLs.

## Troubleshooting

### Application won't start:
1. Check if all Qt5 dependencies are installed
2. Try running with debug output: `./VideoWall 2>&1`
3. Ensure the binary is executable: `chmod +x VideoWall`

### No video playback:
1. Install GStreamer plugins (see dependencies)
2. Check network connectivity
3. Verify M3U8 URLs are valid

### Performance issues:
1. Reduce number of simultaneous streams
2. Check system resources (CPU, RAM, GPU)
3. Update graphics drivers

## License

Please refer to the main project repository for license information.
EOF

# Copy necessary files
cp -r config/ "$PKG_DIR/" 2>/dev/null || true
cp -r build_resources/icons/ "$PKG_DIR/" 2>/dev/null || true

# Create archive
print_status "Creating package archive..."
tar -czf "VideoWall-Linux-Package.tar.gz" "$PKG_DIR"

print_success "Linux package created!"
print_warning ""
print_warning "NOTE: This package contains build scripts for Linux."
print_warning "To build the binary:"
print_warning "  1. Copy VideoWall-Linux-Package.tar.gz to a Linux machine"
print_warning "  2. Extract: tar -xzf VideoWall-Linux-Package.tar.gz"
print_warning "  3. Run: cd VideoWall-Linux-x64 && ./build-on-linux.sh"
print_warning ""
print_status "Package created: VideoWall-Linux-Package.tar.gz"
print_status "Size: $(du -h VideoWall-Linux-Package.tar.gz | cut -f1)"