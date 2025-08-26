# VideoWall Build and Compilation Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Platform-Specific Builds](#platform-specific-builds)
- [Build Configuration](#build-configuration)
- [PyInstaller Setup](#pyinstaller-setup)
- [Docker Builds](#docker-builds)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Overview

VideoWall uses PyInstaller for creating standalone executables across multiple platforms. The build system is designed to create optimized, self-contained applications that include all necessary dependencies and resources.

### Supported Platforms
- **macOS**: Intel (x86_64) and Apple Silicon (arm64)
- **Linux**: x86_64 and ARM64
- **Windows**: Planned support

### Build Artifacts
- **Standalone Executables**: Single file applications
- **Application Bundles**: .app bundles for macOS
- **Distribution Packages**: Tarballs, DEB/RPM packages
- **Docker Images**: Containerized deployments

## Prerequisites

### Common Requirements
- Python 3.8 or higher
- pip package manager
- Git for source code management

### Platform-Specific Requirements

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install python@3.9 pyqt5 create-dmg
```

#### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt-get update

# Install build dependencies
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    build-essential \
    qt5-default qttools5-dev-tools \
    libqt5multimedia5-dev libqt5multimediawidgets5-dev \
    pyqt5-dev-tools

# Install PyInstaller
pip3 install pyinstaller
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# CentOS/RHEL
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3 python3-pip qt5-qtbase-devel qt5-qtmultimedia-devel

# Fedora
sudo dnf install -y @development-tools python3 python3-pip qt5-qtbase-devel qt5-qtmultimedia-devel
```

## Platform-Specific Builds

### macOS Build

#### Standard Build
```bash
# Clone repository
git clone https://github.com/yourusername/video-wall.git
cd video-wall

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build for current architecture
pyinstaller VideoWall.spec --clean --noconfirm

# Create DMG installer
create-dmg \
  --volname "VideoWall" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "dist/VideoWall.app" 175 120 \
  --hide-extension "dist/VideoWall.app" \
  --app-drop-link 425 120 \
  "VideoWall.dmg" \
  "dist/"
```

#### Multi-Architecture Build
```bash
# Build Intel version
pyinstaller VideoWall.spec --clean --noconfirm
mv "dist/VideoWall.app" "dist/VideoWall-Intel.app"

# Build Apple Silicon version
pyinstaller VideoWall-arm64.spec --clean --noconfirm
mv "dist/VideoWall.app" "dist/VideoWall-ARM64.app"

# Create universal binary (optional)
lipo -create \
  "dist/VideoWall-Intel.app/Contents/MacOS/VideoWall" \
  "dist/VideoWall-ARM64.app/Contents/MacOS/VideoWall" \
  -output "dist/VideoWall-Universal.app/Contents/MacOS/VideoWall"
```

#### Code Signing (Optional)
```bash
# Sign the application
codesign --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/VideoWall.app"

# Verify signature
codesign --verify --verbose "dist/VideoWall.app"

# Notarize (for distribution)
xcrun altool --notarize-app \
  --primary-bundle-id "com.yourcompany.videowall" \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD" \
  --file "VideoWall.dmg"
```

### Linux Build

#### Standard Build
```bash
# Clone repository
git clone https://github.com/yourusername/video-wall.git
cd video-wall

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build application
pyinstaller VideoWall-linux.spec --clean --noconfirm

# Create distribution package
bash create-linux-package.sh
```

#### Docker Build (Cross-Platform)
```bash
# Build using Docker on macOS/Linux
docker build -f Dockerfile.linux -t videowall-builder .

# Run build
docker run --rm -v "$(pwd)":/app videowall-builder

# Extract build artifacts
docker cp $(docker create videowall-builder):/app/dist ./dist
```

#### Package Creation
```bash
# Create DEB package (Ubuntu/Debian)
mkdir -p videowall-deb/DEBIAN
mkdir -p videowall-deb/usr/bin
mkdir -p videowall-deb/usr/share/applications
mkdir -p videowall-deb/usr/share/icons/hicolor/256x256/apps

# Copy files
cp dist/VideoWall videowall-deb/usr/bin/
cp scripts/videowall.desktop videowall-deb/usr/share/applications/
cp build_resources/icons/icon.png videowall-deb/usr/share/icons/hicolor/256x256/apps/

# Create control file
cat > videowall-deb/DEBIAN/control << EOF
Package: videowall
Version: 1.0.0
Section: video
Priority: optional
Architecture: amd64
Depends: python3, libqt5multimedia5, libqt5multimediawidgets5
Maintainer: Your Name <your@email.com>
Description: Multi-display video wall application
 VideoWall is a sophisticated multi-display video wall application
 built with PyQt5, designed for creating hardware-accelerated video
 installations.
EOF

# Build package
dpkg-deb --build videowall-deb videowall_1.0.0_amd64.deb
```

## Build Configuration

### PyInstaller Spec Files

#### macOS Spec File (VideoWall.spec)
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['/path/to/video-wall'],
    binaries=[],
    datas=[
        ('config/m3u8-hosts.m3u8', 'config'),
        ('build_resources/icons/icon.icns', 'icons'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.QtNetwork',
        'PyQt5.QtGui',
    ],
    hookspath=['scripts'],
    runtime_hooks=['scripts/qt_plugin_path_hook.py'],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    icon='build_resources/icons/icon.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoWall'
)

app = BUNDLE(
    coll,
    name='VideoWall.app',
    icon='build_resources/icons/icon.icns',
    bundle_identifier='com.yourcompany.videowall',
    info_plist={
        'CFBundleName': 'VideoWall',
        'CFBundleDisplayName': 'VideoWall',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'VideoWall',
        'CFBundleIdentifier': 'com.yourcompany.videowall',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,
    }
)
```

#### Linux Spec File (VideoWall-linux.spec)
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['/path/to/video-wall'],
    binaries=[],
    datas=[
        ('config/m3u8-hosts.m3u8', 'config'),
        ('build_resources/icons/icon.png', 'icons'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.QtNetwork',
        'PyQt5.QtGui',
        'PyQt5.QtX11Extras',
    ],
    hookspath=['scripts'],
    runtime_hooks=['scripts/qt_plugin_path_hook.py'],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoWall',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='build_resources/icons/icon.png'
)
```

### Runtime Hooks

#### Qt Plugin Path Hook (scripts/qt_plugin_path_hook.py)
```python
import os
import sys

def find_qt_plugins():
    """Find Qt plugins directory."""
    # Common Qt plugin paths
    possible_paths = [
        os.path.join(sys._MEIPASS, 'qt', 'plugins'),
        os.path.join(sys._MEIPASS, 'PyQt5', 'Qt', 'plugins'),
        os.path.join(sys._MEIPASS, 'plugins'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    """Set Qt plugin path."""
    qt_plugins = find_qt_plugins()
    if qt_plugins:
        os.environ['QT_PLUGIN_PATH'] = qt_plugins

if __name__ == '__main__':
    main()
```

## Docker Builds

### Dockerfile.linux
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    qt5-default \
    qttools5-dev-tools \
    libqt5multimedia5-dev \
    libqt5multimediawidgets5-dev \
    pyqt5-dev-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PyInstaller
RUN pip install pyinstaller

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY build_resources/ ./build_resources/
COPY scripts/ ./scripts/
COPY VideoWall-linux.spec .

# Build application
RUN pyinstaller VideoWall-linux.spec --clean --noconfirm

# Create non-root user
RUN useradd -m -u 1000 videowall
USER videowall

# Set environment variables for running
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=:99

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["./dist/VideoWall"]
```

### Multi-Stage Docker Build
```dockerfile
# Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    qt5-default \
    qttools5-dev-tools \
    libqt5multimedia5-dev \
    libqt5multimediawidgets5-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
RUN pip install --user pyinstaller

COPY src/ ./src/
COPY config/ ./config/
COPY build_resources/ ./build_resources/
COPY scripts/ ./scripts/
COPY VideoWall-linux.spec .

RUN PYTHONPATH=/app/.local/lib/python3.11/site-packages \
    pyinstaller VideoWall-linux.spec --clean --noconfirm

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libqt5multimedia5 \
    libqt5multimediawidgets5 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    libqt5network5 \
    libqt5x11extras5 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built application
COPY --from=builder /app/dist/VideoWall .
COPY --from=builder /app/config ./config

# Create non-root user
RUN useradd -m -u 1000 videowall
USER videowall

ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb

CMD ["./VideoWall"]
```

## Troubleshooting

### Common Build Issues

#### Missing Qt Plugins
**Problem**: Application crashes with "Qt platform plugin" errors

**Solution**: Ensure Qt plugins are bundled correctly
```python
# In spec file, add to datas:
datas=[
    ('/path/to/qt/plugins', 'qt/plugins'),
]

# Or use runtime hook to set plugin path
os.environ['QT_PLUGIN_PATH'] = '/path/to/plugins'
```

#### Missing Hidden Imports
**Problem**: ImportError for PyQt5 modules

**Solution**: Add to hiddenimports in spec file
```python
hiddenimports=[
    'PyQt5.QtCore',
    'PyQt5.QtWidgets',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.QtNetwork',
    'PyQt5.QtGui',
    'PyQt5.QtX11Extras',  # Linux specific
]
```

#### Large Bundle Size
**Problem**: Generated executable is too large

**Solution**: Optimize spec file
```python
# Exclude unnecessary modules
excludes=[
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'PIL',
    'pandas',
]

# Use UPX compression
upx=True

# Strip binaries
strip=True
```

#### macOS Code Signing Issues
**Problem**: Application fails to run on other systems

**Solution**: Proper code signing
```bash
# Sign with developer ID
codesign --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/VideoWall.app"

# Notarize for distribution
xcrun altool --notarize-app \
  --primary-bundle-id "com.yourcompany.videowall" \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD" \
  --file "VideoWall.dmg"
```

### Debugging Builds

#### Verbose Build Output
```bash
# Run PyInstaller with verbose output
pyinstaller --log-level DEBUG VideoWall.spec

# Or use --debug flag
pyinstaller --debug all VideoWall.spec
```

#### Test Built Application
```bash
# Test in place
python -c "
import sys
sys.path.insert(0, 'dist/VideoWall')
from src.main import main
main()
"

# Test standalone
cd dist
./VideoWall --debug
```

#### Check Dependencies
```bash
# Check what's included
python -c "
import PyInstaller.utils.hooks
print(PyInstaller.utils.hooks.get_all_pyqt5_hiddenimports())
"

# Analyze binary
ldd dist/VideoWall  # Linux
otool -L dist/VideoWall  # macOS
```

## Advanced Configuration

### Custom Build Scripts

#### Automated Build Script (scripts/build-all.sh)
```bash
#!/bin/bash

set -e

VERSION=$(python -c "import src.config.settings; print(src.config.settings.VERSION)")
BUILD_DIR="build-$VERSION"

echo "Building VideoWall version $VERSION"

# Clean previous builds
rm -rf build/ dist/ $BUILD_DIR/
mkdir -p $BUILD_DIR

# Build for current platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Building for macOS..."
    
    # Intel build
    pyinstaller VideoWall.spec --clean --noconfirm
    create-dmg "dist/VideoWall.app" "$BUILD_DIR/VideoWall-macOS-Intel.dmg"
    
    # ARM64 build (if on Apple Silicon)
    if [[ $(uname -m) == "arm64" ]]; then
        pyinstaller VideoWall-arm64.spec --clean --noconfirm
        create-dmg "dist/VideoWall.app" "$BUILD_DIR/VideoWall-macOS-ARM64.dmg"
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Building for Linux..."
    pyinstaller VideoWall-linux.spec --clean --noconfirm
    bash create-linux-package.sh
    mv VideoWall-Linux-Package.tar.gz "$BUILD_DIR/"
fi

# Create checksums
cd $BUILD_DIR
sha256sum * > SHA256SUMS
cd ..

echo "Build complete! Files in $BUILD_DIR/"
ls -la $BUILD_DIR/
```

### CI/CD Integration

#### GitHub Actions Workflow (.github/workflows/build.yml)
```yaml
name: Build

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  release:
    types: [published]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
        
    - name: Build application
      run: |
        if [[ "$RUNNER_OS" == "macOS" ]]; then
          pyinstaller VideoWall.spec --clean --noconfirm
        else
          pyinstaller VideoWall-linux.spec --clean --noconfirm
        fi
        
    - name: Test build
      run: |
        cd dist
        ./VideoWall --version
        
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: videowall-${{ runner.os }}
        path: dist/
```

### Performance Optimization

#### Build Optimization
```python
# In spec file, optimize for size
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoWall',
    debug=False,          # Exclude debug info
    strip=True,          # Strip symbols
    upx=True,           # Compress with UPX
    upx_exclude=[],      # Exclude problematic binaries from UPX
    console=False,
)
```

#### Runtime Optimization
```python
# Add to main.py for better performance
import os

# Optimize Qt settings
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

# Optimize multimedia
os.environ['QT_MEDIA_BACKEND'] = 'gstreamer'  # Linux
os.environ['QT_AVPLAYER_OPTIONS'] = 'hardware-acceleration'  # macOS
```

---

This build system provides comprehensive support for creating optimized, cross-platform distributions of VideoWall with proper dependency management and deployment strategies.