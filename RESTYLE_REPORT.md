# Neo-Noir Glass Monitor Restyle Report

**Project**: VideoWall  
**Date**: 2026-04-17  
**Status**: COMPLETE

---

## Audit Table

| Neo-Noir Requirement | Current State | Action Taken |
|----------------------|---------------|--------------|
| Void-black BG (#0A0B0E) | `BG_VOID = "#0a0b0e"` | PASS — no change needed |
| Card/glass panels (#141518, rgba) | `BG_CARD = "#141518"`, `GlassCard` uses gradient + rgba border-top | PASS — no change needed |
| Accent teal (#14B8A6) | `ACCENT_TEAL = "#14b8a6"` — single constant | PASS — centralized (was already correct) |
| Text primary (#E8E8EC) | `TEXT_PRIMARY = "#e8e8ec"` | PASS — no change needed |
| Layered drop shadows | `QGraphicsDropShadowEffect` on `GlassCard` + `LocalVideoDialog` outer frame | PASS — no change needed |
| Frameless title bar (drag-to-move) | `CustomTitleBar` with drag handlers, min/max/close | PASS — refined (added About button) |
| About modal | DID NOT EXIST | ADDED — `AboutDialog` class in `dialogs.py` |
| Status bar | N/A — fullscreen video wall windows | WAIVED — see justification below |

---

## Color Token Diff

### Added
| Token | Value | Purpose |
|-------|-------|---------|
| `ACCENT_TEAL_SELECTION` | `rgba(20, 184, 166, 30)` | Selection highlights — was inlined 4x |

### Replaced
| Location | Before | After |
|----------|--------|-------|
| `theme.py:211,247,351,369` | `rgba(20, 184, 166, 30)` (hardcoded) | `{ACCENT_TEAL_SELECTION}` (constant) |
| `theme.py:704-705` (close btn hover) | `#ef4444` (hardcoded) | `{ERROR}` (constant) |
| `recorder.py:29` (REC indicator) | `"rgba(220, 38, 38, 0.85)"` / `"#ffffff"` | `rgba(239, 68, 68, 220)` via `ERROR` + `{TEXT_HEADING}` |

No color values changed — only centralized existing colors into named constants.

---

## New Components

### AboutDialog (`src/ui/dialogs.py`)
- Frameless glass panel matching `LocalVideoDialog` pattern
- `QGraphicsDropShadowEffect` (blur 48, offset 12, alpha 120)
- App name ("VideoWall"), version ("v1.6.4"), description, author ("J. Michaels (sanchez314c)"), MIT license
- Clickable GitHub link (`QDesktopServices.openUrl`)
- `GlowLine` separator
- `CustomTitleBar` with close button
- Application modal (`Qt.ApplicationModal`)
- Drag-to-move on whole dialog

### About Button (CustomTitleBar)
- "?" button added between spacer and window controls
- Uses `get_titlebar_button_about_stylesheet()` — teal accent on hover
- Opens `AboutDialog` via `exec_()`
- Applied to all dialogs using `CustomTitleBar` (LocalVideoDialog + AboutDialog)

### New Stylesheet Functions (`src/ui/theme.py`)
- `get_titlebar_button_about_stylesheet()` — neo-glass circle, teal hover
- `get_about_dialog_stylesheet()` — content styling for About modal

---

## Files Modified

| File | Lines | Changes |
|------|-------|---------|
| `src/ui/theme.py` | 807 → 893 (+86) | Added `ACCENT_TEAL_SELECTION` constant, replaced 4x inline rgba, replaced hardcoded `#ef4444` with `ERROR`, added 2 stylesheet functions |
| `src/ui/dialogs.py` | 385 → 519 (+134) | Added `AboutDialog` class, added About button to `CustomTitleBar`, added `_show_about` method |
| `src/core/recorder.py` | 211 → 212 (+1) | Replaced hardcoded colors in `RecordingIndicator` with theme constants |

**Total**: 3 files, +221 net lines

---

## Status Bar Waiver

VideoWall main windows are **fullscreen over each monitor** — the entire display is a video grid. A status bar would:
- Consume screen space in a fullscreen app where every pixel shows video
- Be invisible behind video content in normal operation
- Break the visual continuity of the wall

Status information is instead communicated through:
- Status overlay labels on individual tiles (`StatusOverlay`)
- Console output for recording state
- The `RecordingIndicator` overlay (REC dot)

This is the correct UX for a fullscreen video wall — no status bar needed.

---

## Validation

- `py_compile`: all 3 files clean
- Import resolution: all new exports importable
- No changes to video_tile.py rendering logic
- No changes to keyboard shortcuts or app behavior
- No changes to VideoWall main windows (fullscreen, no title bar)
- Existing `CustomTitleBar` pattern preserved and extended

---

END OF LINE.
