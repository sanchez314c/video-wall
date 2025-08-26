#!/bin/bash

# Run VideoWall from Source - Linux
# Launches the app directly from source code

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MAIN_SCRIPT="src/main.py"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✓${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] ℹ${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_status "🚀 Starting VideoWall from source..."

# Check for Python
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    print_error "$MAIN_SCRIPT not found. Make sure you're in the project root directory."
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Install dependencies if needed
if [ -f "requirements.txt" ]; then
    # Check if dependencies are installed by trying to import a key package
    if ! python3 -c "import tkinter" 2>/dev/null; then
        print_status "Installing dependencies..."
        pip3 install -r requirements.txt
        if [ $? -ne 0 ]; then
            print_error "Failed to install dependencies"
            exit 1
        fi
        print_success "Dependencies installed"
    else
        print_info "Dependencies already installed"
    fi
fi

# Display Python version
PYTHON_VERSION=$(python3 --version 2>&1)
print_info "Python version: $PYTHON_VERSION"

# Launch the application
print_status "Launching VideoWall from source code..."
print_info "Press Ctrl+C to stop the application"
echo ""

# Run the Python application
python3 "$MAIN_SCRIPT"

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    print_success "Application terminated successfully"
else
    print_error "Application terminated with error code: $EXIT_CODE"
fi

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
    print_info "Virtual environment deactivated"
fi