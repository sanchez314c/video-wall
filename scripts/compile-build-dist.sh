#!/bin/bash

# VideoWall Complete Build System
# Builds for ALL platforms: macOS Intel, macOS ARM64, Windows, Linux
# Creates installers: DMG, EXE, AppImage

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="VideoWall"
APP_VERSION="1.0.0"
MAIN_SCRIPT="src/main.py"

# Get the script directory and move to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✔${NC} $1"
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

print_success "All requirements met"

# Step 1: PURGE all existing builds
print_status "🧹 Purging all existing builds..."
rm -rf dist/
rm -rf build/
rm -rf __pycache__/
rm -rf *.spec
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
print_success "All build artifacts purged"

# Step 2: Setup virtual environment
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

# Step 3: Install/update dependencies
print_status "📦 Installing/updating dependencies..."

# Install PyInstaller and other build tools
pip3 install --upgrade pip
pip3 install --upgrade pyinstaller
pip3 install --upgrade py2app  # For macOS builds
pip3 install --upgrade wheel setuptools

# Install project dependencies
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

print_success "Dependencies ready"

# Step 4: Create dist directories structure
print_status "📁 Creating dist folder structure..."
mkdir -p dist/macos-intel
mkdir -p dist/macos-arm64
mkdir -p dist/windows
mkdir -p dist/linux
mkdir -p dist/installers

# Step 5: Prepare PyInstaller options
print_status "🎯 Preparing build configurations..."

# Base PyInstaller options
PYINSTALLER_BASE="--name $APP_NAME --clean --noconfirm"
PYINSTALLER_BASE="$PYINSTALLER_BASE --add-data src:src"

# Add resources if exists
if [ -d "resources" ]; then
    PYINSTALLER_BASE="$PYINSTALLER_BASE --add-data resources:resources"
fi

# Platform-specific options
PYINSTALLER_MAC="$PYINSTALLER_BASE --windowed --onedir"
PYINSTALLER_WIN="$PYINSTALLER_BASE --windowed --onefile"
PYINSTALLER_LINUX="$PYINSTALLER_BASE --onefile"

# Add icon if exists
if [ -f "resources/icon.icns" ]; then
    PYINSTALLER_MAC="$PYINSTALLER_MAC --icon=resources/icon.icns"
    print_info "Found macOS icon: resources/icon.icns"
fi

if [ -f "resources/icon.ico" ]; then
    PYINSTALLER_WIN="$PYINSTALLER_WIN --icon=resources/icon.ico"
    print_info "Found Windows icon: resources/icon.ico"
fi

if [ -f "resources/icon.png" ]; then
    PYINSTALLER_LINUX="$PYINSTALLER_LINUX --icon=resources/icon.png"
    print_info "Found Linux icon: resources/icon.png"
fi

# Step 6: Build for macOS Intel
print_status "🏗️  Building for macOS Intel (x64)..."
print_status "Targets: macOS (Intel + ARM), Windows (x64), Linux (x64)"
print_status "Installers: .dmg, .exe, .AppImage"

# Create spec file for macOS Intel
cat > VideoWall-intel.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['$MAIN_SCRIPT'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('resources', 'resources')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='$APP_NAME',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.icns',
)

app = BUNDLE(
    exe,
    name='$APP_NAME.app',
    icon='resources/icon.icns',
    bundle_identifier='com.videowall.app',
    info_plist={
        'CFBundleShortVersionString': '$APP_VERSION',
        'NSHighResolutionCapable': 'True',
    },
)
EOF

pyinstaller VideoWall-intel.spec --distpath dist/macos-intel

if [ $? -eq 0 ]; then
    print_success "macOS Intel build completed"
else
    print_error "macOS Intel build failed"
fi

# Step 7: Build for macOS ARM64
print_status "🏗️  Building for macOS ARM64..."

# Create spec file for macOS ARM64
cat > VideoWall-arm64.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['$MAIN_SCRIPT'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('resources', 'resources')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='$APP_NAME',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.icns',
)

app = BUNDLE(
    exe,
    name='$APP_NAME.app',
    icon='resources/icon.icns',
    bundle_identifier='com.videowall.app',
    info_plist={
        'CFBundleShortVersionString': '$APP_VERSION',
        'NSHighResolutionCapable': 'True',
    },
)
EOF

