# AUDIT REPORT — VideoWall

**Date**: 2026-04-17
**Stack**: Python 3.8+ / PyQt5 5.15+ / GStreamer 1.0 (Linux) / ffmpeg x11grab (recording)
**Scope**: 22 Python files, 3 PyInstaller specs, 3 run scripts, 1 runtime hook
**Auditor**: Master Control (GLM-5.1)

---

## Executive Summary

| Severity | Count | Auto-fixed |
|----------|-------|------------|
| CRITICAL | 0 | 0 |
| HIGH | 2 | 2 |
| MEDIUM | 5 | 5 |
| LOW | 4 | 4 |
| **Total** | **11** | **11** |

**Files modified**: 8
- `src/core/recorder.py` — 3 fixes (platform guard, dimension validation, safe cleanup)
- `src/core/video_loader.py` — 2 fixes (dead code removal, recursion fix)
- `src/core/video_wall.py` — 1 fix (player cleanup on close)
- `src/core/layout_manager.py` — 1 fix (O(n^2) -> O(1) index lookup)
- `src/core/animator.py` — 1 fix (orphaned stylesheet timer)
- `src/utils/file_utils.py` — 1 fix (symlink loop guard)
- `VideoWall.spec` — 1 fix (icon parameter type)
- `VideoWall-arm64.spec` + `VideoWall-intel.spec` — 3 fixes each (datas, runtime_hooks, icon paths)

**Compilation**: All 22 Python files pass `py_compile`. Zero syntax errors.
**Tests**: `tests/` directory is empty (only `.gitkeep`). No test suite exists.

---

## Architecture Map

**src/core/app.py** — Application entry point. Arg parsing, Qt app creation, M3U8 loading, per-screen VideoWall instantiation. GStreamer plugin path setup for Linux.

**src/core/video_wall.py** — QMainWindow subclass. Orchestrates DisplayManager, VideoManager, LayoutManager, Animator, and ScreenRecorder. Owns refresh timer, stream health checks, keyboard shortcuts, and closeEvent cleanup.

**src/core/video_manager.py** — Manages QMediaPlayer instances (one per tile). Assigns streams/local videos to tiles, handles player errors, media status changes, retry logic with QTimer.singleShot guards against stack overflow.

**src/core/video_loader.py** — Loads M3U8 streams and local video files into QMediaContent. Manages loading timeouts, failed stream tracking, and recently-used video rotation.

**src/core/display_manager.py** — Grid layout setup, tile creation with screen-index offset, fullscreen toggle. Creates TileAnimator.

**src/core/layout_manager.py** — Applies random weighted layout patterns (varied, feature, columns, rows, mixed, asymmetric) enforcing MIN_VISIBLE_TILES..MAX_VISIBLE_TILES bounds. 2x2 max tile size cap.

**src/core/animator.py** — Random transition timer (5/15/30s intervals). Executes swap, resize, fullscreen takeover. Weighted selection with history-based anti-repetition.

**src/core/stream_tracker.py** — GlobalVideoAssigner for multi-monitor deduplication. Tracks per-monitor assignments, filters invalid local videos, manages recently-used rotation.

**src/core/recorder.py** — ffmpeg x11grab subprocess recording to ~/Desktop/MP4. Blinking REC indicator overlay. Start/stop/toggle/cleanup lifecycle.

**src/ui/video_tile.py** — QVideoWidget subclass with status label, loading progress bar, safe hide with RuntimeError guard.

**src/ui/dialogs.py** — Frameless Dark Neo Glass configuration dialog. Custom titlebar with drag-to-move, glass cards, stream/local video settings.

**src/ui/status_overlay.py** — Fade-in/out status message overlay using QPropertyAnimation on windowOpacity.

**src/ui/theme.py** — Centralized color palette and stylesheet generators. 850+ lines of QSS for the entire app.

**src/utils/file_utils.py** — M3U8 link parser, recursive video file scanner with hidden-file filtering.

**src/utils/stream_utils.py** — Stream validation (HEAD request), metadata retrieval, exponential backoff calculator.

---

## Findings & Auto-Fixes

### F-01: recorder.py — No platform guard for x11grab
**File**: `src/core/recorder.py:83-145`
**Severity**: HIGH
**Description**: `ffmpeg -f x11grab` only works on Linux X11. Calling `start()` on macOS/Windows or Wayland Linux silently spawns a failing ffmpeg process, leaks it, and shows a misleading REC indicator.
**Fix**: Added `_is_x11_available()` static method that checks `platform.system() == "Linux"`, no `WAYLAND_DISPLAY`, and `DISPLAY` is set. `start()` returns early with a print if unavailable. Also catches `FileNotFoundError` when ffmpeg is not in PATH.
**Before**: `start()` unconditionally builds x11grab command and spawns ffmpeg.
**After**: `start()` checks platform, validates dimensions > 0, and handles missing ffmpeg.

