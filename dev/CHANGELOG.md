# Changelog

All notable changes to VideoWall will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite (PRD.md, LEARNINGS.md, TODO.md)
- Project manifest and version mapping
- Build system scripts for cross-platform compilation
- Environment configuration support (.env)
- Test structure scaffolding
- Screenshot organization system

### Changed
- Reorganized project structure for better maintainability
- Updated CLAUDE.md with detailed architecture information
- Improved error handling in stream tracker
- Enhanced configuration system

### Fixed
- Memory management in long-running sessions
- Display detection on Linux systems
- M3U8 stream parsing edge cases

## [0.1.0] - 2025-01-22

### Added
- Initial production release
- Multi-monitor support with automatic detection
- M3U8 streaming capability
- Local video playback
- Hardware acceleration via Qt
- Modular architecture implementation
- Configuration system
- Basic error handling and logging
- macOS and Linux support

### Core Features
- **Display Management**: Automatic detection and configuration of multiple displays
- **Video Playback**: Support for common formats (MP4, AVI, MOV, MKV, WEBM)
- **Streaming**: M3U8 playlist parsing and playback
- **Layout System**: Grid-based and custom layouts
- **Fallback System**: Automatic fallback to local content on stream failure
- **Status Overlay**: Debug information and performance metrics

### Technical Implementation
- PyQt5-based user interface
- Qt Multimedia for video playback
- Modular architecture with clear separation of concerns
- Signal/slot pattern for event handling
- JSON-based configuration

## [0.0.9] - 2024-12-15 (Pre-release)

### Added
- Legacy implementations for reference
- VLC-based prototypes
- Multiple experimental approaches
- Basic multi-monitor support

### Experimental Features
- Floating tile layouts
- Dynamic tile management
- Roku integration attempts
- Hardware acceleration experiments

## [0.0.1] - 2024-07-01 (Initial Development)

### Added
- First working prototype
- Basic video playback
- Simple multi-window support
- VLC Python bindings integration

### Known Limitations
- Single file implementation
- No error handling
- Limited format support
- No configuration system

---

## Version History Summary

### Evolution Path
1. **VLC Era (0.0.1 - 0.0.5)**: Experimentation with VLC bindings
2. **PyQt Migration (0.0.6 - 0.0.8)**: Transition to PyQt5
3. **Architecture Refactor (0.0.9)**: Modular design implementation
4. **Production Ready (0.1.0)**: First stable release

### Breaking Changes
- v0.1.0: Complete architecture change from legacy scripts
- v0.0.6: Migration from VLC to PyQt5

### Deprecations
- VLC-based implementations (moved to legacy/)
- Single-file scripts (moved to legacy/)
- Hardcoded configurations (replaced with config system)

## Migration Guide

### From Legacy Scripts to v0.1.0
1. Install new dependencies: `pip install -r requirements.txt`
2. Update configuration files to JSON format
3. Use new modular import structure
4. Replace VLC calls with Qt Multimedia equivalents

### From v0.0.x to v0.1.0
- Configuration files need migration to new format
- Import paths have changed to modular structure
- VLC dependencies can be removed
- New Qt5 plugins may need installation

## Contributors

- Jason Paul Michaels - Initial work and architecture
- Community contributors - Testing and feedback

## Acknowledgments

- Qt/PyQt5 team for the multimedia framework
- VLC team for inspiration and early prototypes
- Open source community for feedback and suggestions

## Future Releases

See [TODO.md](./TODO.md) for planned features and roadmap.

### Planned for v0.2.0
- Comprehensive test suite
- Windows support
- Performance optimizations
- Web control interface

### Planned for v0.3.0
- Plugin system
- Advanced effects
- REST API
- Cloud integration

### Planned for v1.0.0
- Enterprise features
- Professional installer
- Commercial support
- Complete documentation