# Product Requirements Document — VideoWall

**Version**: 1.6.4
**Last Updated**: 2026-04-17
**Owner**: J. Michaels (sanchez314c)
**Status**: Active development, queued for ship

---

## 1. Product Summary

VideoWall is a desktop application that fills every connected monitor with a dynamic grid of video tiles. Each tile pulls a unique stream from an M3U8 playlist (HLS) or falls back to a local video file. Layouts cycle automatically every 5–30 seconds with smooth Qt property animations. Built for installations, control rooms, digital signage, and ambient displays.

Pure Python + Qt. No OpenCV, no Electron, no Node, no FFmpeg Python bindings.

## 2. Tech Stack

| Layer | Choice | Version |
|---|---|---|
| Language | Python | 3.8+ (3.11 recommended) |
| GUI / Multimedia | PyQt5 | 5.15+ |
| Video backend (Linux) | GStreamer 1.0 (system) | system-installed |
| Video backend (macOS) | Qt native | Qt 5.15 |
| Screen recording | ffmpeg (x11grab) | system-installed |
| HTTP / stream validation | requests | 2.28+ |
| Packaging | PyInstaller | 5.0+ |
| Test framework | pytest, pytest-qt, pytest-cov | 7.0+ |

**No web tech.** This is a native desktop binary.

## 3. Architecture (current)

```
src/
├── main.py              # Direct execution entry
├── __main__.py          # Module execution entry (python -m src)
├── core/
│   ├── app.py           # QApplication init, arg parsing, screen spawning
│   ├── video_wall.py    # Per-monitor main window, keyboard shortcuts, timers
│   ├── display_manager.py  # Grid layout, tile creation, fullscreen toggle
│   ├── video_manager.py # Player lifecycle, stream/fallback switching
│   ├── video_loader.py  # Media loading, GPU detection, player config
│   ├── layout_manager.py # 6 layout patterns, tile placement math
│   ├── animator.py      # QPropertyAnimation controller, transition scheduler
│   └── recorder.py      # ffmpeg x11grab recorder + blinking REC indicator (Linux X11 only)
├── ui/
│   ├── video_tile.py    # QVideoWidget with status/loading overlays
│   ├── dialogs.py       # Frameless startup config dialog
│   ├── status_overlay.py # Per-tile state badge
│   └── theme.py         # Dark Neo Glass design system + QSS (848 LOC)
├── utils/
│   ├── file_utils.py    # M3U8 parsing, recursive video file scan
│   └── (stream_utils.py removed in refactor — was unused)
└── config/
    └── settings.py      # All app-wide constants
```

**Total LOC**: ~3,488 across 21 Python files (post-refactor: removed 2 dead modules and ~120 LOC of dead GPU detection).

**Resource files**:
- `m3u8-hosts.m3u8` — playlist (root level, also bundled into binary)
- `resources/icons/` — app icons
- `build_resources/icons/` — PyInstaller build-time icons (.icns, .ico, .png)
- `scripts/qt_plugin_path_hook.py` — PyInstaller runtime hook for GStreamer paths

## 4. Functional Requirements

### 4.1 Display Management
- Auto-detect all monitors via `QApplication.screens()` at startup
- Spawn one fullscreen `VideoWall` window per detected display
- Monitors connected after launch are NOT picked up (documented limitation)
- Mixed-resolution displays supported (each window sized to its screen)

### 4.2 Content Playback
- M3U8 / HLS streaming via QMediaPlayer
- Local video fallback (MP4, AVI, MOV, MKV, WEBM) on stream timeout/error
- Up to **15 concurrent active players** (`MAX_ACTIVE_PLAYERS`)
- 6–12 visible tiles at any time, drawn from a 4×4 grid pool
- Hardware acceleration: opt-in via `--hwa-enabled` flag, strategy `alternate` (every other tile)

### 4.3 Layouts (Animator)
Six patterns cycle automatically:
- **Varied** — mix of 1×1, 1×2, 2×1, 2×2 tiles
- **Feature** — one 2×2 dominates, rest fill around it
- **Columns** — tall 2×1 tiles, no wide spans
- **Rows** — wide 1×2 tiles, no tall spans
- **Mixed** — medium variety, 2×2 + mixed spans
- **Asymmetric** — offset arrangement, varied sizes

Animator fires every 5 / 15 / 30 sec (random). 90% reshuffle, 10% animated tile swap. Animation duration: 8000ms (`ANIMATION_DURATION_MS`).

### 4.4 Stream Health
- Stream check interval: 30000ms (`STREAM_CHECK_INTERVAL_MS`)
- Loading timeout before fallback: 15000ms (`VIDEO_LOADING_TIMEOUT_MS`)
- Failed stream → tile auto-switches to local video from configured folder

### 4.5 Screen Recording
- Toggle: `R` key
- Backend: ffmpeg `x11grab` (Linux X11 only — Wayland NOT supported)
- Output: `~/Desktop/VideoWall-Recording-YYYYMMDD_HHMMSS.mp4`
- Visual indicator: blinking red REC badge top-left

### 4.6 Startup Dialog
Frameless Dark Neo Glass dialog on launch. User selects:
- Skip stream pre-testing (default ON for fast startup)
- Enable local video fallback + folder picker
- Auto-start recording 3 seconds after launch