pyinstaller VideoWall-arm64.spec --distpath dist/macos-arm64

if [ $? -eq 0 ]; then
    print_success "macOS ARM64 build completed"
else
    print_error "macOS ARM64 build failed"
fi

# Step 8: Build for Windows
print_status "🏗️  Building for Windows (x64)..."

pyinstaller $PYINSTALLER_WIN --distpath dist/windows "$MAIN_SCRIPT"

if [ $? -eq 0 ]; then
    # Rename to .exe if not already
    if [ -f "dist/windows/$APP_NAME" ]; then
        mv "dist/windows/$APP_NAME" "dist/windows/$APP_NAME.exe"
    fi
    print_success "Windows build completed"
else
    print_warning "Windows build failed (cross-compilation may require Wine)"
fi

# Step 9: Build for Linux
print_status "🏗️  Building for Linux (x64)..."

pyinstaller $PYINSTALLER_LINUX --distpath dist/linux "$MAIN_SCRIPT"

if [ $? -eq 0 ]; then
    print_success "Linux build completed"
else
    print_warning "Linux build failed"
fi

# Step 10: Create macOS DMG installers
print_status "📦 Creating macOS DMG installers..."

# Install create-dmg if not available
if ! command_exists create-dmg; then
    print_info "Installing create-dmg..."
    if command_exists brew; then
        brew install create-dmg
    else
        print_warning "Homebrew not found. Trying npm..."
        npm install -g create-dmg
    fi
fi

# Create Intel DMG
if [ -d "dist/macos-intel/$APP_NAME.app" ]; then
    print_status "Creating Intel DMG..."
    create-dmg \
        --volname "$APP_NAME" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 200 190 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 600 185 \
        "dist/installers/${APP_NAME}-${APP_VERSION}-intel.dmg" \
        "dist/macos-intel/$APP_NAME.app" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Intel DMG created: dist/installers/${APP_NAME}-${APP_VERSION}-intel.dmg"
    else
        print_warning "Intel DMG creation failed"
    fi
fi

# Create ARM64 DMG
if [ -d "dist/macos-arm64/$APP_NAME.app" ]; then
    print_status "Creating ARM64 DMG..."
    create-dmg \
        --volname "$APP_NAME" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 200 190 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 600 185 \
        "dist/installers/${APP_NAME}-${APP_VERSION}-arm64.dmg" \
        "dist/macos-arm64/$APP_NAME.app" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "ARM64 DMG created: dist/installers/${APP_NAME}-${APP_VERSION}-arm64.dmg"
    else
        print_warning "ARM64 DMG creation failed"
    fi
fi

# Step 11: Create Linux AppImage
print_status "📦 Creating Linux AppImage..."

if [ -f "dist/linux/$APP_NAME" ]; then
    # Download appimagetool if not present
    if [ ! -f "/tmp/appimagetool-x86_64.AppImage" ]; then
        print_info "Downloading appimagetool..."
        wget -q -O /tmp/appimagetool-x86_64.AppImage \
            https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
        chmod +x /tmp/appimagetool-x86_64.AppImage
    fi
    
    # Create AppDir structure
    APPDIR="dist/linux/$APP_NAME.AppDir"
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
    
    # Copy executable
    cp "dist/linux/$APP_NAME" "$APPDIR/usr/bin/"
    
    # Create desktop file
    cat > "$APPDIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=$APP_NAME
Exec=$APP_NAME
Icon=$APP_NAME
Type=Application
Categories=AudioVideo;Video;
EOF
    
    # Copy icon if exists
    if [ -f "resources/icon.png" ]; then
        cp "resources/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"
    fi
    
    # Create AppRun script
    cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/usr/bin/VideoWall" "$@"
APPRUN
    chmod +x "$APPDIR/AppRun"
    
    # Build AppImage
    /tmp/appimagetool-x86_64.AppImage "$APPDIR" "dist/installers/${APP_NAME}-${APP_VERSION}.AppImage" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "AppImage created: dist/installers/${APP_NAME}-${APP_VERSION}.AppImage"
    else
        print_warning "AppImage creation failed"
    fi
    
    # Clean up AppDir
    rm -rf "$APPDIR"
fi

# Step 12: Create Windows installer (if NSIS available)
print_status "📦 Creating Windows installer..."

if [ -f "dist/windows/$APP_NAME.exe" ]; then
    if command_exists makensis; then
        # Create NSIS script
        cat > installer.nsi << EOF
