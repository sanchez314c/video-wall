# LINT REPORT — VideoWall

Date: 2026-04-17

## Tools Run

| Tool | Version | Status |
|------|---------|--------|
| black | 26.3.1 | Reformatted 23 files |
| isort | 8.0.1 | Fixed 14 files |
| autoflake | N/A | Skipped (PEP 668 blocked pip install) |
| flake8 | 7.3.0 | 0 remaining issues |
| pylint | N/A | Not installed (system package not available) |
| mypy | 1.20.0 | 1 remaining issue (types-requests stubs) |

## Files Reformatted by black (23)

All `src/` Python files were reformatted to line-length=100, matching pyproject.toml config.

## Files Fixed by isort (14)

Import ordering aligned with black profile. Affected files:
- `src/main.py`, `src/core/app.py`, `src/core/animator.py`, `src/core/layout_manager.py`
- `src/core/video_wall.py`, `src/core/video_loader.py`, `src/core/video_manager.py`
- `src/core/recorder.py`, `src/core/display_manager.py`, `src/core/stream_tracker.py`
- `src/ui/video_tile.py`, `src/ui/dialogs.py`, `src/ui/status_overlay.py`
- `src/utils/stream_utils.py`

## Manual Fixes Applied

### F401 — Unused Imports Removed (11 files, ~30 imports)

| File | Removed Imports |
|------|-----------------|
| `src/core/app.py:10` | `QFontDatabase` |
| `src/core/display_manager.py:6` | `QMainWindow` |
| `src/core/layout_manager.py:7-8` | `QTimer`, `QGridLayout` |
| `src/core/recorder.py:11` | `Qt` |
| `src/core/video_loader.py:9` | `sys` |
| `src/core/video_loader.py:12` | `QMediaPlayer` |
| `src/core/video_loader.py:14` | `HARDWARE_ACCEL_STRATEGY`, `HARDWARE_DECODE_PRIORITY`, `VIDEO_BUFFER_SIZE` |
| `src/core/video_loader.py:21` | `get_all_m3u8_links`, `get_video_files_recursively` |
| `src/core/video_manager.py:7` | `QUrl` |
| `src/core/video_manager.py:8` | `QMediaContent` |
| `src/core/video_wall.py:5-7` | `os`, `random`, `sys` |
| `src/core/video_wall.py:10-11` | `QMediaContent`, `QGridLayout`, `QMessageBox`, `QWidget` |
| `src/core/video_wall.py:13` | `DEFAULT_GRID_COLS`, `DEFAULT_GRID_ROWS` (entire import line) |
| `src/ui/dialogs.py:6` | `QPoint` |
| `src/ui/dialogs.py:7` | `QFont` |
| `src/ui/dialogs.py:23` | `ACCENT_BLUE`, `BG_CARD`, `BG_TERTIARY`, `BG_VOID`, `BORDER_LIGHT`, `RADIUS_CARD`, `RADIUS_XL`, `TEXT_DIM`, `TEXT_HEADING`, `TEXT_PRIMARY` |
| `src/ui/status_overlay.py:7` | `QColor`, `QFont`, `QPainter`, `QPen` |
| `src/ui/status_overlay.py:8` | `QWidget` |
| `src/ui/video_tile.py:6` | `QEasingCurve`, `QPropertyAnimation` |
| `src/ui/video_tile.py:7` | `QPalette` |

### F541 — f-string Without Placeholders (12 instances)

Converted to regular strings in:
- `src/core/animator.py` (9 instances): lines 46, 77, 85, 88, 91, 94, 114, 325, 364
- `src/ui/theme.py` (2 instances): lines 482, 492
- `src/core/video_manager.py` (1 instance): line 244

### F841 — Unused Variable (1 instance)

- `src/core/animator.py:287` — removed unused `tile_id` assignment in `animation_finished()`

### E731 — Lambda Assignment (2 instances)

- `src/core/video_manager.py:115` — converted to local `_stream_timeout` def
- `src/core/video_manager.py:239` — converted to local `_retry_timeout` def

### E302 — Missing Blank Lines (1 instance)

- `src/core/video_loader.py:17` — added 2 blank lines before `class VideoLoader:` (caused by import removal)

### Config Fix

- `pyproject.toml` — `mypy python_version` changed from `"3.8"` to `"3.9"` (3.8 unsupported by mypy 1.20+)

## Remaining Issues

### flake8: 0 issues

### mypy: 1 issue

- `src/utils/stream_utils.py:8` — `Library stubs not installed for "requests" [import-untyped]`
  - Fix: `pip install types-requests` (optional, does not affect runtime)

### pylint: Not Run

pylint not available as system package. Install via `pip install pylint` in a venv for future runs.

## Status

DONE

All auto-fixable issues resolved. flake8 passes clean. Only remaining issue is a mypy types-requests stub (non-blocking, no code change needed).