### F-02: recorder.py — Unsafe subprocess cleanup in stop()
**File**: `src/core/recorder.py:147-172`
**Severity**: HIGH
**Description**: `stop()` writes `b"q"` to stdin without checking if process is alive. If process already exited, `BrokenPipeError` is thrown. The exception handler then calls `self.process.kill()` on a dead process, potentially raising `OSError`. Also, if the Popen object's stdin was already closed, this crashes.
**Fix**: Check `self.process.poll() is None` before writing. Added `BrokenPipeError` and `OSError` catch blocks. All kill paths wrapped in try/except OSError.
**Before**: Blind stdin write, generic exception catch.
**After**: Poll check, BrokenPipeError/OSError handling, safe kill.

### F-03: video_loader.py — Dead code: _detect_gpu_capabilities()
**File**: `src/core/video_loader.py:55-177`
**Severity**: MEDIUM
**Description**: 120-line `_detect_gpu_capabilities()` method exists but is never called. Constructor comment says "detection will happen asynchronously" but no code triggers it. Also stores unused `gpu_info` dict and `current_gpu_index`. The method runs `nvidia-smi`, `rocm-smi`, `vainfo`, `vdpauinfo` via subprocess — all use list args (shell=False, safe), but the dead code bloats the module and imports `subprocess` unnecessarily.
**Fix**: Removed the entire method, `gpu_info` dict, `current_gpu_index`, and the `subprocess`/`platform` imports. Kept `player_count` which is used by `configure_player()`.
**Before**: 177 lines with dead GPU detection.
**After**: 25 lines in constructor, no subprocess dependency.

### F-04: video_loader.py — get_random_stream() infinite recursion
**File**: `src/core/video_loader.py:296-323`
**Severity**: MEDIUM
**Description**: When `exclude_list` contains ALL m3u8 links, the method clears `failed_streams` and recurses with the same `exclude_list`. Since `exclude_set` is rebuilt from `exclude_list + failed_streams`, and `failed_streams` is now empty but `exclude_list` still blocks everything, the recursion repeats infinitely (until Python recursion limit).
**Fix**: Rewrote to separate concerns — first filter by `exclude_list`, then prefer non-failed streams. If only failed streams remain, clear failures and pick one. No recursion.
**Before**: Recursive call `return self.get_random_stream(exclude_list)`.
**After**: Iterative fallback with `failed_streams.clear()` as last resort.

### F-05: video_wall.py — closeEvent doesn't release QMediaPlayer resources
**File**: `src/core/video_wall.py:168-195`
**Severity**: MEDIUM
**Description**: `closeEvent()` pauses players but doesn't clean up `_loading_timer` objects stored on players (orphaned QTimer), doesn't stop players (only pauses), and doesn't release media content (`setMedia(NullMedia)`). Players remain in memory until garbage collection, which may hold GStreamer pipeline resources.
**Fix**: Added explicit cleanup loop: stop loading timers, stop players, set NullMedia, clear player list.
**Before**: `pause_all_players()` only.
**After**: Timer cleanup + stop + NullMedia + clear.

### F-06: file_utils.py — os.walk follows symlinks (potential infinite loop)
**File**: `src/utils/file_utils.py:83`
**Severity**: LOW
**Description**: `os.walk(folder_path)` follows symlinks by default on some systems. If a user's video folder contains symlink cycles (common in NAS setups, e.g., `/mnt/media -> /mnt/media/subdir`), this scans infinitely.
**Fix**: Added `followlinks=False` to `os.walk()`.
**Before**: `os.walk(folder_path)`
**After**: `os.walk(folder_path, followlinks=False)`

### F-07: layout_manager.py — O(n^2) tile index lookups
**File**: `src/core/layout_manager.py:97,144,228,243`
**Severity**: LOW
**Description**: `self.tiles.index(tile)` is called inside loops that iterate over tiles. Each call is O(n), making the overall loop O(n^2). With 16 tiles max this is negligible, but it's a code quality issue.
**Fix**: Added `_tile_index = {id(t): i for i, t in enumerate(self.tiles)}` dict in constructor. Replaced all 4 `self.tiles.index(tile)` calls with `self._tile_index[id(tile)]`.
**Before**: `self.tiles.index(tile)` — O(n) per call.
**After**: `self._tile_index[id(tile)]` — O(1) per call.

### F-08: VideoWall.spec — icon parameter is list instead of string
**File**: `VideoWall.spec:35`
**Severity**: LOW
**Description**: `icon=['resources/icons/icon.png']` passes a list to PyInstaller's `icon` parameter, which expects a string. PyInstaller may handle this gracefully, but it's technically wrong.
**Fix**: Changed to `icon='resources/icons/icon.png'`.

### F-09: VideoWall-arm64.spec, VideoWall-intel.spec — Missing runtime_hooks and m3u8 data
**File**: `VideoWall-arm64.spec`, `VideoWall-intel.spec`
**Severity**: MEDIUM
**Description**: macOS specs don't include `runtime_hooks=['scripts/qt_plugin_path_hook.py']` (needed for Qt plugin path setup in bundled app), don't bundle `m3u8-hosts.m3u8` (needed for stream loading), use inconsistent `datas` (missing m3u8 file), and reference non-existent `resources/icon.icns` (actual icon is at `resources/icons/icon.png`). Also missing `PyQt5.QtNetwork` in hiddenimports and `optimize=0` setting.
**Fix**: Synchronized all 3 specs to match: added `('m3u8-hosts.m3u8', '.')` to datas, added `runtime_hooks`, added `PyQt5.QtNetwork`, added `optimize=0`, fixed icon paths to `resources/icons/icon.png`.

