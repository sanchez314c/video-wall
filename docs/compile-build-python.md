# Python Application Build System

Complete build system for Python applications with multi-platform support, following the same professional methodology as the Electron version.

## Required /dist Folder Structure:

After running `compile-build-dist.sh`, the `/dist` folder will contain:

```
dist/
├── linux/                   # Linux executable
│   └── [AppName]           # Linux binary
├── macos-intel/            # macOS Intel build
│   ├── [AppName]           # Unix executable
│   └── [AppName].app/      # macOS app bundle
├── macos-arm64/            # macOS ARM64 build
│   ├── [AppName]           # Unix executable
│   └── [AppName].app/      # macOS app bundle
├── windows/                # Windows build
│   └── [AppName].exe       # Windows executable
├── installers/             # Platform installers
│   ├── [AppName]-[version]-intel.dmg     # macOS Intel installer
│   ├── [AppName]-[version]-arm64.dmg     # macOS ARM64 installer
│   ├── [AppName]-[version]-setup.exe     # Windows installer (NSIS)
│   └── [AppName]-[version].AppImage      # Linux AppImage
└── build-info.json         # Build metadata
```

## Script 1: compile-build-dist.sh
Main build script for Python applications:

```bash
#!/bin/bash

# Python Application Compile-Build-Dist Script
# One-command solution for complete multi-platform build process

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="YourAppName"  # Change this to your app name
APP_VERSION="1.0.0"      # Change this to your version
MAIN_SCRIPT="main.py"    # Change this to your entry point
ICON_PATH="assets/icon"  # Path to icon files (without extension)

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display help
show_help() {
    echo "Python Application Complete Build Script"
    echo ""
    echo "Usage: ./compile-build-dist.sh [options]"
    echo ""
    echo "Options:"
    echo "  --no-clean         Skip cleaning build artifacts"
    echo "  --platform PLAT    Build only for specific platform (macos-intel|macos-arm64|windows|linux|all)"
    echo "  --no-venv          Skip virtual environment creation"
    echo "  --debug            Build with debug mode enabled"
    echo "  --help             Display this help message"
    echo ""
    echo "Examples:"
    echo "  ./compile-build-dist.sh                           # Full build for all platforms"
    echo "  ./compile-build-dist.sh --platform macos-intel    # Build only for macOS Intel"
    echo "  ./compile-build-dist.sh --no-clean                # Build without cleaning first"
}

# Parse command line arguments
NO_CLEAN=false
NO_VENV=false
DEBUG_MODE=false
BUILD_PLATFORM="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-clean)
            NO_CLEAN=true
            shift
            ;;
        --no-venv)
            NO_VENV=true
            shift
            ;;
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        --platform)
            BUILD_PLATFORM="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check for required tools
print_status "Checking requirements..."

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python version: $PYTHON_VERSION"

# Check for pip
if ! command_exists pip3; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

print_success "Base requirements met"

# Step 1: Clean everything if not skipped
if [ "$NO_CLEAN" = false ]; then
    print_status "🧹 Purging all existing builds..."
    rm -rf dist/
    rm -rf build/
    rm -rf __pycache__/
    rm -rf *.spec
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    print_success "All build artifacts purged"
fi

# Step 2: Setup virtual environment if not skipped
if [ "$NO_VENV" = false ]; then
    print_status "🐍 Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
else
    print_info "Skipping virtual environment setup"
fi

# Step 3: Install/update dependencies
print_status "📦 Installing/updating dependencies..."

# Install PyInstaller and other build tools
pip3 install --upgrade pip
pip3 install --upgrade pyinstaller
pip3 install --upgrade wheel setuptools

# Install project dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install project dependencies"
        exit 1
    fi
    print_success "Project dependencies installed"
else
    print_warning "No requirements.txt found, skipping project dependencies"
fi

# Additional build tools for creating installers
if [ "$(uname)" = "Darwin" ]; then
    # macOS specific tools
    if ! command_exists create-dmg; then
        print_info "Installing create-dmg for macOS installer creation..."
        if command_exists brew; then
            brew install create-dmg
        else
            print_warning "Homebrew not found. DMG creation will be skipped."
        fi
    fi
elif [ "$(uname)" = "Linux" ]; then
    # Linux specific tools
    if ! command_exists appimagetool; then
        print_info "Downloading appimagetool for AppImage creation..."
        wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
        chmod +x appimagetool-x86_64.AppImage
        sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
    fi
fi

print_success "All dependencies ready"

# Step 4: Create PyInstaller spec file
print_status "📝 Creating PyInstaller spec file..."

# Determine PyInstaller options
PYINSTALLER_OPTS="--name $APP_NAME"
PYINSTALLER_OPTS="$PYINSTALLER_OPTS --onefile"

if [ "$DEBUG_MODE" = false ]; then
    PYINSTALLER_OPTS="$PYINSTALLER_OPTS --windowed"
    PYINSTALLER_OPTS="$PYINSTALLER_OPTS --noconsole"
else
    PYINSTALLER_OPTS="$PYINSTALLER_OPTS --console"
    PYINSTALLER_OPTS="$PYINSTALLER_OPTS --debug all"
fi

# Add icon if it exists
if [ -f "${ICON_PATH}.icns" ] || [ -f "${ICON_PATH}.ico" ] || [ -f "${ICON_PATH}.png" ]; then
    if [ "$(uname)" = "Darwin" ] && [ -f "${ICON_PATH}.icns" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --icon=${ICON_PATH}.icns"
    elif [ "$(uname)" = "Windows" ] && [ -f "${ICON_PATH}.ico" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --icon=${ICON_PATH}.ico"
    elif [ -f "${ICON_PATH}.png" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --icon=${ICON_PATH}.png"
    fi
fi

# Step 5: Build for specified platforms
print_status "🏗️  Building for platform(s): $BUILD_PLATFORM"

# Create dist directories
mkdir -p dist/installers

# Function to build for macOS
build_macos() {
    local arch=$1
    print_status "Building for macOS ($arch)..."
    
    local dist_dir="dist/macos-$arch"
    mkdir -p "$dist_dir"
    
    # Build with PyInstaller
    if [ "$arch" = "intel" ]; then
        pyinstaller $PYINSTALLER_OPTS --distpath "$dist_dir" --target-arch x86_64 "$MAIN_SCRIPT"
    else
        pyinstaller $PYINSTALLER_OPTS --distpath "$dist_dir" --target-arch arm64 "$MAIN_SCRIPT"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "macOS $arch build completed"
        
        # Create .app bundle
        if [ -f "$dist_dir/$APP_NAME" ]; then
            print_status "Creating macOS app bundle..."
            
            # Create app bundle structure
            APP_BUNDLE="$dist_dir/$APP_NAME.app"
            mkdir -p "$APP_BUNDLE/Contents/MacOS"
            mkdir -p "$APP_BUNDLE/Contents/Resources"
            
            # Move executable
            mv "$dist_dir/$APP_NAME" "$APP_BUNDLE/Contents/MacOS/$APP_NAME"
            
            # Create Info.plist
            cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourcompany.$APP_NAME</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$APP_VERSION</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
            
            # Copy icon if exists
            if [ -f "${ICON_PATH}.icns" ]; then
                cp "${ICON_PATH}.icns" "$APP_BUNDLE/Contents/Resources/icon.icns"
            fi
            
            print_success "App bundle created: $APP_BUNDLE"
            
            # Create DMG installer if create-dmg is available
            if command_exists create-dmg; then
                print_status "Creating DMG installer..."
                create-dmg \
                    --volname "$APP_NAME" \
                    --window-pos 200 120 \
                    --window-size 800 400 \
                    --icon-size 100 \
                    --app-drop-link 600 185 \
                    "dist/installers/${APP_NAME}-${APP_VERSION}-${arch}.dmg" \
                    "$APP_BUNDLE"
                    
                if [ $? -eq 0 ]; then
                    print_success "DMG created: dist/installers/${APP_NAME}-${APP_VERSION}-${arch}.dmg"
                else
                    print_warning "DMG creation failed"
                fi
            fi
        fi
    else
        print_error "macOS $arch build failed"
        return 1
    fi
}

# Function to build for Windows
build_windows() {
    print_status "Building for Windows..."
    
    local dist_dir="dist/windows"
    mkdir -p "$dist_dir"
    
    # Build with PyInstaller
    pyinstaller $PYINSTALLER_OPTS --distpath "$dist_dir" "$MAIN_SCRIPT"
    
    if [ $? -eq 0 ]; then
        print_success "Windows build completed"
        
        # Create NSIS installer if makensis is available
        if command_exists makensis; then
            print_status "Creating Windows installer..."
            
            # Create NSIS script
            cat > installer.nsi << EOF
!define PRODUCT_NAME "$APP_NAME"
!define PRODUCT_VERSION "$APP_VERSION"
!define PRODUCT_PUBLISHER "Your Company"

Name "\${PRODUCT_NAME} \${PRODUCT_VERSION}"
OutFile "dist/installers/\${PRODUCT_NAME}-\${PRODUCT_VERSION}-setup.exe"
InstallDir "\$PROGRAMFILES\\\${PRODUCT_NAME}"
RequestExecutionLevel admin

Section "MainSection" SEC01
    SetOutPath "\$INSTDIR"
    File "dist/windows/\${PRODUCT_NAME}.exe"
    CreateShortcut "\$DESKTOP\\\${PRODUCT_NAME}.lnk" "\$INSTDIR\\\${PRODUCT_NAME}.exe"
    CreateShortcut "\$SMPROGRAMS\\\${PRODUCT_NAME}\\\${PRODUCT_NAME}.lnk" "\$INSTDIR\\\${PRODUCT_NAME}.exe"
SectionEnd

Section "Uninstall"
    Delete "\$INSTDIR\\\${PRODUCT_NAME}.exe"
    Delete "\$DESKTOP\\\${PRODUCT_NAME}.lnk"
    Delete "\$SMPROGRAMS\\\${PRODUCT_NAME}\\\${PRODUCT_NAME}.lnk"
    RMDir "\$INSTDIR"
SectionEnd
EOF
            
            makensis installer.nsi
            rm installer.nsi
            
            if [ $? -eq 0 ]; then
                print_success "Windows installer created"
            else
                print_warning "Windows installer creation failed"
            fi
        else
            print_info "NSIS not found, skipping Windows installer creation"
        fi
    else
        print_error "Windows build failed"
        return 1
    fi
}

# Function to build for Linux
build_linux() {
    print_status "Building for Linux..."
    
    local dist_dir="dist/linux"
    mkdir -p "$dist_dir"
    
    # Build with PyInstaller
    pyinstaller $PYINSTALLER_OPTS --distpath "$dist_dir" "$MAIN_SCRIPT"
    
    if [ $? -eq 0 ]; then
        print_success "Linux build completed"
        
        # Create AppImage if appimagetool is available
        if command_exists appimagetool; then
            print_status "Creating AppImage..."
            
            # Create AppDir structure
            APPDIR="$dist_dir/$APP_NAME.AppDir"
            mkdir -p "$APPDIR/usr/bin"
            mkdir -p "$APPDIR/usr/share/applications"
            mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
            
            # Copy executable
            cp "$dist_dir/$APP_NAME" "$APPDIR/usr/bin/"
            
            # Create desktop file
            cat > "$APPDIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=$APP_NAME
Exec=$APP_NAME
Icon=$APP_NAME
Type=Application
Categories=Utility;
EOF
            
            # Copy icon if exists
            if [ -f "${ICON_PATH}.png" ]; then
                cp "${ICON_PATH}.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"
            fi
            
            # Create AppRun script
            cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/usr/bin/$APP_NAME" "$@"
EOF
            chmod +x "$APPDIR/AppRun"
            
            # Build AppImage
            appimagetool "$APPDIR" "dist/installers/${APP_NAME}-${APP_VERSION}.AppImage"
            
            if [ $? -eq 0 ]; then
                print_success "AppImage created: dist/installers/${APP_NAME}-${APP_VERSION}.AppImage"
            else
                print_warning "AppImage creation failed"
            fi
            
            # Clean up AppDir
            rm -rf "$APPDIR"
        else
            print_info "appimagetool not found, skipping AppImage creation"
        fi
    else
        print_error "Linux build failed"
        return 1
    fi
}

# Build based on platform selection
case $BUILD_PLATFORM in
    macos-intel)
        build_macos "intel"
        ;;
    macos-arm64)
        build_macos "arm64"
        ;;
    windows)
        build_windows
        ;;
    linux)
        build_linux
        ;;
    all)
        # Detect current platform and build accordingly
        if [ "$(uname)" = "Darwin" ]; then
            build_macos "intel"
            build_macos "arm64"
            print_info "Cross-compilation for Windows/Linux requires Wine or Docker"
        elif [ "$(uname)" = "Linux" ]; then
            build_linux
            print_info "Cross-compilation for macOS/Windows requires additional setup"
        else
            build_windows
            print_info "Cross-compilation for macOS/Linux requires additional setup"
        fi
        ;;
    *)
        print_error "Invalid platform: $BUILD_PLATFORM"
        exit 1
        ;;
esac

# Step 6: Create build info
print_status "📋 Creating build information..."

cat > dist/build-info.json << EOF
{
    "app_name": "$APP_NAME",
    "version": "$APP_VERSION",
    "build_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "python_version": "$PYTHON_VERSION",
    "platform": "$BUILD_PLATFORM",
    "debug_mode": $DEBUG_MODE
}
EOF

# Step 7: Display build results
print_status "📊 Build Results:"
echo ""

if [ -d "dist" ]; then
    print_status "📁 Generated builds:"
    echo ""
    
    # Check macOS builds
    if [ -d "dist/macos-intel" ] || [ -d "dist/macos-arm64" ]; then
        print_success "macOS builds:"
        [ -d "dist/macos-intel" ] && echo "   ${GREEN}✓${NC} Intel: dist/macos-intel/"
        [ -d "dist/macos-arm64" ] && echo "   ${GREEN}✓${NC} ARM64: dist/macos-arm64/"
    fi
    
    # Check Windows build
    if [ -d "dist/windows" ]; then
        print_success "Windows build:"
        echo "   ${GREEN}✓${NC} dist/windows/${APP_NAME}.exe"
    fi
    
    # Check Linux build
    if [ -d "dist/linux" ]; then
        print_success "Linux build:"
        echo "   ${GREEN}✓${NC} dist/linux/${APP_NAME}"
    fi
    
    # Check installers
    if [ -d "dist/installers" ] && [ "$(ls -A dist/installers 2>/dev/null)" ]; then
        echo ""
        print_status "📦 Generated installers:"
        for installer in dist/installers/*; do
            if [ -f "$installer" ]; then
                size=$(du -h "$installer" | cut -f1)
                echo "   ${GREEN}✓${NC} $(basename "$installer") ($size)"
            fi
        done
    fi
    
    # Show directory tree
    echo ""
    print_status "📂 Directory structure:"
    if command_exists tree; then
        tree -L 3 dist/
    else
        find dist -type f -o -type d | head -20
    fi
else
    print_error "No dist directory found. Build may have failed."
fi

# Clean up spec files unless in debug mode
if [ "$DEBUG_MODE" = false ]; then
    rm -f *.spec
fi

echo ""
print_success "🎉 Build process completed!"
print_status "📁 All builds are in: ./dist/"
print_info "To run the app:"
print_info "  From source: ./run-python-source.sh"
print_info "  From binary: ./run-python.sh"
```

