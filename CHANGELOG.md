# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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