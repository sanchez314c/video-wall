# VideoWall — Module API Reference

Internal API documentation for the VideoWall codebase. All public classes and functions exposed by each module, intended for contributors extending or embedding the application.

VideoWall is a PyQt5 desktop application — there is **no public REST or RPC API**. This document covers internal Python module interfaces.

---

## src.core.app

Entry point. Bootstraps QApplication, parses CLI args, shows startup dialog, spawns one `VideoWall` per detected screen.

### `main() -> int`
Initialize and run the application. Returns app exit code.

**CLI args**:
- `--hwa-enabled` — sets `VIDEOWALL_HWA_ENABLED=1` env var, hint Qt to use platform decoders

**Side effects**:
- Sets `GST_PLUGIN_SYSTEM_PATH` on Linux if unset (probes `/usr/lib/x86_64-linux-gnu/gstreamer-1.0`, `/usr/lib/gstreamer-1.0`, `/usr/lib64/gstreamer-1.0`)
- Loads `m3u8-hosts.m3u8` from project root or `_MEIPASS` (PyInstaller bundle)
- Applies Dark Neo Glass stylesheet via `theme.get_app_stylesheet()`

---

## src.core.video_wall

### `class VideoWall(QMainWindow)`

Per-monitor main window. One instance per detected screen.

**Constructor**: `VideoWall(app, m3u8_links, local_videos, screen)`
- `app: QApplication` — shared event loop
- `m3u8_links: list[str]` — full playlist
- `local_videos: list[str]` — fallback file paths
- `screen: QScreen` — target monitor

**Public attributes**:
- `display_manager: DisplayManager`
- `video_manager: VideoManager`
- `layout_manager: LayoutManager`
- `animator: TileAnimator`
- `recorder: ScreenRecorder`

**Key bindings**:
| Key | Slot |
|---|---|
| Right Arrow | `manual_layout_refresh()` |
| `R` | `recorder.toggle()` |
| `F11` / `Alt+F` | `toggle_fullscreen()` |
| `Esc` / `Ctrl+Q` | `close()` |

---

## src.core.display_manager

### `class DisplayManager`
Owns the `QGridLayout`, creates `VideoTile` widgets, handles fullscreen toggling per screen.

**Methods**:
- `create_tiles(rows: int, cols: int) -> list[VideoTile]`
- `clear_tiles()`
- `apply_fullscreen(enabled: bool)`

---

## src.core.video_manager

### `class VideoManager`
Player lifecycle controller. Bounded by `MAX_ACTIVE_PLAYERS`. Owns stream-to-tile assignment, fallback switching, and retry timing.

**Key methods**:
- `assign_streams_to_tiles(tiles: list[VideoTile], streams: list[str])`
- `retry_tile_stream(tile_index: int)` — scheduled via `QTimer.singleShot` to avoid recursion
- `switch_to_fallback(tile_index: int)` — pulls from `local_videos`

**Signal handlers**:
- `_handle_media_status_change(status)` — wired to each `QMediaPlayer.mediaStatusChanged`
- `_handle_player_error(error)` — wired to `QMediaPlayer.error`

---

## src.core.video_loader

### `class VideoLoader`
Configures individual `QMediaPlayer` instances. Reads `LOW_LATENCY_MODE` and `VIDEO_LOADING_TIMEOUT_MS` from settings. Tracks player count for `MAX_ACTIVE_PLAYERS` enforcement and rotates recently-used local videos to avoid repetition. Hardware acceleration is environment-driven (Qt plugin level, set by `--hwa-enabled` flag in `app.py`), not per-player.

**Key methods**:
- `load_media(player: QMediaPlayer, url: str)`
- `get_random_stream(exclude_list: list[str]) -> str` — iterative fallback (no recursion); clears `failed_streams` as last resort.
- `get_random_local_video(exclude_list: list[str]) -> str` — recently-used rotation

---

## src.core.layout_manager

### `class LayoutManager`
Layout pattern engine. Picks one of 6 patterns (`varied`, `feature`, `columns`, `rows`, `mixed`, `asymmetric`) and computes tile geometry within the grid.

**Methods**:
- `choose_pattern() -> str`
- `apply_pattern(pattern: str, tiles: list[VideoTile], grid_rect: QRect)`
- `compute_tile_rects(pattern: str, grid_rect: QRect) -> list[QRect]`

---

## src.core.animator