## Script 2: run-python-source.sh
Run Python application from source:

```bash
#!/bin/bash

# Run Python Application from Source (Development Mode)
# Launches the app directly from source code

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MAIN_SCRIPT="main.py"    # Change this to your entry point
USE_VENV=true            # Set to false to use system Python

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

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

print_status "🚀 Starting Python application from source..."

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

# Setup virtual environment if requested
if [ "$USE_VENV" = true ]; then
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
        # Check if dependencies are installed
        if ! pip3 show -q $(head -1 requirements.txt | cut -d'=' -f1) 2>/dev/null; then
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
else
    print_info "Using system Python installation"
fi

# Display Python version
PYTHON_VERSION=$(python3 --version 2>&1)
print_info "Python version: $PYTHON_VERSION"

# Launch the application
print_status "Launching application from source code..."
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

# Deactivate virtual environment if it was activated
if [ "$USE_VENV" = true ] && [ -n "$VIRTUAL_ENV" ]; then
    deactivate
    print_info "Virtual environment deactivated"
fi
```

## Script 3: run-python.sh
Run compiled Python binary:

```bash
#!/bin/bash

# Run Python Application from Compiled Binary
# Launches the compiled application from dist folder

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="YourAppName"  # Change this to match your app name

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

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

print_status "🚀 Launching compiled Python application..."

# Check if dist directory exists
if [ ! -d "dist" ]; then
    print_error "No dist/ directory found. Please run ./compile-build-dist.sh first."
    exit 1
fi

# Detect current platform
PLATFORM=""
BINARY_PATH=""

if [ "$(uname)" = "Darwin" ]; then
    # macOS
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        PLATFORM="macos-arm64"
    else
        PLATFORM="macos-intel"
    fi
    
    # Look for app bundle first
    if [ -d "dist/$PLATFORM/$APP_NAME.app" ]; then
        BINARY_PATH="dist/$PLATFORM/$APP_NAME.app"
        print_info "Found macOS app bundle"
    elif [ -f "dist/$PLATFORM/$APP_NAME" ]; then
        BINARY_PATH="dist/$PLATFORM/$APP_NAME"
        print_info "Found macOS executable"
    fi
    
elif [ "$(uname)" = "Linux" ]; then
    # Linux
    PLATFORM="linux"
    if [ -f "dist/$PLATFORM/$APP_NAME" ]; then
        BINARY_PATH="dist/$PLATFORM/$APP_NAME"
        print_info "Found Linux executable"
    fi
    
elif [[ "$(uname -s)" =~ MINGW|CYGWIN|MSYS ]]; then
    # Windows (Git Bash, Cygwin, MSYS)
    PLATFORM="windows"
    if [ -f "dist/$PLATFORM/$APP_NAME.exe" ]; then
        BINARY_PATH="dist/$PLATFORM/$APP_NAME.exe"
        print_info "Found Windows executable"
    fi
else
    print_error "Unsupported platform: $(uname)"
    exit 1
fi

# If platform-specific binary not found, look for any binary
if [ -z "$BINARY_PATH" ]; then
    print_warning "Platform-specific binary not found for $PLATFORM"
    print_status "Searching for any available binary..."
    
    # Search for any executable
    for dir in dist/*/; do
        if [ -d "$dir" ]; then
            # Check for app bundle
            if [ -d "$dir$APP_NAME.app" ]; then
                BINARY_PATH="$dir$APP_NAME.app"
                print_success "Found app bundle: $BINARY_PATH"
                break
            # Check for Unix executable
            elif [ -f "$dir$APP_NAME" ] && [ -x "$dir$APP_NAME" ]; then
                BINARY_PATH="$dir$APP_NAME"
                print_success "Found executable: $BINARY_PATH"
                break
            # Check for Windows executable
            elif [ -f "$dir$APP_NAME.exe" ]; then
                BINARY_PATH="$dir$APP_NAME.exe"
                print_success "Found Windows executable: $BINARY_PATH"
                break
            fi
        fi
    done
fi

# Launch the application if found
if [ -n "$BINARY_PATH" ]; then
    print_success "Launching $APP_NAME..."
    
    # Launch based on type
    if [[ "$BINARY_PATH" == *.app ]]; then
        # macOS app bundle
        open "$BINARY_PATH"
        print_success "Application launched successfully!"
        print_info "The app is now running. Check your dock to interact with it."
        
    elif [[ "$BINARY_PATH" == *.exe ]]; then
        # Windows executable
        if [[ "$(uname -s)" =~ MINGW|CYGWIN|MSYS ]]; then
            # Running on Windows
            "$BINARY_PATH" &
            print_success "Application launched successfully!"
        else
            print_warning "This is a Windows executable. You may need Wine to run it on $(uname)."
            print_info "Attempting to launch with Wine..."
            if command -v wine >/dev/null 2>&1; then
                wine "$BINARY_PATH" &
                print_info "Application launched with Wine"
            else
                print_error "Wine is not installed. Cannot run Windows executable on $(uname)."
                exit 1
            fi
        fi
        
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
    print_warning "Available files in dist/:"
    
    if [ -d "dist" ]; then
        find dist -type f -name "$APP_NAME*" -o -type d -name "*.app" 2>/dev/null | head -10
    fi
    
    echo ""
    print_info "To build the app first, run:"
    print_info "  ./compile-build-dist.sh"
    print_info ""
    print_info "To run from source instead:"
    print_info "  ./run-python-source.sh"
    
    exit 1
fi
```

