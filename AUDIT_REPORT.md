# VideoWall — Code Quality Audit Report

**Date:** 2026-03-14
**Auditor:** Master Control (forensic automated audit)
**Scope:** Full source audit of `/media/heathen-admin/RAID/Development/Projects/portfolio/video-wall/src/`
**Status:** All CRITICAL/HIGH/MEDIUM findings remediated. LOW findings documented.

---

## Audit Summary

| Severity | Found | Fixed | Deferred |
|----------|-------|-------|----------|
| CRITICAL | 0 | — | 0 |
| HIGH | 4 | 4 | 0 |
| MEDIUM | 4 | 4 | 0 |
| LOW | 1 | 1 | 0 |
| **Total** | **9** | **9** | **0** |

No known CVEs detected via `pip-audit` against `requirements.txt`.

---

## Finding Details

### HIGH — Duplicate `InvalidMedia` handler (dead code + double retry trigger)
**File:** `src/core/video_manager.py` lines 314–325
**Description:** `_handle_media_status_change` contained two separate `elif status == QMediaPlayer.InvalidMedia:` blocks. Python's `elif` chain only evaluates the first matching arm. The second block was completely unreachable dead code. Additionally, it masked any future intent to handle `InvalidMedia` differently in a second context.
**Risk:** Confusing maintenance surface; future developer may believe the second block runs (it never does).
**Fix:** Removed the second duplicate `elif status == QMediaPlayer.InvalidMedia` block. The `StalledMedia` handler between them was preserved correctly.

---

### HIGH — Synchronous recursive `retry_tile_stream()` call risks call stack overflow
**File:** `src/core/video_manager.py` line 240
**Description:** `retry_tile_stream()` called itself synchronously (`self.retry_tile_stream(tile_index)`) when a stream failed to load. On network failure with many streams in the `tried_urls` exclusion set all marked failed, this path could recurse into itself rapidly enough to exhaust the Python call stack (default ~1000 frames), crashing the process with `RecursionError`.
**Risk:** Application crash under sustained stream failure conditions.
**Fix:** Replaced the direct call with `QTimer.singleShot(200, lambda: self.retry_tile_stream(tile_index))` to return control to the event loop between retry attempts, breaking the recursion.

---

### HIGH — `shell=True` in subprocess call on Windows (command injection risk)
**File:** `src/core/video_loader.py` line 144
**Description:** `subprocess.run(['nvidia-smi.exe', ...], shell=True)` was used on Windows. When `shell=True` is combined with a list argument, the behavior is platform-dependent and counterintuitive (on Windows, the list is re-joined into a string before being passed to `cmd.exe`). More critically, `shell=True` opens the door to command injection if any argument were ever to incorporate user-controlled or environment-sourced input.
**Risk:** Command injection vulnerability surface; incorrect cross-platform behavior.
**Fix:** Removed `shell=True`. The command is a static list with no user input, so direct `Popen`-style execution is both correct and safe.

---

### HIGH — Unused import `GlobalVideoAssigner` in display_manager.py
**File:** `src/core/display_manager.py` line 10
**Description:** `from src.core.stream_tracker import GlobalVideoAssigner` was present but `GlobalVideoAssigner` was never instantiated, referenced, or used anywhere in `DisplayManager`. This is confirmed dead import.
**Risk:** Unnecessary module load on startup; misleads readers into thinking multi-monitor tracking is active inside `DisplayManager` (it is not — it lives in `VideoManager`).
**Fix:** Removed the import.

---

### MEDIUM — Bare `except:` clauses silently swallow all exceptions
**File:** `src/core/video_loader.py` lines 137, 154 (pre-fix)
**Description:** Two `except:` blocks (macOS `arch` detection and Windows `nvidia-smi.exe` detection) used naked `except:` which catches `BaseException`, including `SystemExit`, `KeyboardInterrupt`, and `MemoryError`. This prevents clean shutdown and hides unexpected errors.
**Risk:** Silent failure masks real problems; interferes with SIGINT handling in GPU detection path.
**Fix:** Replaced both with `except (subprocess.SubprocessError, FileNotFoundError, OSError):` — the specific exceptions that can actually be raised by these subprocess calls.