### 4.7 Keyboard Shortcuts
| Key | Action |
|---|---|
| Right Arrow | Manual layout refresh |
| `R` | Toggle screen recording |
| `F11` / `Alt+F` | Toggle fullscreen |
| `Esc` | Exit fullscreen / quit |
| `Ctrl+Q` | Quit |

## 5. Non-Functional Requirements

### Performance
- Target: smooth playback of 9 simultaneous 1080p streams on a single display
- Memory ceiling: bounded by `MAX_ACTIVE_PLAYERS = 15`
- Startup: under ~3 seconds to first tile rendering (depends on `skip_stream_testing`)

### Reliability
- Stream failures self-recover via fallback timer
- No process should crash the parent QApplication; player errors are caught per-tile
- GStreamer plugin path is set BEFORE QApplication init (Linux only) — critical for PyInstaller bundles

### Platform Support
| Platform | Status | Notes |
|---|---|---|
| Linux (X11) | Primary | GStreamer 1.0, x11grab recording |
| Linux (Wayland) | Partial | Playback works, recording does NOT |
| macOS (Intel) | Supported | Qt native backend, separate spec file |
| macOS (ARM64) | Supported | Separate spec file |
| Windows | Build script exists, untested | `run-source-windows.bat` |

### Security
- Stream URLs in `m3u8-hosts.m3u8` are user-provided, no validation beyond URL parsing
- No network access except outbound HLS fetches via QMediaPlayer
- No credentials, tokens, or secrets stored anywhere
- File system access limited to user-selected fallback folder + `~/Desktop` for recording output

## 6. Configuration

All app-wide constants in `src/config/settings.py`:

| Setting | Default | Purpose |
|---|---|---|
| `DEFAULT_GRID_ROWS` | 4 | Grid rows |
| `DEFAULT_GRID_COLS` | 4 | Grid columns |
| `MIN_VISIBLE_TILES` | 6 | Min tiles shown |
| `MAX_VISIBLE_TILES` | 12 | Max tiles shown |
| `MAX_ACTIVE_PLAYERS` | 15 | Player concurrency cap |
| `LOW_LATENCY_MODE` | False | When True, QMediaPlayer notifyInterval=50ms (higher CPU) |
| `ANIMATION_DURATION_MS` | 8000 | Tile transition duration (ms) |
| `STREAM_CHECK_INTERVAL_MS` | 30000 | Stream health poll (ms) |
| `VIDEO_LOADING_TIMEOUT_MS` | 15000 | Fallback trigger threshold (ms) |

Hardware acceleration is environment-driven (Qt plugin level via `--hwa-enabled`), not per-player.

## 7. Build & Distribution

```bash
# Linux
pyinstaller VideoWall.spec --clean --noconfirm
# Output: dist/VideoWall/VideoWall

# macOS ARM64
pyinstaller VideoWall-arm64.spec --clean --noconfirm

# macOS Intel
pyinstaller VideoWall-intel.spec --clean --noconfirm
```

The spec bundles `m3u8-hosts.m3u8` and `resources/`. Runtime hook `scripts/qt_plugin_path_hook.py` sets GStreamer paths so the packaged binary finds system decoders on Linux.

## 8. Known Limitations

1. **No hot-plug monitor support** — must reconnect monitors before launch
2. **Wayland recording unsupported** — x11grab is X11-only
3. **No bezel compensation** — tiles align to screen edges, not physical bezel offsets
4. **No remote control** — no IPC, REST, or socket interface
5. **No playlist scheduling** — all streams run continuously; no time-based rotation
6. **Single playlist file** — `m3u8-hosts.m3u8` at project root, no UI for editing

## 9. Out of Scope (deliberately)

- Web UI / browser-based control
- Cloud sync
- DRM / paywall content
- Multi-machine clustering
- Network-coordinated synchronized playback across multiple PCs
- Plugin / effect system

## 10. Roadmap (vision-mode, NOT current state)

The following are aspirational and NOT implemented:
- Hot-plug monitor detection
- Wayland-compatible recording (PipeWire screencast)
- Bezel-aware layout math
- Headless control via REST/WebSocket
- Playlist scheduling / time-based rotation
- Bundled GStreamer plugins for fully self-contained Linux binary

---

## Appendix A: Entry Points

| Command | Calls | Notes |
|---|---|---|
| `python -m src` | `src/__main__.py` → `src.core.app:main` | Module execution |
| `python src/main.py` | `src/main.py` → `src.core.app:main` | Direct script |
| `./run-source-linux.sh` | venv setup + `python -m src` | Recommended |
| `./run-source-mac.sh` | venv setup + `python -m src` | macOS |
| `dist/VideoWall/VideoWall` | PyInstaller binary | Production |

## Appendix B: External Dependencies

**Linux (Ubuntu/Debian apt):**
```
python3 python3-pip python3-pyqt5
gstreamer1.0-plugins-base gstreamer1.0-plugins-good
gstreamer1.0-plugins-bad gstreamer1.0-libav
ffmpeg  # for screen recording
```

**Python (requirements.txt):**
```
PyQt5>=5.15.0
PyQt5-Qt5>=5.15.0
PyQt5-sip>=12.8.0
requests>=2.28.0
pyinstaller>=5.0   # build-time only
```

## Appendix C: Test Coverage

Test runner: `pytest`, plugins: `pytest-qt`, `pytest-cov`, `pytest-mock`
Test directory: `tests/`
Run: `pytest tests/` or `pytest --cov=src --cov-report=html tests/`

Current test count and coverage TBD by audit step.