## Additional Files Needed:

### requirements.txt
Create this file with your Python dependencies:
```
# Core dependencies
pyinstaller>=5.0
wheel
setuptools

# Your app dependencies
# Add your specific packages here
# numpy>=1.21.0
# pandas>=1.3.0
# requests>=2.26.0
```

### Project Structure:
```
your-python-app/
├── main.py                    # Your main entry point
├── requirements.txt           # Python dependencies
├── compile-build-dist.sh      # Main build script
├── run-python-source.sh       # Run from source
├── run-python.sh             # Run compiled binary
├── assets/                   # Optional assets
│   ├── icon.icns            # macOS icon
│   ├── icon.ico             # Windows icon
│   └── icon.png             # Linux icon
└── src/                      # Your source code
    └── ...
```

## Setup Instructions:

1. **Save the three scripts** in your Python project root
2. **Make them executable**:
   ```bash
   chmod +x compile-build-dist.sh
   chmod +x run-python-source.sh
   chmod +x run-python.sh
   ```
3. **Update configuration** in each script:
   - Change `APP_NAME` to your application name
   - Change `APP_VERSION` to your version
   - Change `MAIN_SCRIPT` to your entry point (e.g., `main.py`, `app.py`)
   - Update icon paths if you have icons

4. **Install system dependencies** (optional but recommended):
   ```bash
   # macOS
   brew install create-dmg
   
   # Linux
   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
   chmod +x appimagetool-x86_64.AppImage
   sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
   
   # Windows (for creating installers)
   # Install NSIS from https://nsis.sourceforge.io/
   ```

5. **Build your application**:
   ```bash
   ./compile-build-dist.sh              # Full build for all platforms
   ./compile-build-dist.sh --help        # See all options
   ```

6. **Run your application**:
   ```bash
   ./run-python-source.sh    # Development mode
   ./run-python.sh          # Production binary
   ```

## Key Features:
- ✅ Multi-platform support (macOS Intel+ARM, Windows, Linux)
- ✅ Virtual environment management
- ✅ Automatic dependency installation
- ✅ Platform-specific installers (DMG, EXE, AppImage)
- ✅ Color-coded output with timestamps
- ✅ Comprehensive error handling
- ✅ Debug mode support
- ✅ Clean build options
- ✅ macOS app bundle creation
- ✅ Build metadata tracking

The system follows the same professional methodology as the Electron version but is specifically adapted for Python applications using PyInstaller.