---

### MEDIUM — `requests` missing from `requirements.txt`
**File:** `requirements.txt`
**Description:** `src/utils/stream_utils.py` imports `requests` for `validate_stream()` and `get_stream_metadata()`. However, `requests` was absent from `requirements.txt`. Any fresh environment install would fail at runtime when these functions are called.
**Risk:** Silent dependency gap; `ImportError` at runtime on clean installs.
**Fix:** Added `requests>=2.28.0` to `requirements.txt`.

---

### MEDIUM — `run-source-linux.sh` missing `set -euo pipefail`; unquoted `$PYTHON_CMD`
**File:** `run-source-linux.sh`
**Description:** The script had no `set -euo pipefail`, meaning individual command failures (e.g., pip install failing mid-way) would not abort execution — the script would continue silently into a broken state. Additionally, `$PYTHON_CMD` was unquoted in several locations, which would cause word splitting if the path contained spaces.
**Risk:** Silent partial failures; path-with-spaces breakage.
**Fix:** Added `set -euo pipefail` as line 2. Quoted all `$PYTHON_CMD` expansions to `"$PYTHON_CMD"`.

---

### MEDIUM — Unused import `time` in `stream_utils.py`
**File:** `src/utils/stream_utils.py` line 1
**Description:** `import time` was present at the top of the file. `time` is never referenced anywhere in the module. `random` is used in `should_retry_stream()`.
**Risk:** Minor — unnecessary import adds to module load time; misleads readers looking for usage.
**Fix:** Removed `import time`.

---

### LOW — Maximize button in `CustomTitleBar` had no connected callback (dead widget)
**File:** `src/ui/dialogs.py`
**Description:** `self.btn_maximize` was created, styled, and added to the titlebar layout, but `clicked` was never connected to any slot. Clicking it did nothing, which is confusing UX.
**Risk:** Broken UI control; user confusion.
**Fix:** Connected `clicked` to a new `_toggle_maximize()` method that calls `showMaximized()` / `showNormal()` and updates the button icon to reflect state (`□` vs `▣`).

---

## Dependency Vulnerability Scan

```
pip-audit --requirement requirements.txt
Result: No known vulnerabilities found
```

All pinned ranges (`PyQt5>=5.15.0`, `requests>=2.28.0`, etc.) are clear of known CVEs as of audit date 2026-03-14.

---

## Files Modified

| File | Change |
|------|--------|
| `src/core/video_manager.py` | Removed duplicate `InvalidMedia` handler; guarded recursive retry with `QTimer` |
| `src/core/video_loader.py` | Removed `shell=True` from Windows subprocess; replaced bare `except:` with specific exception types |
| `src/core/display_manager.py` | Removed unused `GlobalVideoAssigner` import |
| `src/utils/stream_utils.py` | Removed unused `import time` |
| `requirements.txt` | Added `requests>=2.28.0` |
| `run-source-linux.sh` | Added `set -euo pipefail`; quoted all `$PYTHON_CMD` expansions |
| `src/ui/dialogs.py` | Wired maximize button to `_toggle_maximize()` method |

---

## Backup Location

Pre-fix backups stored at:
`/media/heathen-admin/RAID/Development/Projects/portfolio/video-wall/backup/audit_20260314_170727/`

---

## Remaining Notes (No Action Required)

- `stream_utils.py` — `validate_stream()` and `get_stream_metadata()` are never called from any live code path (stream testing is skipped by default per dialog checkbox). The functions are present as optional tooling. No removal warranted without User direction.
- `GlobalVideoAssigner` in `stream_tracker.py` — the class itself is sound and used nowhere at present. It's available for future multi-monitor stream coordination. Keeping the file.
- `_detect_gpu_capabilities()` in `video_loader.py` — method is defined but never called (GPU detection was stubbed out per the inline comment). Not a bug; the method is ready for future wiring. No action taken.
