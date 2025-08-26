# VideoWall Development Guide

## Table of Contents
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Debugging](#debugging)
- [Contributing](#contributing)
- [Release Process](#release-process)

## Development Environment Setup

### Prerequisites
- Python 3.8+
- Git
- IDE (recommended: VS Code, PyCharm, or Vim)
- Virtual environment tool (venv or conda)

### Quick Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/video-wall.git
   cd video-wall
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Install in Development Mode**
   ```bash
   pip install -e .
   ```

### IDE Configuration

#### VS Code
Install these extensions:
- Python
- Pylance
- Python Docstring Generator
- GitLens

Configure workspace settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

#### PyCharm
1. Open project directory
2. Configure Python interpreter to use venv
3. Enable code inspection with Pylint
4. Set up code style to follow project standards

## Project Structure

### Directory Layout
```
video-wall/
├── src/                    # Source code
│   ├── core/              # Core application logic
│   ├── ui/                # User interface components
│   ├── utils/             # Utility functions
│   └── config/            # Configuration modules
├── docs/                  # Documentation
├── tests/                 # Test suite (if implemented)
├── scripts/               # Build and utility scripts
├── config/                # Configuration files
├── build_resources/       # Build assets (icons, etc.)
└── dist/                  # Built distributions
```

### Core Components

#### VideoWall (`src/core/video_wall.py`)
Main application window and central coordinator
- Manages application lifecycle
- Coordinates between components
- Handles global events

#### VideoManager (`src/core/video_manager.py`)
Multi-video playback coordination
- Manages video player instances
- Handles playback synchronization
- Implements fallback strategies

#### DisplayManager (`src/core/display_manager.py`)
Multi-monitor detection and configuration
- Detects available displays
- Manages display arrangements
- Handles display change events

#### LayoutManager (`src/core/layout_manager.py`)
Dynamic grid layout and positioning
- Calculates video positions
- Manages layout transitions
- Implements layout algorithms

#### Animator (`src/core/animator.py`)
Smooth animation and transition effects
- Handles layout animations
- Manages transition timing
- Implements easing functions

## Code Standards

### Python Style Guide
Follow PEP 8 with these project-specific conventions:

#### Naming Conventions
```python
# Classes: PascalCase
class VideoManager:
    pass

# Functions and variables: snake_case
def load_video_file():
    video_path = "/path/to/video"
    return video_path

# Constants: UPPER_SNAKE_CASE
MAX_ACTIVE_PLAYERS = 15
DEFAULT_GRID_SIZE = 3

# Private members: prefix with underscore
class MyClass:
    def __init__(self):
        self._private_var = "private"
        self.__very_private = "very private"
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from typing import List, Optional

# Third-party imports
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, pyqtSignal

# Local imports
from src.core.video_manager import VideoManager
from src.utils.file_utils import load_videos
```

#### Docstrings
Use Google-style docstrings:
```python
def calculate_layout_positions(grid_size: Tuple[int, int], 
                           screen_size: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Calculate video tile positions for grid layout.
    
    Args:
        grid_size: Tuple of (rows, columns) for the grid
        screen_size: Tuple of (width, height) of the screen
        
    Returns:
        List of (x, y) tuples for each video position
        
    Raises:
        ValueError: If grid_size exceeds screen capacity
    """
    pass
```

### Error Handling

#### Exception Hierarchy
```python
class VideoWallError(Exception):
    """Base exception for VideoWall application."""
    pass

class VideoLoadError(VideoWallError):
    """Raised when video loading fails."""
    pass

class DisplayError(VideoWallError):
    """Raised when display configuration fails."""
    pass
```

#### Error Handling Pattern
```python
def load_video_file(file_path: str) -> Optional[Video]:
    """Load video file with error handling."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")
        
        video = Video(file_path)
        return video
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error loading video: {e}")
        raise VideoLoadError(f"Failed to load video: {e}")
```

### Logging

Use Python's logging module:
```python
import logging

logger = logging.getLogger(__name__)

class VideoManager:
    def __init__(self):
        logger.info("Initializing VideoManager")
        
    def play_video(self, video_path: str):
        logger.debug(f"Playing video: {video_path}")
        # ... implementation
        logger.info(f"Video started: {video_path}")
```

Configure logging in main.py:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_wall.log'),
        logging.StreamHandler()
    ]
)
```

## Testing

### Test Structure (When Implemented)
```
tests/
├── unit/                   # Unit tests
│   ├── test_video_manager.py
│   ├── test_layout_manager.py
│   └── test_animator.py
├── integration/            # Integration tests
│   ├── test_display_integration.py
│   └── test_streaming_integration.py
├── fixtures/              # Test data
│   ├── sample_videos/
│   └── test_streams.m3u8
└── conftest.py           # pytest configuration
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_video_manager.py

# Run with verbose output
pytest -v
```

### Writing Tests

#### Unit Test Example
```python
import pytest
from src.core.layout_manager import LayoutManager

class TestLayoutManager:
    def setup_method(self):
        self.layout_manager = LayoutManager()
    
    def test_calculate_grid_positions(self):
        """Test grid position calculation."""
        positions = self.layout_manager.calculate_grid_positions(
            grid_size=(2, 2),
            screen_size=(1920, 1080)
        )
        
        assert len(positions) == 4
        assert positions[0] == (0, 0)  # Top-left
        assert positions[3] == (960, 540)  # Bottom-right
    
    def test_invalid_grid_size(self):
        """Test error handling for invalid grid size."""
        with pytest.raises(ValueError):
            self.layout_manager.calculate_grid_positions(
                grid_size=(0, 0),
                screen_size=(1920, 1080)
            )
```

#### Integration Test Example
```python
import pytest
from PyQt5.QtWidgets import QApplication
from src.core.video_wall import VideoWall

class TestVideoWallIntegration:
    @pytest.fixture
    def app(self):
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        app.quit()
    
    def test_full_application_startup(self, app):
        """Test complete application startup."""
        video_wall = VideoWall()
        assert video_wall.isVisible()
        video_wall.close()
```

## Debugging

### Debug Mode
Run with debug flag:
```bash
python -m src --debug
```

### Debugging Tools

#### pdb (Python Debugger)
```python
import pdb; pdb.set_trace()  # Set breakpoint
```

#### VS Code Debugging
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug VideoWall",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "args": ["--debug"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

#### Qt Debugging
Enable Qt debugging:
```python
import os
os.environ['QT_DEBUG_PLUGINS'] = '1'
os.environ['QT_LOGGING_RULES'] = '*=true'
```

### Common Debugging Scenarios

#### Video Playback Issues
```python
# Check supported formats
from PyQt5.QtMultimedia import QMediaPlayer
print("Supported formats:", QMediaPlayer.supportedMimeTypes())

# Check player state
player = QMediaPlayer()
print("Player state:", player.state())
print("Error:", player.error())
```

#### Display Issues
```python
# Check detected displays
from PyQt5.QtWidgets import QApplication
app = QApplication([])
screens = app.screens()
for i, screen in enumerate(screens):
    print(f"Screen {i}: {screen.size()} @ {screen.logicalDotsPerInch()} DPI")
```

## Contributing

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests for new functionality
   - Update documentation

3. **Test Changes**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   pylint src/
   black src/
   
   # Test application
   python -m src
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Commit Message Format
Use conventional commits:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

Examples:
```
feat(video): add support for MKV format

fix(display): correct multi-monitor detection on Linux

docs(api): update video manager documentation
```

### Code Review Process

1. **Self-Review**
   - Code follows standards
   - Tests pass
   - Documentation updated

2. **Peer Review**
   - Request review from team member
   - Address feedback
   - Update as needed

3. **Merge**
   - Ensure CI passes
   - Squash commits if needed
   - Merge to main branch

## Release Process

### Version Management
Use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Update version in:
- `src/config/settings.py`
- `VideoWall.spec` (build spec)
- `CHANGELOG.md`

### Pre-Release Checklist

1. **Code Quality**
   - [ ] All tests pass
   - [ ] Code coverage > 80%
   - [ ] Linting passes
   - [ ] Documentation updated

2. **Build Testing**
   - [ ] macOS build succeeds
   - [ ] Linux build succeeds
   - [ ] Docker build works
   - [ ] Installation tested

3. **Feature Testing**
   - [ ] Core features work
   - [ ] Edge cases handled
   - [ ] Performance acceptable
   - [ ] Security review done

### Release Steps

1. **Update Version**
   ```bash
   # Update version numbers
   # Update CHANGELOG.md
   git commit -m "chore: bump version to X.Y.Z"
   ```

2. **Create Tag**
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

3. **Build Releases**
   ```bash
   # macOS
   pyinstaller VideoWall.spec --clean --noconfirm
   
   # Linux
   bash build-linux.sh
   ```

4. **Create GitHub Release**
   - Upload build artifacts
   - Copy release notes from CHANGELOG
   - Link to documentation

5. **Update Documentation**
   - Update website if applicable
   - Announce release
   - Update download links

### Post-Release

1. **Monitor Issues**
   - Watch for bug reports
   - Address critical issues quickly

2. **Plan Next Release**
   - Review feedback
   - Prioritize features
   - Update roadmap

## Additional Resources

### Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [API.md](API.md) - API reference
- [BUILD_COMPILE.md](BUILD_COMPILE.md) - Build system

### Tools and Utilities
- Black: Code formatting
- Pylint: Code linting
- pytest: Testing framework
- PyInstaller: Application packaging

### Community
- GitHub Issues: Bug reports and features
- GitHub Discussions: Questions and ideas
- Wiki: Community documentation

---

For questions about development, see [CONTRIBUTING.md](CONTRIBUTING.md) or open an issue on GitHub.