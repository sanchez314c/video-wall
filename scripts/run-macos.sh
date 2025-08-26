#!/bin/bash

# Run VideoWall from Compiled Binary - macOS
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

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    PLATFORM="macos-arm64"
    print_info "Detected Apple Silicon Mac"
else
    PLATFORM="macos-intel"
    print_info "Detected Intel Mac"
fi

# Look for app bundle
BINARY_PATH=""
if [ -d "dist/$PLATFORM/$APP_NAME.app" ]; then
    BINARY_PATH="dist/$PLATFORM/$APP_NAME.app"
    print_success "Found macOS app bundle"
elif [ -f "dist/$PLATFORM/$APP_NAME" ]; then
    BINARY_PATH="dist/$PLATFORM/$APP_NAME"
    print_success "Found macOS executable"
fi

# If platform-specific binary not found, try the other architecture
if [ -z "$BINARY_PATH" ]; then
    print_warning "No $PLATFORM binary found, checking other architecture..."
    
    if [ "$PLATFORM" = "macos-arm64" ]; then
        ALT_PLATFORM="macos-intel"
    else
        ALT_PLATFORM="macos-arm64"
    fi
    
    if [ -d "dist/$ALT_PLATFORM/$APP_NAME.app" ]; then
        BINARY_PATH="dist/$ALT_PLATFORM/$APP_NAME.app"
        print_warning "Found $ALT_PLATFORM app bundle (may run under Rosetta)"
    elif [ -f "dist/$ALT_PLATFORM/$APP_NAME" ]; then
        BINARY_PATH="dist/$ALT_PLATFORM/$APP_NAME"
        print_warning "Found $ALT_PLATFORM executable (may run under Rosetta)"
    fi
fi

# Launch the application if found
if [ -n "$BINARY_PATH" ]; then
    print_success "Launching $APP_NAME..."
    
    if [[ "$BINARY_PATH" == *.app ]]; then
        # macOS app bundle
        open "$BINARY_PATH"
        print_success "Application launched successfully!"
        print_info "The app is now running. Check your dock to interact with it."
    else
        # Unix executable
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
    fi
else
    print_error "Could not find $APP_NAME binary in dist/ directory"
    print_info "To build the app first, run:"
    print_info "  ./scripts/compile-build-dist.sh"
    print_info ""
    print_info "To run from source instead:"
    print_info "  ./scripts/run-macos-source.sh"
    
    exit 1
fi