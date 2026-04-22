# Architecture

## High-Level Overview

Video Wall is a desktop application built on PyQt5. It creates one fullscreen `QMainWindow` per connected display, each running independent video players, layout managers, and animation timers. All windows share the same `QApplication` event loop and the same pool of stream URLs loaded at startup.

```
QApplication
├── VideoWall (screen 0)       QMainWindow
│   ├── DisplayManager         Grid layout + tile creation
│   ├── VideoManager           Player pool + stream assignment
│   ├── LayoutManager          Pattern selection + tile placement
│   ├── TileAnimator           Animation scheduling + geometry animation
│   └── ScreenRecorder         ffmpeg x11grab capture
└── VideoWall (screen 1)       same structure
```

There is no server, no IPC between windows, and no persistent state file. Configuration lives in `settings.py` and the startup dialog. Stream URLs come from `m3u8-hosts.m3u8`.

## Component Breakdown

### `src/core/app.py` — Entry Point

Handles CLI argument parsing (`--hwa-enabled`), loads the M3U8 playlist, shows the startup config dialog, then iterates `app.screens()` to create one `VideoWall` per monitor. Also sets the GStreamer plugin path on Linux for packaged binary compatibility.

### `src/core/video_wall.py` — Main Window

The `VideoWall` class extends `QMainWindow`. It owns and wires together all the subsystems. Key responsibilities:
- Sets the window to fullscreen on its assigned `QScreen`
- Handles keyboard events (Esc, F11, Right arrow, R, Ctrl+Q)
- Runs a 30-second health check timer (`stream_check_timer`) that scans for stalled players
- Exposes `refresh_all_videos()` which the animator calls to trigger layout changes

### `src/core/display_manager.py` — Grid and Tiles

Creates the `QGridLayout` and instantiates `VideoTile` objects. The grid defaults to 4x4, creating 16 tiles total — but only 6 to 12 are visible at any time depending on the active layout pattern. Also handles fullscreen toggle (windowed vs fullscreen).

### `src/core/video_manager.py` — Player Lifecycle

Creates one `QMediaPlayer` per tile at startup. On each content refresh cycle:
1. Clears the `tried_urls` tracking state
2. Shuffles the available stream pool
3. Assigns unique URLs to visible tiles (no duplicates per cycle)
4. Starts a 15-second loading timeout per player
5. Falls back to a local video on timeout, error, or when streams run out

Tracks `using_local_video[tile_index]` per tile so the health check skips local video tiles.

### `src/core/video_loader.py` — Media Loading

Wraps `QMediaPlayer` configuration and media loading. Handles:
- Muting all players (video wall is silent)
- Setting `notifyInterval` to 100ms for smooth status updates
- Loading M3U8 URLs via `QMediaContent(QUrl(url))`
- Loading local videos via `QUrl.fromLocalFile(path)`
- Detecting GPU capabilities (CUDA via `nvidia-smi`, VAAPI via `vainfo`, Metal on macOS) — detection result is informational only since PyQt5 doesn't expose per-player HWA control directly
- Tracking `failed_streams` (a set of URLs that errored) so they're excluded from future cycles

### `src/core/layout_manager.py` — Layout Patterns

Selects and applies grid layouts. The algorithm:
1. Picks a random pattern from 6 options
2. Removes all tiles from the grid and hides them
3. Places tiles back using an occupancy grid (`occupied_cells[row][col]`) to prevent overlaps
4. Stops at `MAX_VISIBLE_TILES` (12)
5. Retries up to 5 times if the visible count falls outside the 6-12 range
6. Falls back to a uniform 1x1 grid if all retries fail

Tile sizes are capped at 2x2 to ensure enough tiles remain visible. The `feature` pattern places one 2x2 tile first at a random position, then fills the rest normally.

### `src/core/animator.py` — Transition Scheduler

`TileAnimator` extends `QObject` and owns a `QTimer` that fires on a random interval (5, 15, or 30 seconds). On each tick it executes a pre-chosen transition type:

- **resize** (90% probability) — calls `video_wall.refresh_all_videos()`, which reshuffles the layout and reassigns content
- **swap** (10% probability) — picks two random visible tiles, moves them in the grid layout, then runs `QPropertyAnimation` on each tile's geometry
- **full_screen** and **refresh** are disabled (0% weight) to maintain the 6-tile minimum

Animation uses `QPropertyAnimation` on the `geometry` property with 8-second duration and one of three easing curves (InOutSine, OutCubic, InOutQuad). The next transition type is chosen at the end of each cycle to avoid back-to-back repeats.

### Multi-Monitor Stream Distribution
~~`stream_tracker.py`~~ removed in 2026-04-17 refactor — `GlobalVideoAssigner` had zero call sites. Each `VideoManager` (one per monitor) handles its own stream/local-video assignment independently. There is no cross-monitor coordination; with enough streams in the playlist, overlap is rare. If you need strict cross-monitor uniqueness, reintroduce a coordinator at the `app.py` level and pass it into each `VideoWall`.

### `src/core/recorder.py` — Screen Recorder

