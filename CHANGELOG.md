# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.6] - 2026-04-22 — Repo Pipeline Pass

End-to-end repo pipeline (12 steps) executed against the project. All steps pass; secrets audit clean.

### Added
- `pyproject.toml` — PEP-621 metadata + tool configs (black, isort, pylint, flake8, mypy, pytest, coverage)
- `.github/workflows/test.yml` — pytest matrix (Python 3.8-3.12) under Xvfb
- `.github/workflows/lint.yml` — black/isort/flake8/pylint
- `.github/ISSUE_TEMPLATE/bug_report.md` + `feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `AboutDialog` (src/ui/dialogs.py) — frameless glass panel with app info, MIT license, GitHub link
- "?" About button in `CustomTitleBar` wired to open `AboutDialog`
- `_is_x11_available()` platform guard in `ScreenRecorder` — fail-fast on macOS/Windows/Wayland
- `os.walk(followlinks=False)` symlink-loop guard in `file_utils.py`

### Changed
- `docs/PRD.md` rewritten to reflect actual current state (was vision-mode with inflated targets)
- `docs/API-DOCS.md` rewritten from 748B stub to full module API reference
- `docs/INSTALL.md` consolidated from `SETUP.md` (more thorough setup steps)
- `docs/ARCHITECTURE.md` synchronized with current source (removed stream_tracker section)
- `docs/DOCUMENTATION_INDEX.md` rewritten to reflect actual file list
- `docs/PROJECT_MANIFEST.json` updated with current stats (3488 LOC, 21 files)
- `src/config/settings.py` — fixed `ICON_PATH` (was `resources/icon.png`, now `resources/icons/icon.png`)
- `run-source-linux.sh` — entry point standardized to `python -m src` (was `python -m src.core.app`)
- `src/core/animator.py` — orphaned stylesheet revert timer now tracked + cancelled with animation
- `src/core/layout_manager.py` — replaced O(n²) `tiles.index()` with O(1) dict lookup
- `src/core/recorder.py` — safe subprocess cleanup (poll-before-write, BrokenPipeError/OSError handlers)
- `src/core/video_loader.py` — rewrote `get_random_stream()` to iterative fallback (was recursive, infinite-loop risk)
- `src/core/video_wall.py` — `closeEvent` properly stops players + sets NullMedia + clears list
- `src/ui/theme.py` — centralized ACCENT_TEAL_SELECTION, removed hardcoded #ef4444 references
- `VideoWall-arm64.spec`, `VideoWall-intel.spec` — added `runtime_hooks`, m3u8 in datas, PyQt5.QtNetwork hidden import, fixed icon paths
- `resources/screenshots/main-app-image.png` — replaced with current Neo-Noir Glass dialog screenshot showing About button

### Removed
- `src/core/stream_tracker.py` — `GlobalVideoAssigner` had zero call sites (147 LOC)
- `src/utils/stream_utils.py` — `validate_stream`, `get_stream_metadata`, `should_retry_stream` had zero call sites (89 LOC)
- `src/core/video_loader.py` — 120 lines of dead `_detect_gpu_capabilities()` (never called) + `gpu_info` dict + `current_gpu_index`
- `src/config/settings.py` — `VIDEO_BUFFER_SIZE`, `HARDWARE_DECODE_PRIORITY`, `HARDWARE_ACCEL_STRATEGY`, `DEFAULT_CONFIG` (no source readers)
- `src/core/animator.py` — `current_layout` dead attribute
- `src/core/recorder.py` — `recording_count` write-only attribute
- `src/ui/theme.py` — 3 dead theme functions (`get_video_tile_loading_stylesheet`, `get_dialog_card_stylesheet`, `get_dialog_main_stylesheet`)
- `src/core/video_manager.py` — `assigned_this_cycle` unused set
- Root: `AUDIT_REPORT.md` (regenerated), `BUILD_REPORT.md`, `implement.md`, `VERSION_MAP.md` (transient)
- `docs/CLAUDE.do` (typo file, was portfolio meta-doc not project doc)
- `dev/` folder (stale duplicates of docs/)
- `SETUP.md`, `ARCHITECTURE.md` (root duplicates consolidated into docs/)
- `dist_old/` (empty), `scripts/compile-build-dist-universal.sh.backup`
- ~30 unused PyQt5 imports across 11 files (formatter pass)

### Fixed
- F-01 HIGH: `recorder.start()` no longer silently leaks ffmpeg on non-X11 platforms
- F-02 HIGH: `recorder.stop()` handles already-dead process without crash
- F-03 MED: dead GPU detection bloat removed (-120 LOC, -1 subprocess import)
- F-04 MED: `get_random_stream()` infinite recursion when all streams excluded → iterative fallback
- F-05 MED: closeEvent now releases QMediaPlayer + GStreamer pipeline resources
- F-06 LOW: symlink-loop scan in `get_video_files_recursively`
- F-07 LOW: O(n²) tile index lookups → O(1)
- F-08 LOW: spec icon parameter type (list → str)
- F-09 MED: macOS specs missing runtime_hooks/m3u8/icon paths
- F-10 LOW: orphaned stylesheet revert timer survives animation cancellation
- F-11 MED: ffmpeg crash on zero-dimension capture (added dimension validation)

### Security
- Zero secrets in git history (verified by 3-scan audit: tracked .env, full-history pattern scan, HEAD credential strings)
- All subprocess calls use list-form args (no shell=True)
- No `eval()` / `exec()` / `os.system()` anywhere

### Stats
- LOC: 3716 → 3488 (-228, -6.1%)
- Files: 23 → 21 (-2 dead modules)
- flake8: clean (0 issues)
- compileall: clean (exit 0)

### Pipeline Reports
- `LINT_REPORT.md`, `AUDIT_REPORT.md`, `WIRE_AUDIT_REPORT.md`, `RESTYLE_REPORT.md`, `CODEREVIEW_REPORT.md`, `PIPELINE_LOG.md`

## [1.6.5] - 2026-03-14 17:10 UTC

### Fixed — Forensic Code Audit Remediation

**HIGH: Duplicate `InvalidMedia` handler removed (`video_manager.py`)**
- Second `elif status == QMediaPlayer.InvalidMedia:` block was unreachable dead code in `_handle_media_status_change`. Removed.

**HIGH: Recursive `retry_tile_stream()` call stack risk fixed (`video_manager.py`)**
- Direct synchronous recursion `self.retry_tile_stream(tile_index)` at line 240 replaced with `QTimer.singleShot(200, ...)` to prevent stack overflow under sustained stream failure conditions.

**HIGH: `shell=True` command injection risk removed (`video_loader.py`)**
- `subprocess.run(['nvidia-smi.exe', ...], shell=True)` on Windows path changed to direct list invocation without `shell=True`.

**HIGH: Unused `GlobalVideoAssigner` import removed (`display_manager.py`)**
- Dead import `from src.core.stream_tracker import GlobalVideoAssigner` removed. Class was never used in this module.

**MEDIUM: Bare `except:` clauses replaced with specific exception types (`video_loader.py`)**
- Two `except:` blocks in GPU detection code replaced with `except (subprocess.SubprocessError, FileNotFoundError, OSError):` to avoid swallowing `KeyboardInterrupt`, `SystemExit`, and other fatal signals.

**MEDIUM: Missing `requests` dependency added (`requirements.txt`)**
- `requests>=2.28.0` added. Was imported in `stream_utils.py` but absent from install requirements.

**MEDIUM: Bash script hardened (`run-source-linux.sh`)**
- Added `set -euo pipefail` to abort on any command failure.
- Quoted all `$PYTHON_CMD` variable expansions to handle paths with spaces.

**MEDIUM: Unused `import time` removed (`stream_utils.py`)**
- `time` module was imported but never referenced anywhere in the file.

**LOW: Maximize button wired to working callback (`dialogs.py`)**
- `CustomTitleBar.btn_maximize` was a dead control with no `clicked` connection. Added `_toggle_maximize()` method that calls `showMaximized()` / `showNormal()` and updates button icon.

---

## [1.6.4] - 2026-03-04 22:50 UTC

### Fixed - Video Playback in Packaged Binary
- Fixed videos stuck on "Loading" in PyInstaller binary by adding GStreamer plugin path discovery
- Root cause: packaged binary could not find system GStreamer element plugins (decoders, demuxers) needed by Qt multimedia backend
- Added `runtime_hooks` to `VideoWall.spec` pointing to `scripts/qt_plugin_path_hook.py`
- Rewrote `qt_plugin_path_hook.py` with Linux GStreamer support (`GST_PLUGIN_SYSTEM_PATH`, `GST_PLUGIN_PATH`, `GST_PLUGIN_SCANNER`)
- Added fallback GStreamer path setup in `src/core/app.py` for defense-in-depth
- Rebuilt and reinstalled binary to `/opt/VideoWall/`

## [1.6.3] - 2026-03-01 21:43 UTC

### Added - Linux Binary Build & System Install
- Built fresh PyInstaller binary from source using conda `video-wall` environment (Python 3.10, PyQt5 5.15.11)
- Fixed broken PyQt5 installation in conda env (force reinstall resolved missing QtCore)
- Installed binary to `/opt/VideoWall/` with symlink at `/usr/local/bin/videowall`
- Created Ubuntu `.desktop` entry at `/usr/share/applications/videowall.desktop` for app launcher integration
- Binary includes all bundled Qt libraries, M3U8 playlist, and resources (166MB total)

## [1.6.2] - 2026-02-13 00:00 UTC

### Added - Repository Structure Compliance (Repo Prep Phase 1)
- **`.gitignore`** - Comprehensive Python/PyQt5 gitignore with platform-specific exclusions
  - Python build artifacts, virtual environments, PyInstaller outputs
  - IDE files (.vscode, .idea, .DS_Store)
  - Platform-specific files (macOS, Linux, Windows)
  - Project-specific exclusions (archive/, backup/, dist_old/)
- **`requirements-dev.txt`** - Development dependency specification
  - Testing framework (pytest, pytest-cov, pytest-qt, pytest-mock)
  - Code quality tools (black, isort, pylint, flake8, mypy)
  - Documentation tools (sphinx, sphinx-rtd-theme)
  - Build tools (pyinstaller, wheel, setuptools, twine)
  - Debugging utilities (ipython, ipdb)

### Fixed
- Missing essential repository files now present
- README.md references to `requirements-dev.txt` now valid

## [1.6.1] - 2026-02-08 18:10 UTC

### Enhanced - Dark Neo Glass Design Depth
- **`src/ui/dialogs.py`** - Full frameless window overhaul:
  - Frameless window with `Qt.FramelessWindowHint` and translucent background
  - Custom titlebar with traffic-light window controls (red/yellow/green dots)
  - Drag-to-move support via custom `CustomTitleBar` widget
  - Floating panel effect with 16px float gap and rounded corners via outer QFrame
  - `QGraphicsDropShadowEffect` on outer frame (blur 48, offset 12)
  - Teal glow accent line (`GlowLine`) under title heading
  - Glass cards now have teal top-accent border (`border-top: 2px solid rgba(20,184,166,0.35)`)
  - Shadow effects now applied to GlassCard instances (previously defined but never called)
- **`src/ui/theme.py`** - New style helpers added:
  - `get_titlebar_stylesheet()`, `get_titlebar_button_close/minimize/maximize_stylesheet()`
  - `get_glow_line_stylesheet()` - teal horizontal glow separator
  - `get_glass_card_accent_stylesheet()` - card with teal top-accent border
  - `get_outer_frame_stylesheet()` - floating panel border and gradient

## [1.6.0] - 2026-02-08 22:30 UTC

### Added - Dark Neo Glass Theme Restyle
- **`src/ui/theme.py`** - Centralized Dark Neo Glass design token system with complete QSS stylesheet
  - 40+ color constants (backgrounds, typography, accents, borders, status, glass effects)
  - Border radius, scrollbar, and spacing tokens
  - `get_app_stylesheet()` - Full QApplication stylesheet covering all Qt widget types
  - 15+ component-specific stylesheet functions for video tiles, status overlays, dialogs, progress bars
- Glass card component (`GlassCard`) with gradient backgrounds and subtle borders
- Separator line component (`SeparatorLine`) with gradient fade effect
- Teal-to-cyan gradient accent system throughout all UI components

### Changed
- **`src/core/app.py`** - Applied global Dark Neo Glass stylesheet on QApplication initialization
- **`src/ui/dialogs.py`** - Complete restyle of configuration dialog:
  - Glass card sections for Stream Settings and Local Video Settings
  - Teal gradient primary action button
  - Ghost/secondary styled folder selection button
  - Themed checkboxes with gradient checked state
  - Warning labels with amber tint background
  - Section headers with teal accent color
- **`src/ui/video_tile.py`** - All hardcoded colors replaced with theme functions
  - Status labels use themed glass overlay styling
  - Progress bars use teal-to-cyan gradient fills
  - Error states use themed red with proper borders
- **`src/ui/status_overlay.py`** - Replaced inline hardcoded styles with theme functions
- **`src/core/display_manager.py`** - Central widget uses `BG_VOID` (#0a0b0e) from theme
- **`src/core/animator.py`** - Tile fade/transition styles use theme functions
- **`run-source-linux.sh`** - Rewritten for Python/PyQt5 (was incorrectly referencing npm/Electron)

### Theme Specifications
- Color palette: Void Black (#0a0b0e) through Card (#141518) with teal (#14b8a6) primary accent
- Typography: Inter/SF Pro/Roboto font stack, #e8e8ec primary text
- Scrollbars: 6px thin, dark themed with hover states
- Inputs: Dark background (#18191c) with teal focus glow
- Buttons: Teal-to-cyan gradient primary, glass secondary, red destructive
- Progress bars: Teal-to-cyan gradient fill on dark track
- Tooltips, menus, tabs, group boxes all themed

### Technical
- Zero hardcoded colors outside centralized theme system
- All component stylesheets generated from theme constants
- Pre-restyle backup archived at `archive/20260208_*.zip`

## [Unreleased]

### Changed
- Documentation standardization and reorganization
- Consolidated 22 documentation files into standardized structure
- Added comprehensive documentation index and navigation
- Moved outdated build documentation to archive
- Updated internal links to new documentation structure

### Added
- New documentation files:
  - `docs/DOCUMENTATION_INDEX.md` - Complete documentation navigation
  - `docs/QUICK_START.md` - 5-minute setup guide
  - `docs/FAQ.md` - Comprehensive FAQ and troubleshooting
  - `docs/TROUBLESHOOTING.md` - Detailed debugging guide
  - `docs/DEVELOPMENT.md` - Development workflow and standards
  - `docs/DEPLOYMENT.md` - Production deployment guide
  - `docs/WORKFLOW.md` - Development process documentation
  - `docs/ARCHITECTURE.md` - System architecture documentation
  - `docs/BUILD_COMPILE.md` - Build system guide

### Changed
- Renamed `CLAUDE.md` to `AGENTS.md` for broader AI assistant compatibility
- Updated main README.md with consolidated content and proper navigation
- Archived outdated Electron build system documentation
- Improved documentation cross-references and navigation

## [1.0.0] - 2024-09-XX

### Added
- Initial release of VideoWall
- Multi-monitor video wall display
- Support for M3U8 streaming
- Local video file playback
- PyQt5-based user interface
- Dynamic tile layout management
- Stream tracking and management
- Hardware acceleration support
- Cross-platform compatibility (Windows, macOS, Linux)

### Features
- Real-time video streaming from M3U8 sources
- Local video file integration
- Multi-monitor support with windowed mode
- Dynamic grid layout with effects
- Stream fallback mechanisms
- Video controls and overlays
- Status monitoring and error handling

### Technical
- Built with Python and PyQt5
- Modular architecture with core, UI, and utils
- Configuration management
- Video processing and display management
- Cross-platform build scripts