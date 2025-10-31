# Building VideoWall for Linux

## Option 1: Using GitHub Actions (Recommended)

1. Push your code to GitHub
2. Go to the Actions tab in your repository
3. Select "Build Linux Binary" workflow
4. Click "Run workflow"
5. Download the `videowall-linux` artifact when complete

## Option 2: Using Docker on macOS

### Prerequisites
- Docker Desktop installed and running

### Method A: Debian-based build
```bash
bash build-linux.sh
```

### Method B: Alpine-based build (smaller image)
```bash
bash build-linux-alpine.sh
```

## Option 3: Manual Linux Build

On a Linux machine with:

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3-pyqt5 \
    python3-pyqt5.qtmultimedia \
    python3-pyqt5.qtquick \
    qt5-default \
    libqt5multimedia5-plugins \
    libqt5multimediawidgets5 \
    libqt5multimedia5 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    libqt5network5 \
    libqt5svg5

# Install Python dependencies
pip install pyinstaller==6.16.0 PyQt5 PyQt5Multimedia requests

# Build
pyinstaller VideoWall-linux.spec --clean --noconfirm
```

## Running the Linux Binary

1. Copy the `dist/Linux` folder to your Linux machine
2. Navigate to the folder: `cd dist/Linux`
3. Run: `./run-VideoWall.sh`

## Dependencies on Target Linux System

The user needs to have these packages installed:
- libqt5multimedia5
- libqt5multimediawidgets5
- libqt5widgets5
- libqt5gui5
- libqt5core5a
- libqt5network5

Install with:
```bash
sudo apt-get install libqt5multimedia5 libqt5multimediawidgets5 libqt5widgets5 libqt5gui5 libqt5core5a libqt5network5
```

## Troubleshooting

### If the app doesn't start:
1. Check if all Qt dependencies are installed
2. Try running with: `./VideoWall 2>&1 | head -20`
3. Make sure the binary is executable: `chmod +x VideoWall`

### If video playback doesn't work:
1. Install gstreamer plugins: `sudo apt-get install gstreamer1.0-libav gstreamer1.0-plugins-ugly`
2. Check if M3U8 streaming is supported
3. Verify network connectivity