#!/bin/bash

# Run VideoWall from Compiled Binary - Linux
# Launches the compiled application from dist folder

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="VideoWall"

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

print_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] ℹ${NC} $1"
}

print_status "🚀 Launching compiled VideoWall application..."

# Check if dist directory exists
if [ ! -d "dist" ]; then
    print_error "No dist/ directory found. Please run ./scripts/compile-build-dist.sh first."
    exit 1
fi

# Look for Linux binary
BINARY_PATH=""
if [ -f "dist/linux/$APP_NAME" ]; then
    BINARY_PATH="dist/linux/$APP_NAME"
    print_success "Found Linux executable"
fi

# Check for AppImage as alternative
if [ -z "$BINARY_PATH" ] && [ -f "dist/installers/$APP_NAME-1.0.0.AppImage" ]; then
    BINARY_PATH="dist/installers/$APP_NAME-1.0.0.AppImage"
    print_success "Found AppImage"
fi

# Launch the application if found
if [ -n "$BINARY_PATH" ]; then
    print_success "Launching $APP_NAME..."
    
    # Make sure it's executable
    if [ ! -x "$BINARY_PATH" ]; then
        print_status "Making binary executable..."
        chmod +x "$BINARY_PATH"
    fi
    
    # Run the binary
    "$BINARY_PATH"
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "Application terminated successfully"
    else
        print_error "Application terminated with error code: $EXIT_CODE"
    fi
else
    print_error "Could not find $APP_NAME binary in dist/ directory"
    print_info "To build the app first, run:"
    print_info "  ./scripts/compile-build-dist.sh"
    print_info ""
    print_info "To run from source instead:"
    print_info "  ./scripts/run-linux-source.sh"
    
    exit 1
fi