!define PRODUCT_NAME "$APP_NAME"
!define PRODUCT_VERSION "$APP_VERSION"
!define PRODUCT_PUBLISHER "VideoWall Team"

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
            print_success "Windows installer created: dist/installers/${APP_NAME}-${APP_VERSION}-setup.exe"
        else
            print_warning "Windows installer creation failed"
        fi
    else
        print_info "NSIS not found, skipping Windows installer"
    fi
fi

# Step 13: Create build info
print_status "📋 Creating build information..."

cat > dist/build-info.json << EOF
{
    "app_name": "$APP_NAME",
    "version": "$APP_VERSION",
    "build_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "python_version": "$PYTHON_VERSION",
    "platform": "all",
    "builds": {
        "macos-intel": $([ -d "dist/macos-intel/$APP_NAME.app" ] && echo "true" || echo "false"),
        "macos-arm64": $([ -d "dist/macos-arm64/$APP_NAME.app" ] && echo "true" || echo "false"),
        "windows": $([ -f "dist/windows/$APP_NAME.exe" ] && echo "true" || echo "false"),
        "linux": $([ -f "dist/linux/$APP_NAME" ] && echo "true" || echo "false")
    },
    "installers": {
        "dmg-intel": $([ -f "dist/installers/${APP_NAME}-${APP_VERSION}-intel.dmg" ] && echo "true" || echo "false"),
        "dmg-arm64": $([ -f "dist/installers/${APP_NAME}-${APP_VERSION}-arm64.dmg" ] && echo "true" || echo "false"),
        "appimage": $([ -f "dist/installers/${APP_NAME}-${APP_VERSION}.AppImage" ] && echo "true" || echo "false"),
        "windows-setup": $([ -f "dist/installers/${APP_NAME}-${APP_VERSION}-setup.exe" ] && echo "true" || echo "false")
    }
}
EOF

# Clean up spec files
rm -f *.spec

# Step 14: Display build results
echo ""
print_status "═══════════════════════════════════════════════════════════════"
print_status "📊 Build Results:"
print_status "═══════════════════════════════════════════════════════════════"
echo ""

if [ -d "dist" ]; then
    print_status "📁 Generated builds:"
    echo ""
    
    # Check macOS builds
    if [ -d "dist/macos-intel/$APP_NAME.app" ] || [ -d "dist/macos-arm64/$APP_NAME.app" ]; then
        print_success "macOS builds:"
        [ -d "dist/macos-intel/$APP_NAME.app" ] && echo "   ${GREEN}✔${NC} Intel: dist/macos-intel/$APP_NAME.app"
        [ -d "dist/macos-arm64/$APP_NAME.app" ] && echo "   ${GREEN}✔${NC} ARM64: dist/macos-arm64/$APP_NAME.app"
    fi
    
    # Check Windows build
    if [ -f "dist/windows/$APP_NAME.exe" ]; then
        print_success "Windows build:"
        size=$(du -h "dist/windows/$APP_NAME.exe" | cut -f1)
        echo "   ${GREEN}✔${NC} dist/windows/$APP_NAME.exe ($size)"
    fi
    
    # Check Linux build
    if [ -f "dist/linux/$APP_NAME" ]; then
        print_success "Linux build:"
        size=$(du -h "dist/linux/$APP_NAME" | cut -f1)
        echo "   ${GREEN}✔${NC} dist/linux/$APP_NAME ($size)"
    fi
    
    # Check installers
    echo ""
    print_status "📦 Generated installers:"
    
    for installer in dist/installers/*; do
        if [ -f "$installer" ]; then
            size=$(du -h "$installer" | cut -f1)
            name=$(basename "$installer")
            echo "   ${GREEN}✔${NC} $name ($size)"
        fi
    done
    
    # Show directory tree
    echo ""
    print_status "📂 Directory structure:"
    if command_exists tree; then
        tree -L 2 dist/
    else
        ls -la dist/
        ls -la dist/installers/
    fi
else
    print_error "No dist directory found. Build may have failed."
fi

echo ""
print_success "🎉 Build process completed!"
print_status "📁 All builds are in: ./dist/"
print_info "To run the app:"
print_info "  From source: ./scripts/run-macos-source.sh"
print_info "  From binary: ./scripts/run-macos.sh"