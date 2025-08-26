# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project: VideoWall

A multi-display video wall application built with PyQt5. Supports M3U8 streaming and local video playback across multiple monitors with hardware acceleration and animated layout transitions.

**Author**: J. Michaels (sanchez314c)
**Version**: 1.0.0
**Language**: Python 3.11
**Framework**: PyQt5

## Quick Start

```bash
# Linux
./run-source-linux.sh

# macOS
./run-source-mac.sh

# Direct
python -m src
python -m src --hwa-enabled   # with hardware acceleration
```

## Project Structure

```
video-wall/
├── src/                    # Application source code
│   ├── main.py             # Direct execution entry point
│   ├── __main__.py         # Module execution entry point
│   ├── core/               # Core application logic
│   │   ├── app.py          # Application init and arg parsing
│   │   ├── video_wall.py   # Main window and coordinator
│   │   ├── video_manager.py
│   │   ├── display_manager.py
│   │   ├── layout_manager.py
│   │   ├── animator.py
│   │   ├── video_loader.py
│   │   └── stream_tracker.py
│   ├── ui/                 # UI components
│   │   ├── video_tile.py
│   │   ├── dialogs.py
│   │   └── status_overlay.py
│   └── utils/              # Utility modules
│       ├── file_utils.py
│       └── stream_utils.py
├── config/                 # Configuration files
│   └── m3u8-hosts.m3u8     # Stream URLs
├── resources/              # App resources
│   └── icons/              # Application icons
├── build_resources/        # PyInstaller build resources
│   └── icons/              # Build-time icons (.icns, .ico, .png)
├── tests/                  # Test suite
├── docs/                   # Full documentation
├── scripts/                # Build and utility scripts
│   └── legacy/             # Old standalone scripts
├── archive/                # Timestamped backups
└── legacy/                 # Legacy version storage
```

## Development Rules

1. **Read files before editing** — never assume content
2. **No stray files in root** — put things in their proper subdirectory
3. **Backup before major changes** — use `archive/` folder
4. **Python 3.11** via conda or venv
5. **No direct deletion** — move to archive or legacy

## Key Settings (src/config/settings.py)

- `DEFAULT_GRID_ROWS = 3`, `DEFAULT_GRID_COLS = 3`
- `ANIMATION_DURATION_MS = 8000`
- `VIDEO_BUFFER_SIZE = 15000`
- `MAX_ACTIVE_PLAYERS = 15`

## Dependencies

```
PyQt5 >= 5.15.0
requests >= 2.25.0
pyinstaller >= 5.0  (build only)
```

**Linux system packages:**
```bash
sudo apt-get install libqt5multimedia5 libqt5multimediawidgets5 \
    libqt5widgets5 libqt5gui5 libqt5core5a libqt5network5
```

## Build

```bash
# Linux
pyinstaller VideoWall.spec --clean --noconfirm

# macOS ARM64
pyinstaller VideoWall-arm64.spec --clean --noconfirm

# macOS Intel
pyinstaller VideoWall-intel.spec --clean --noconfirm
```

## Testing

```bash
pytest tests/
pytest --cov=src --cov-report=html tests/
```

## Documentation

Full docs in `docs/` — see `docs/DOCUMENTATION_INDEX.md` for the index.
