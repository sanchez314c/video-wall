#!/bin/bash

# Run VideoWall from Source on macOS
# PyQt5 multi-display video wall application

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

# Check if we're on macOS
if [ "$(uname)" != "Darwin" ]; then
    print_error "This script is for macOS only"
    exit 1
fi

print_status "Starting VideoWall from source (macOS)..."

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
    print_error "Python is not installed. Install via: brew install python"
    exit 1
fi

print_status "Using Python: $($PYTHON_CMD --version)"

# Check for PyQt5
if ! $PYTHON_CMD -c "import PyQt5" 2>/dev/null; then
    print_error "PyQt5 is not installed. Attempting to install dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Run the application
print_success "Launching VideoWall..."
$PYTHON_CMD -m src "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "VideoWall session ended"
else
    print_error "VideoWall exited with code $EXIT_CODE"
fi

exit $EXIT_CODE
