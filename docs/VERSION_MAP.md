# Version Map - VideoWall

## Overview
VideoWall has evolved through multiple iterations, from simple VLC-based implementations to sophisticated PyQt5 multi-monitor solutions with hardware acceleration.

## Current Architecture

### Main Version (src/)
**Purpose**: Production-ready PyQt5-based video wall application
**Status**: Active development
**Key Features**:
- Multi-monitor support with automatic detection
- M3U8 streaming and local video playback
- Hardware acceleration via Qt multimedia
- Modular architecture with clear separation of concerns
- Professional error handling and fallback mechanisms

**Run**: 
```bash
python -m src
# or after installation:
videowall
```

## Legacy Implementations (legacy/)

### PyQt5 Implementations
Various PyQt5-based approaches exploring different features:

1. **pyqt5-m3u8-grid-professional.py** - Professional grid layout with M3U8 support
2. **pyqt5-video-wall-with-effects-and-controls.py** - Advanced effects and control system
3. **pyqt5-m3u8-multimonitor-fallback.py** - Multi-monitor with fallback logic
4. **pyqt5-local-grid-effects-controls.py** - Local video with effects
5. **pyqt5-local-windowed-multimonitor.py** - Windowed mode for multi-monitor

### VLC-Based Implementations
Earlier explorations using python-vlc:

1. **vlc-dynamic-video-wall-with-hardware-acceleration.py** - Hardware acceleration focus
2. **vlc-floating-tiles-video-wall.py** - Floating tile layout
3. **vlc-local-dynamic-tiles.py** - Dynamic tile management
4. **vlc-hybrid-roku-plex.py** - Integration with Roku/Plex
5. **vlc-local-floating-animated.py** - Animated floating tiles

### Standalone Implementations
Self-contained scripts for specific use cases:

1. **standalone-dynamic-video-wall-m3u8-streams.py** - Dynamic M3U8 streaming
2. **standalone-multi-monitor-m3u8-with-fallback.py** - Multi-monitor with fallback
3. **standalone-roku-integration-video-wall.py** - Roku device integration
4. **standalone-pyqt5-video-wall-with-effects.py** - Effects-focused implementation

### Multi-Monitor Specializations
Focused on multi-display setups:

1. **multi-monitor-local-video-wall-windowed-mode.py** - Windowed mode across monitors
2. **multi-monitor-m3u8-video-wall-with-local-fallback.py** - Streaming with local fallback

## Evolution Timeline

### Phase 1: VLC Exploration (Early)
- Started with VLC bindings for basic video playback
- Explored floating and dynamic tile concepts
- Learned about hardware acceleration needs

### Phase 2: PyQt5 Migration (Middle)
- Moved to PyQt5 for better Qt integration
- Implemented grid layouts and effects
- Added M3U8 streaming support

### Phase 3: Architecture Refinement (Current)
- Modular architecture in src/
- Proper separation of concerns
- Professional error handling
- Comprehensive configuration system

## Lessons Learned Across Versions

### VLC Phase Taught:
- Hardware acceleration is crucial for performance
- VLC bindings have limitations for complex layouts
- Need for better event handling and UI integration

### PyQt5 Experiments Taught:
- Qt's multimedia framework provides better integration
- Grid layouts work well for video walls
- Effects need careful performance consideration
- M3U8 parsing requires robust error handling

### Current Architecture Benefits:
- Modular design allows easy feature additions
- Separation of UI and logic improves maintainability
- Configuration system enables flexibility
- Proper error handling ensures stability

## How to Navigate Versions

1. **For Production Use**: Use the main version in `src/`
2. **For Learning**: Explore `legacy/` implementations to understand evolution
3. **For Specific Features**: Check legacy files for specialized implementations (e.g., Roku integration)

## Technology Stack Evolution

### Dependencies Evolution:
- **Early**: python-vlc, basic Python
- **Middle**: PyQt5, more structured approach
- **Current**: PyQt5, requests, professional tooling (pytest, black, flake8)

### Architecture Evolution:
- **Early**: Single-file scripts
- **Middle**: Some modularization
- **Current**: Full MVC-like architecture with proper packaging

## Key Technical Decisions

1. **PyQt5 over VLC**: Better integration, more control
2. **Modular Architecture**: Easier to maintain and extend
3. **M3U8 Support**: Critical for streaming use cases
4. **Hardware Acceleration**: Essential for multi-display performance
5. **Configuration System**: Flexibility for different setups