### F-10: animator.py — Orphaned stylesheet revert timer
**File**: `src/core/animator.py:277-278`
**Severity**: LOW
**Description**: `QTimer.singleShot(4000, ...)` fires a stylesheet revert after 4 seconds, but if the animation is cancelled (e.g., by `stop_timers_and_animations` or a new animation starting for the same tile), the timer still fires, reverting the stylesheet on a tile that may now be in a different state.
**Fix**: Replaced `QTimer.singleShot` with a tracked `QTimer` stored on the animation object. When an animation is stopped (in `start_animation`'s cancel-existing path), the timer is stopped and cleaned up.
**Before**: Anonymous `QTimer.singleShot(4000, ...)`.
**After**: Tracked `stylesheet_timer` on animation, cancelled on animation stop.

### F-11: recorder.py — Missing dimension validation
**File**: `src/core/recorder.py:100-102`
**Severity**: MEDIUM
**Description**: After the even-dimension rounding (`w = w if w % 2 == 0 else w - 1`), no check for w <= 0 or h <= 0. If the screen geometry reports 1px width, rounding gives 0, and ffmpeg fails with a confusing error.
**Fix**: Added `if w <= 0 or h <= 0: return` guard.
**Before**: No dimension check.
**After**: Early return with print if dimensions are invalid.

---

## Remaining Concerns (Not Auto-Fixed)

### RC-01: No test suite
**Severity**: HIGH (from a quality perspective, not a runtime bug)
The `tests/` directory is empty. All 22 source files have zero test coverage. This should be addressed before shipping.

### RC-02: VideoWall is a god class
`VideoWall` (video_wall.py) owns 5 subsystems (DisplayManager, VideoManager, LayoutManager, Animator, Recorder) and directly manages timers, keyboard events, and refresh orchestration. Consider extracting a coordinator pattern for long-term maintainability.

### RC-03: stream_tracker.GlobalVideoAssigner is instantiated but never used
`stream_tracker.py` defines `GlobalVideoAssigner` but no code in the codebase imports or instantiates it. The `VideoManager` handles stream assignment independently. This is dead code.

### RC-04: stream_utils functions are never called
`validate_stream()`, `get_stream_metadata()`, and `should_retry_stream()` in `stream_utils.py` are not imported anywhere. The dialog's "Skip Stream Testing" checkbox is always checked by default, and no code path calls these functions.

### RC-05: HARDWARE_ACCEL_STRATEGY="alternate" is defined but never applied
`settings.py` defines the strategy, but `video_loader.py`'s `configure_player()` only logs HWA status. No actual per-player strategy application exists. Qt's HWA is controlled at the environment/plugin level, not per-player in PyQt5.

### RC-06: Cross-platform recorder
Recording only works on Linux X11. macOS and Windows users get a silent no-op. Consider adding `avfoundation` (macOS) and `dshow`/`gdigrab` (Windows) capture support, or at minimum, a dialog warning.

### RC-07: run-source-linux.sh runs `python -m src.core.app` instead of `python -m src`
Line 70 of `run-source-linux.sh` runs `$PYTHON_CMD -m src.core.app` while the other scripts use `$PYTHON_CMD -m src`. Both work (src/core/app.py has `main()`), but the inconsistency could cause confusion.

---

## Security Assessment

- **Command injection**: All subprocess calls use list-form args (shell=False). Safe. `recorder.py` constructs ffmpeg command from trusted sources (screen geometry, DISPLAY env var). `video_loader.py` GPU detection (now removed) also used list-form. No `shell=True` anywhere.
- **Path traversal**: `get_video_files_recursively()` takes a user-chosen folder via QFileDialog — bounded by dialog. M3U8 paths resolved from app's own config file. Recorder output goes to ~/Desktop only. No arbitrary path injection vectors.
- **Untrusted URL handling**: M3U8 URLs are passed to `QUrl()` and `QMediaContent` — Qt handles these safely. No `eval()`/`exec()`/`os.system()` on URL content. `stream_utils.py` validates URLs via `urlparse()` before HEAD requests.
- **Secret leakage**: No hardcoded keys, tokens, passwords, or API credentials found.
- **_MEIPASS safety**: `settings.py` and `qt_plugin_path_hook.py` both check `hasattr(sys, '_MEIPASS')` before using it. Paths constructed with `os.path.join()`. Safe.

---

## Status

```
AUDIT: COMPLETE
FINDINGS: 11 (0 CRITICAL, 2 HIGH, 5 MEDIUM, 4 LOW)
AUTO-FIXED: 11 of 11
COMPILE CHECK: PASS (22/22 files)
TESTS: NOT PRESENT (empty tests/ directory)
SECURITY: CLEAN (no injection, no secrets, safe subprocess usage)
```

END OF LINE.
