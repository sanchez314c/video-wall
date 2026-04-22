#!/bin/bash
set -euo pipefail

# Run video-wall from Source on Linux
# Dark Neo Glass themed PyQt5 application

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')]${NC} $1"
}

# Check if we're on Linux
if [ "$(uname)" != "Linux" ]; then
    print_error "This script is for Linux only"
    exit 1
fi

print_status "Starting VideoWall from source (Linux)..."

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python is not installed. Install with: sudo apt install python3"
    exit 1
fi

print_status "Using Python: $("$PYTHON_CMD" --version)"

# Check for PyQt5
if ! "$PYTHON_CMD" -c "import PyQt5" 2>/dev/null; then
    print_error "PyQt5 is not installed. Install with: pip install PyQt5"
    print_status "Attempting to install dependencies..."
    "$PYTHON_CMD" -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Set Qt platform plugin path if needed
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"

# Optimize for multi-core
export QT_ASSUME_STDERR_HAS_CONSOLE=1

# Run the application
print_success "Launching VideoWall..."
"$PYTHON_CMD" -m src "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "VideoWall session ended"
else
    print_error "VideoWall exited with code $EXIT_CODE"
fi

exit $EXIT_CODE