`ScreenRecorder` spawns an `ffmpeg` subprocess using `x11grab` to capture the window's screen region. Output goes to `~/Desktop/VideoWall-Recording-YYYYMMDD_HHMMSS.mp4`. Graceful shutdown sends `q` to ffmpeg stdin; if that times out after 5 seconds, it escalates to SIGINT then SIGKILL. `RecordingIndicator` is a blinking red `QLabel` overlay shown during recording.

### `src/ui/video_tile.py` — Tile Widget

`VideoTile` extends `QVideoWidget`. Each tile has:
- A centered `QLabel` for status messages (loading, error, stream name)
- A `QProgressBar` for the loading animation (animated via a 100ms timer)
- Logic to reposition both overlays on resize

### `src/ui/dialogs.py` — Startup Config Dialog

`LocalVideoDialog` is a frameless `QDialog` with a custom titlebar (`CustomTitleBar`) that supports drag-to-move. Built with the Dark Neo Glass design system. Collects:
- Skip stream testing flag
- Auto-record flag
- Local video folder path

### `src/ui/theme.py` — Design Token System

Centralizes all visual constants (colors, radii, font sizes) and generates QSS stylesheet strings. No hardcoded colors exist outside this file. Key tokens:
- `BG_VOID` (#0a0b0e) — window/background black
- `BG_CARD` (#141518) — card/panel background
- `ACCENT_TEAL` (#14b8a6) — primary accent
- `TEXT_PRIMARY` (#e8e8ec) — main text

### `src/utils/`

- `file_utils.py` — parses `m3u8-hosts.m3u8` (skips comments, deduplicates, basic URL validation) and recursively scans folders for video files (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`, `.3gp`). Uses `os.walk(followlinks=False)` to prevent symlink-loop scans.
- ~~`stream_utils.py`~~ — REMOVED (2026-04-17 refactor). All 3 functions (`validate_stream`, `get_stream_metadata`, `should_retry_stream`) had zero call sites.

## Data Flow

```
startup
  m3u8-hosts.m3u8 ──► get_all_m3u8_links() ──► m3u8_links[]
  dialog ──► config dict (folder_path, flags)
  get_video_files_recursively(folder_path) ──► local_videos[]

per monitor
  VideoWall.__init__
    ├── DisplayManager: create 16 VideoTile widgets in 4x4 grid
    ├── VideoManager: create 16 QMediaPlayer instances, connect to tiles
    ├── LayoutManager: select and apply initial layout
    └── TileAnimator: start random interval timer

layout refresh cycle (every 5-30s)
  TileAnimator.trigger_random_action()
    └── VideoWall.refresh_all_videos()
          ├── animator.stop_timers_and_animations()
          ├── video_manager.pause_all_players()
          ├── layout_manager.apply_random_layout()
          │     └── hide/show tiles, place in QGridLayout with row/col spans
          ├── video_manager.assign_content_to_tiles()
          │     ├── shuffle available streams
          │     ├── load_stream() → QMediaPlayer.setMedia() + timeout timer
          │     └── _fallback_to_local_video() when streams exhausted/fail
          ├── video_manager.resume_visible_players() [500ms delay]
          └── animator.start_random_timer()

stream failure path
  QMediaPlayer.error signal
    └── video_manager._handle_player_error()
          └── retry_tile_stream()
                ├── try another URL (up to 3 attempts)
                └── _fallback_to_local_video()

health check (every 30s)
  VideoWall.check_stream_health()
    └── for each visible non-local tile: if not PlayingState → retry_tile_stream()
```

## Key Design Decisions

**One window per monitor, not one window spanning all monitors.** Each `VideoWall` instance is positioned and fullscreened to its `QScreen`. This gives independent layout cycling per screen and avoids cross-screen tearing.

**Pool-based tile creation.** 16 tiles are always instantiated. The layout manager hides/shows them and adjusts their grid spans, rather than creating/destroying widgets on each cycle. This avoids the overhead and flicker of widget construction.

**Occupancy grid for placement.** `LayoutManager` tracks which grid cells are filled using a 2D boolean array. This prevents overlapping tiles when placing multi-cell spans and is O(rows*cols) to check.

**No duplicate streams per cycle.** `VideoManager.assign_content_to_tiles()` maintains an `assigned_this_cycle` set so two visible tiles never play the same stream simultaneously.

**Timeout-based fallback, not error-only.** Each player gets a 15-second loading timer. Streams that never emit an error but also never buffer (common with some HLS sources) are caught and redirected to local video.

**Centralized theme system.** All QSS is generated from token constants in `theme.py`. This makes global style changes (color, radius, font) a single-file edit.

## Directory Structure

```
video-wall/
├── src/                    Source code package
│   ├── core/               Business logic (no UI dependencies except VideoWall/DisplayManager)
│   ├── ui/                 Qt widgets and theming
│   ├── utils/              Pure utility functions
│   └── config/             App-wide constants
├── m3u8-hosts.m3u8         Stream playlist (user-editable)
├── resources/              Icons and screenshots (bundled into binary)
├── scripts/                Build utilities and PyInstaller runtime hooks
├── build_resources/        Build-time assets (platform icons, screenshots)
├── docs/                   Extended documentation
├── dist/                   PyInstaller output (not committed)
├── archive/                Pre-restyle and pre-build backups
├── VideoWall.spec          PyInstaller build configuration
└── run-source-*.sh/.bat    Platform launch scripts
```
