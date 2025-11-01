# VideoWall Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Platform-Specific Deployment](#platform-specific-deployment)
- [Build System](#build-system)
- [Distribution](#distribution)
- [Installation Packages](#installation-packages)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Overview

VideoWall supports multiple deployment strategies depending on the target environment and use case:

- **Standalone Applications**: Native executables for macOS and Linux
- **Docker Containers**: Containerized deployments for cloud or on-premise
- **Source Installation**: Development or custom deployments
- **Package Managers**: System package installations

## Platform-Specific Deployment

### macOS Deployment

#### Prerequisites
- macOS 10.14+ (Mojave or later)
- Xcode Command Line Tools
- Python 3.8+ (for source builds)
- Apple Developer ID (for distribution)

#### Build Process

1. **Install Dependencies**
   ```bash
   # Install PyInstaller and dependencies
   pip install pyinstaller PyQt5
   
   # Install build tools
   brew install create-dmg
   ```

2. **Build Application**
   ```bash
   # Intel build
   pyinstaller VideoWall.spec --clean --noconfirm
   
   # Apple Silicon build
   pyinstaller VideoWall-arm64.spec --clean --noconfirm
   ```

3. **Create DMG Package**
   ```bash
   # Create DMG installer
   create-dmg \
     --volname "VideoWall" \
     --window-pos 200 120 \
     --window-size 600 300 \
     --icon-size 100 \
     --icon "VideoWall.app" 175 120 \
     --hide-extension "VideoWall.app" \
     --app-drop-link 425 120 \
     "VideoWall.dmg" \
     "dist/VideoWall.app"
   ```

4. **Code Signing (Optional)**
   ```bash
   # Sign the application
   codesign --force --verify --verbose --sign "Developer ID Application: Your Name" \
     dist/VideoWall.app/Contents/MacOS/VideoWall
   
   # Create notarized DMG
   xcrun altool --notarize-app \
     --primary-bundle-id "com.yourcompany.videowall" \
     --username "your@email.com" \
     --password "@keychain:AC_PASSWORD" \
     --file VideoWall.dmg
   ```

#### Installation
```bash
# Mount DMG and copy to Applications
hdiutil attach VideoWall.dmg
cp -R "/Volumes/VideoWall/VideoWall.app" /Applications/
hdiutil detach "/Volumes/VideoWall"
```

### Linux Deployment

#### Prerequisites
- Linux distribution (Ubuntu 18.04+, CentOS 7+, etc.)
- Python 3.8+ (for source builds)
- Build tools and Qt5 development libraries

#### Build Process

1. **Install System Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y \
     python3 python3-pip python3-venv \
     build-essential \
     qt5-default qttools5-dev-tools \
     libqt5multimedia5-dev libqt5multimediawidgets5-dev
   
   # CentOS/RHEL
   sudo yum install -y \
     python3 python3-pip \
     gcc gcc-c++ make \
     qt5-qtbase-devel qt5-qtmultimedia-devel
   ```

2. **Build Application**
   ```bash
   # Using PyInstaller
   pyinstaller VideoWall-linux.spec --clean --noconfirm
   
   # Or using build script
   bash build-linux.sh
   ```

3. **Create Package**
   ```bash
   # Create tar.gz package
   bash create-linux-package.sh
   
   # Or create DEB package (Ubuntu)
   dpkg-deb --build videowall-package
   ```

#### Installation

**From Tarball:**
```bash
tar -xzf VideoWall-Linux-Package.tar.gz
cd VideoWall-Linux
sudo ./install.sh
```

**From DEB Package:**
```bash
sudo dpkg -i videowall_1.0.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed
```

**From RPM Package:**
```bash
sudo rpm -i videowall-1.0.0.x86_64.rpm
```

## Build System

### PyInstaller Configuration

#### Spec File Structure
```python
# VideoWall.spec example
a = Analysis(
    ['src/main.py'],
    pathex=['/path/to/videowall'],
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
    ],
    hookspath=[],
    runtime_hooks=['scripts/qt_plugin_path_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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
    icon='build_resources/icons/icon.ico'
)
```

#### Build Scripts

**macOS Build Script:**
```bash
#!/bin/bash
# build-macos.sh

set -e

echo "Building VideoWall for macOS..."

# Clean previous builds
rm -rf build/ dist/

# Determine architecture
ARCH=$(uname -m)
SPEC_FILE="VideoWall.spec"

if [[ "$ARCH" == "arm64" ]]; then
    SPEC_FILE="VideoWall-arm64.spec"
fi

# Build application
pyinstaller "$SPEC_FILE" --clean --noconfirm

# Create DMG
create-dmg \
  --volname "VideoWall" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "dist/VideoWall.app" 175 120 \
  --hide-extension "dist/VideoWall.app" \
  --app-drop-link 425 120 \
  "VideoWall-$ARCH.dmg" \
  "dist/"

echo "Build complete: VideoWall-$ARCH.dmg"
```

**Linux Build Script:**
```bash
#!/bin/bash
# build-linux.sh

set -e

echo "Building VideoWall for Linux..."

# Clean previous builds
rm -rf build/ dist/

# Build application
pyinstaller VideoWall-linux.spec --clean --noconfirm

# Create package
bash create-linux-package.sh

echo "Build complete: VideoWall-Linux-Package.tar.gz"
```

### Docker Build

#### Dockerfile
```dockerfile
# Dockerfile.linux
FROM python:3.11-slim

# Install system dependencies
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

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY build_resources/ ./build_resources/

# Install application
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 videowall
USER videowall

# Set environment variables
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=offscreen

# Expose port for web interface (if applicable)
EXPOSE 8080

# Run application
CMD ["python", "-m", "src", "--no-gui"]
```

#### Build and Run
```bash
# Build Docker image
docker build -f Dockerfile.linux -t videowall:latest .

# Run container
docker run -d \
  --name videowall \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  videowall:latest
```

## Distribution

### GitHub Releases

#### Automated Release Workflow
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
        
    - name: Build application
      run: |
        if [[ "$RUNNER_OS" == "macOS" ]]; then
          pyinstaller VideoWall.spec --clean --noconfirm
        else
          pyinstaller VideoWall-linux.spec --clean --noconfirm
        fi
        
    - name: Create release asset
      run: |
        if [[ "$RUNNER_OS" == "macOS" ]]; then
          tar -czf VideoWall-macOS.tar.gz -C dist .
        else
          tar -czf VideoWall-Linux.tar.gz -C dist .
        fi
        
    - name: Upload release asset
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ github.event.release.upload_url }}
        asset_path: VideoWall-${{ runner.os }}.tar.gz
        asset_name: VideoWall-${{ runner.os }}.tar.gz
        asset_content_type: application/gzip
```

### Package Managers

#### Homebrew (macOS)
```ruby
# Formula/videowall.rb
class Videowall < Formula
  desc "Multi-display video wall application"
  homepage "https://github.com/yourusername/video-wall"
  url "https://github.com/yourusername/video-wall/archive/v1.0.0.tar.gz"
  sha256 "..."
  
  depends_on "python@3.9"
  depends_on "pyqt5"
  
  def install
    bin.install "src/main.py" => "videowall"
    prefix.install "src"
    prefix.install "config"
    prefix.install "build_resources"
  end
  
  test do
    system "#{bin}/videowall", "--version"
  end
end
```

#### APT (Ubuntu/Debian)
```bash
# Create PPA repository structure
mkdir -p videowall-ppa/{debian,conf}

# conf/distributions
Origin: VideoWall PPA
Label: VideoWall PPA
Codename: focal
Architectures: amd64 arm64
Components: main
Description: VideoWall PPA repository
SignWith: YOUR_GPG_KEY_ID

# Build and upload package
debuild -S
dput ppa:yourusername/videowall videowall_1.0.0_source.changes
```

## Installation Packages

### Windows Installer (Future)
```python
# build_windows.py (for future Windows support)
import cx_Freeze

executables = [
    cx_Freeze.Executable(
        "src/main.py",
        base="Win32GUI",
        targetName="VideoWall.exe",
        icon="build_resources/icons/icon.ico"
    )
]

cx_Freeze.setup(
    name="VideoWall",
    version="1.0.0",
    description="Multi-display video wall application",
    executables=executables,
    options={
        "build_exe": {
            "packages": ["PyQt5"],
            "include_files": [
                ("config/m3u8-hosts.m3u8", "config/m3u8-hosts.m3u8"),
                ("build_resources/icons", "icons")
            ]
        }
    }
)
```

### Snap Package (Linux)
```yaml
# snap/snapcraft.yaml
name: videowall
version: '1.0.0'
summary: Multi-display video wall application
description: |
  VideoWall is a sophisticated multi-display video wall application 
  built with PyQt5, designed for creating hardware-accelerated video 
  installations on Linux.

grade: stable
confinement: strict

apps:
  videowall:
    command: bin/python3 -m src
    plugs:
      - home
      - network
      - audio-playback
      - opengl
      - desktop
      - desktop-legacy
      - x11

parts:
  videowall:
    plugin: python
    python-version: python3
    source: .
    stage-packages:
      - python3-pyqt5
      - python3-pyqt5.qtmultimedia
      - libqt5multimedia5
      - libqt5multimediawidgets5
```

## Docker Deployment

### Multi-Stage Docker Build
```dockerfile
# Dockerfile.multi-stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    qt5-default \
    qttools5-dev-tools \
    libqt5multimedia5-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libqt5multimedia5 \
    libqt5multimediawidgets5 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    libqt5network5 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY src/ /app/src/
COPY config/ /app/config/
COPY build_resources/ /app/build_resources/

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 videowall
USER videowall

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["python", "-m", "src"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  videowall:
    build:
      context: .
      dockerfile: Dockerfile.multi-stage
    environment:
      - DISPLAY=${DISPLAY}
      - QT_QPA_PLATFORM=xcb
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
      - ./videos:/app/videos:ro
      - ./config/m3u8-hosts.m3u8:/app/config/m3u8-hosts.m3u8:ro
    ports:
      - "8080:8080"  # If web interface is added
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - videowall
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance
```bash
# Launch EC2 instance with GPU support
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type g4dn.xlarge \
  --key-name my-key-pair \
  --security-group-ids sg-903004f8 \
  --subnet-id subnet-6e7f829e \
  --user-data file://user-data.sh
```

#### User Data Script
```bash
#!/bin/bash
# user-data.sh

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker

# Pull and run VideoWall
docker run -d \
  --name videowall \
  --restart unless-stopped \
  -p 8080:8080 \
  your-registry/videowall:latest
```

### Kubernetes Deployment

#### Deployment Manifest
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: videowall
spec:
  replicas: 3
  selector:
    matchLabels:
      app: videowall
  template:
    metadata:
      labels:
        app: videowall
    spec:
      containers:
      - name: videowall
        image: your-registry/videowall:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DISPLAY
          value: ":99"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        volumeMounts:
        - name: video-storage
          mountPath: /app/videos
          readOnly: true
      volumes:
      - name: video-storage
        persistentVolumeClaim:
          claimName: video-pvc
```

#### Service Manifest
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: videowall-service
spec:
  selector:
    app: videowall
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

## Monitoring and Maintenance

### Health Monitoring

#### Application Health Check
```python
# src/health.py
import psutil
import requests
from PyQt5.QtCore import QTimer

class HealthMonitor:
    def __init__(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_health)
        self.timer.start(30000)  # Check every 30 seconds
        
    def check_health(self):
        """Check application health metrics."""
        metrics = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'active_players': self.get_active_player_count(),
            'display_count': self.get_display_count()
        }
        
        # Log metrics
        logger.info(f"Health metrics: {metrics}")
        
        # Alert if thresholds exceeded
        if metrics['cpu_percent'] > 90:
            logger.warning("High CPU usage detected")
        if metrics['memory_percent'] > 90:
            logger.warning("High memory usage detected")
```

#### Prometheus Metrics
```python
# src/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
video_playback_counter = Counter('videowall_playback_total', 'Total video playbacks')
error_counter = Counter('videowall_errors_total', 'Total errors', ['error_type'])
active_players_gauge = Gauge('videowall_active_players', 'Number of active players')
playback_duration = Histogram('videowall_playback_duration_seconds', 'Video playback duration')

def start_metrics_server(port=8000):
    """Start Prometheus metrics server."""
    start_http_server(port)
```

### Log Management

#### Log Rotation
```python
# src/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure logging with rotation."""
    handler = RotatingFileHandler(
        'video_wall.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
```

#### Centralized Logging
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  videowall:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: videowall
        
  fluentd:
    image: fluent/fluentd:v1.14-debian-1
    volumes:
      - ./fluent.conf:/fluentd/etc/fluent.conf
    ports:
      - "24224:24224"
      
  elasticsearch:
    image: elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
      
  kibana:
    image: kibana:7.15.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Backup and Recovery

#### Configuration Backup
```bash
#!/bin/bash
# backup-config.sh

BACKUP_DIR="/backup/videowall/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r config/ "$BACKUP_DIR/"
cp -r build_resources/ "$BACKUP_DIR/"

# Backup user data (if any)
cp -r ~/.videowall/ "$BACKUP_DIR/user-data/" 2>/dev/null || true

# Create archive
tar -czf "videowall-backup-$(date +%Y%m%d_%H%M%S).tar.gz" -C "$BACKUP_DIR" .

# Cleanup old backups (keep last 7 days)
find /backup/videowall -name "*.tar.gz" -mtime +7 -delete
```

#### Automated Recovery
```python
# src/recovery.py
import os
import shutil
import tarfile

class RecoveryManager:
    def __init__(self, backup_dir="/backup/videowall"):
        self.backup_dir = backup_dir
        
    def restore_from_backup(self, backup_file):
        """Restore configuration from backup."""
        try:
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall()
                
            # Move files to correct locations
            if os.path.exists("config/"):
                shutil.rmtree("config/")
            shutil.move("config/", "./")
            
            logger.info(f"Successfully restored from {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
            
    def list_backups(self):
        """List available backups."""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith(".tar.gz"):
                backups.append(os.path.join(self.backup_dir, file))
        return sorted(backups, reverse=True)
```

---

For additional deployment options, see [BUILD_COMPILE.md](BUILD_COMPILE.md) or contact the development team.