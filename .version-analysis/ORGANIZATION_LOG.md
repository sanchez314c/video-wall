# Video Wall - Organization Log

**Date:** 2026-01-10
**Operation:** Version Consolidation

---

## Summary

| Metric | Value |
|--------|-------|
| Distinct programs | 1 |
| Total versions | 3 |
| Duplicates archived | 3 |
| Naming format | video-wall_v0.0.X |

---

## Final Structure

```
video-wall/
├── video-wall_v0.0.1/     (2.4 MB - VLC architecture)
├── video-wall_v0.0.2/     (253 MB - older PyQt variant)
├── video-wall_v0.0.3/     (192 MB - latest PyQt5)
│
├── archive/
│   └── duplicates_20260110_214135/
│
└── .version-analysis/
    └── ORGANIZATION_LOG.md
```

---

## Version Details

| Version | Original Name | Size | Tech Stack | Description |
|---------|---------------|------|------------|-------------|
| v0.0.1 | VideoWall_02 | 2.4 MB | VLC/FFmpeg | Oldest - multi-package VLC architecture |
| v0.0.2 | VideoWall_00 | 253 MB | PyQt5 | Older PyQt variant with dist |
| v0.0.3 | (root) | 192 MB | PyQt5 v2.0.0 | Latest - hardware-accelerated PyQt5 |

---

## MD5 Fingerprint Analysis

### README.md Groups
| MD5 Hash | Locations |
|----------|-----------|
| 915913580c99... | ROOT, archive/video-wall (DUPLICATES) |
| af254f0079fe... | video-wall_00, *videowall/VideoWall_00 |
| f933b76883a6... | VideoWall_02, VideoWall2_03 (DUPLICATES) |

### Source Code Analysis
- ROOT = archive/video-wall = archive/video-wall_00 (identical core files)
- *videowall/VideoWall_00 has code differences (older variant)
- VideoWall_02 = VideoWall2_03 (identical)

---

## Archived Contents

Location: `archive/duplicates_20260110_214135/`

| Directory | Reason | Size |
|-----------|--------|------|
| video-wall_duplicate | Identical to root | 2.2 MB |
| video-wall_00_duplicate | Near-identical to root | 171 MB |
| VideoWall2_03_duplicate | Identical to VideoWall_02 | 2.5 MB |
| legacy_scripts-*.zip | Legacy scripts backup | 164 KB |

---

## Architecture Evolution

```
v0.0.1 (VideoWall_02)     → VLC/FFmpeg multi-package
         ↓
v0.0.2 (VideoWall_00)     → PyQt5 refactor
         ↓
v0.0.3 (current)          → PyQt5 v2.0.0 with hardware acceleration
```

---

## Rollback Instructions

```bash
BASE="/media/mpRAID/Development/Projects/video-wall"
ARCHIVE="$BASE/archive/duplicates_20260110_214135"

# Restore root from v0.0.3
mv "$BASE/video-wall_v0.0.3"/* "$BASE/"
rmdir "$BASE/video-wall_v0.0.3"

# Restore archived versions
mv "$BASE/video-wall_v0.0.1" "$BASE/archive/VideoWall_02"
mv "$BASE/video-wall_v0.0.2" "$BASE/archive/*videowall/VideoWall_00"
mkdir -p "$BASE/archive/*videowall"

# Restore duplicates
mv "$ARCHIVE/video-wall_duplicate" "$BASE/archive/video-wall"
mv "$ARCHIVE/video-wall_00_duplicate" "$BASE/archive/video-wall_00"
mv "$ARCHIVE/VideoWall2_03_duplicate" "$BASE/archive/VideoWall2_03"
```

---

**END OF LINE.**