### `class TileAnimator`
Schedules layout transitions and runs `QPropertyAnimation` for tile geometry changes.

**Behavior**:
- Fires every 5 / 15 / 30 sec (random)
- 90% of fires: layout reshuffle (apply new pattern)
- 10% of fires: tile swap (animated geometry crossfade)
- Animation duration: `settings.ANIMATION_DURATION_MS` (default 8000ms)
- Easing curve: `QEasingCurve.InOutCubic`

**Methods**:
- `start()` / `stop()`
- `animate_to_layout(target_rects: list[QRect])`

---

## src.core.recorder

### `class ScreenRecorder`
ffmpeg `x11grab` wrapper with blinking REC indicator overlay.

**Methods**:
- `start()` — spawns ffmpeg subprocess
- `stop()` — sends SIGINT, waits for finalize
- `toggle()`
- `is_recording() -> bool`

**Output path**: `~/Desktop/VideoWall-Recording-YYYYMMDD_HHMMSS.mp4`

**Linux X11 only.** Wayland NOT supported (no x11grab).

---

## src.ui.video_tile

### `class VideoTile(QWidget)`
Composite widget: `QVideoWidget` + `StatusOverlay` + loading indicator. Each tile is one cell in the grid.

**Slots**:
- `set_player(player: QMediaPlayer)`
- `set_status(text: str)`
- `set_loading(loading: bool)`

---

## src.ui.dialogs

### `class LocalVideoDialog(QDialog)`
Frameless Dark Neo Glass startup dialog. User picks fallback folder, toggles stream pre-testing, enables auto-recording.

**Methods**:
- `exec_() -> int` — standard QDialog modal exec
- `get_results() -> dict` — returns `{use_local_videos, folder_path, skip_stream_testing, record_streams}`

---

## src.ui.status_overlay

### `class StatusOverlay(QWidget)`
Per-tile state badge widget. Renders text in the corner of a `VideoTile`.

---

## src.ui.theme

Design token system + QSS stylesheet builder. **848 LOC** — the visual identity layer.

**Key functions**:
- `get_app_stylesheet() -> str` — full QSS for the QApplication
- `get_dialog_stylesheet() -> str` — frameless dialog QSS
- `get_tile_stylesheet() -> str` — per-tile QSS

**Color tokens** (representative):
- `BG_VOID = "#0A0A0F"` — void black
- `BG_GLASS = "rgba(15, 15, 25, 0.85)"` — frosted panel
- `ACCENT_TEAL = "#14B8A6"`
- `TEXT_PRIMARY = "#E5E7EB"`

---

## src.utils.file_utils

### `get_all_m3u8_links(path: str) -> list[str]`
Parse an `.m3u8` playlist file. Strips comments (lines starting with `#`), trims whitespace, prepends `https://` to lines without a protocol.

### `get_video_files_recursively(folder: str) -> list[str]`
Walk a folder, return all video files (extensions: `.mp4 .avi .mov .mkv .webm .m4v`). Uses `os.walk(followlinks=False)` to prevent symlink loops.

---

## src.config.settings

Module-level constants. No classes, no functions. See [PRD §6](PRD.md#6-configuration) for the full list.

**Key constants**:
- `DEFAULT_GRID_ROWS`, `DEFAULT_GRID_COLS` — grid dimensions
- `MIN_VISIBLE_TILES`, `MAX_VISIBLE_TILES` — visible tile bounds
- `MAX_ACTIVE_PLAYERS` — player concurrency cap
- `LOW_LATENCY_MODE` — when True, sets QMediaPlayer notify interval to 50ms
- `ANIMATION_DURATION_MS`, `STREAM_CHECK_INTERVAL_MS`, `VIDEO_LOADING_TIMEOUT_MS` — timers
- `BASE_DIR`, `RESOURCE_DIR`, `ICON_PATH` — runtime paths (PyInstaller-aware via `sys._MEIPASS`)

---

## Environment Variables (consumed)

| Variable | Read by | Purpose |
|---|---|---|
| `VIDEOWALL_HWA_ENABLED` | `video_loader` | Hardware acceleration toggle (set by `--hwa-enabled` arg) |
| `GST_PLUGIN_SYSTEM_PATH` | Qt multimedia (Linux) | GStreamer plugin search path |
| `DISPLAY` | `recorder` | Required for x11grab capture |
| `QT_QPA_PLATFORM` | Qt itself | Platform plugin (`xcb`, `wayland`) |
