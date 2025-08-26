#!/bin/bash

# UNIVERSAL MULTI-PLATFORM BUILD SYSTEM
# Auto-detects project type and builds for all platforms
# Supports: Electron, Python, Swift, TypeScript, Web, PWA
# Includes comprehensive optimization and cleanup

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_DIR"

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

print_header() {
    echo ""
    echo -e "${PURPLE}════════════════════════════════════════════${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}════════════════════════════════════════════${NC}"
    echo ""
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect project type
detect_project_type() {
    PROJECT_TYPE="unknown"

    # Check for Electron
    if [ -f "package.json" ] && grep -q '"electron"' package.json; then
        PROJECT_TYPE="electron"

    # Check for Python
    elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ] || ls *.py >/dev/null 2>&1; then
        PROJECT_TYPE="python"

    # Check for Swift/macOS
    elif [ -f "Package.swift" ] || ls *.xcodeproj >/dev/null 2>&1 || ls *.swift >/dev/null 2>&1; then
        if [ "$(uname)" = "Darwin" ]; then
            PROJECT_TYPE="swift"
        else
            echo "error: Swift projects can only be built on macOS" >&2
            exit 1
        fi

    # Check for TypeScript
    elif [ -f "tsconfig.json" ]; then
        PROJECT_TYPE="typescript"

    # Check for Node.js/JavaScript project
    elif [ -f "package.json" ]; then
        # Check if it's a web framework
        if grep -q '"next"' package.json || grep -q '"nuxt"' package.json || grep -q '"gatsby"' package.json; then
            PROJECT_TYPE="webapp"
        elif grep -q '"react"' package.json || grep -q '"vue"' package.json || grep -q '"angular"' package.json || grep -q '"svelte"' package.json; then
            PROJECT_TYPE="spa"
        else
            PROJECT_TYPE="nodejs"
        fi

    # Check for static web project
    elif [ -f "index.html" ] || [ -f "src/index.html" ]; then
        PROJECT_TYPE="web"

    # Check for Dockerfile
    elif [ -f "Dockerfile" ]; then
        PROJECT_TYPE="docker"
    fi

    if [ "$PROJECT_TYPE" = "unknown" ]; then
        echo "error: Could not detect project type" >&2
        echo "Supported project types:" >&2
        echo "  • Electron (package.json with electron dependency)" >&2
        echo "  • Python (requirements.txt, setup.py, or .py files)" >&2
        echo "  • Swift (Package.swift or .xcodeproj on macOS)" >&2
        echo "  • TypeScript (tsconfig.json)" >&2
        echo "  • Node.js (package.json)" >&2
        echo "  • Web (index.html)" >&2
        exit 1
    fi

    echo "$PROJECT_TYPE"
}

# Function to cleanup system temp directories
cleanup_system_temp() {
    print_status "🧹 Cleaning system temp directories..."
    
    # macOS temp cleanup
    if [ "$(uname)" = "Darwin" ]; then
        TEMP_DIR=$(find /private/var/folders -name "Temporary*" -type d 2>/dev/null | head -1)
        if [ -n "$TEMP_DIR" ]; then
            PARENT_DIR=$(dirname "$TEMP_DIR")
            BEFORE_SIZE=$(du -sh "$PARENT_DIR" 2>/dev/null | cut -f1)
            
            # Clean up build artifacts (older than 1 day)
            find "$PARENT_DIR" -name "t-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
            find "$PARENT_DIR" -name "electron-download-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
            find "$PARENT_DIR" -name "pyinstaller-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
            find "$PARENT_DIR" -name "npm-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
            
            AFTER_SIZE=$(du -sh "$PARENT_DIR" 2>/dev/null | cut -f1)
            print_success "System temp cleanup: $BEFORE_SIZE → $AFTER_SIZE"
        fi
    fi
    
    # Linux temp cleanup
    if [ "$(uname)" = "Linux" ]; then
        if [ -d "/tmp" ]; then
            BEFORE_SIZE=$(du -sh /tmp 2>/dev/null | cut -f1)
            find /tmp -name "electron-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
            find /tmp -name "npm-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
            find /tmp -name "pyinstaller-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
            AFTER_SIZE=$(du -sh /tmp 2>/dev/null | cut -f1)
            print_success "System temp cleanup: $BEFORE_SIZE → $AFTER_SIZE"
        fi
    fi
    
    # Project-specific cleanup
    rm -rf node_modules/.cache 2>/dev/null || true
    rm -rf .build 2>/dev/null || true
    rm -rf build-temp 2>/dev/null || true
    rm -rf __pycache__ 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".DS_Store" -delete 2>/dev/null || true
}

# Function to setup build temp directory
setup_build_temp() {
    BUILD_TEMP_DIR="$SCRIPT_DIR/build-temp"
    mkdir -p "$BUILD_TEMP_DIR"
    export TMPDIR="$BUILD_TEMP_DIR"
    export TMP="$BUILD_TEMP_DIR"
    export TEMP="$BUILD_TEMP_DIR"
    export ELECTRON_CACHE="$BUILD_TEMP_DIR/electron-cache"
    export PYINSTALLER_WORKDIR="$BUILD_TEMP_DIR/pyinstaller"
    print_info "Using custom temp directory: $BUILD_TEMP_DIR"
}

# Function to cleanup build temp
cleanup_build_temp() {
    if [ -n "$BUILD_TEMP_DIR" ] && [ -d "$BUILD_TEMP_DIR" ]; then
        print_status "🧹 Cleaning build temp directory..."
        TEMP_SIZE=$(du -sh "$BUILD_TEMP_DIR" 2>/dev/null | cut -f1 || echo "0")
        rm -rf "$BUILD_TEMP_DIR" 2>/dev/null || true
        print_success "Cleaned build temp: $TEMP_SIZE"
    fi
}

# Build function for Electron projects
build_electron() {
    print_header "🔌 BUILDING ELECTRON APPLICATION"
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Install dependencies
    print_status "📦 Installing dependencies..."
    if [ -f "yarn.lock" ]; then
        yarn install
    elif [ -f "pnpm-lock.yaml" ]; then
        pnpm install
    else
        npm install
    fi
    
    # Install electron-builder if not present
    if ! npm list electron-builder >/dev/null 2>&1; then
        print_status "Installing electron-builder..."
        npm install --save-dev electron-builder
    fi
    
    # Clean previous builds
    rm -rf dist/ build/ out/
    
    # Set parallelism for faster builds
    export ELECTRON_BUILDER_PARALLELISM=18
    
    # Build for all platforms
    print_status "🏗️ Building for all platforms..."
    if [ -f "yarn.lock" ]; then
        yarn dist
    elif [ -f "pnpm-lock.yaml" ]; then
        pnpm dist
    else
        npm run dist
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Electron build completed successfully"
        
        # List outputs
        if [ -d "dist" ]; then
            print_info "📦 Build outputs:"
            find dist -name "*.dmg" -o -name "*.exe" -o -name "*.AppImage" -o -name "*.deb" -o -name "*.rpm" | while read -r file; do
                SIZE=$(ls -lah "$file" | awk '{print $5}')
                print_info "  ✔ $(basename "$file") ($SIZE)"
            done
        fi
    else
        print_error "Electron build failed"
        exit 1
    fi
}

# Build function for Python projects
build_python() {
    print_header "🐍 BUILDING PYTHON APPLICATION"
    
    # Check Python
    PYTHON_CMD=""
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    print_info "Python command: $PYTHON_CMD"
    
    # Setup virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    if [ "$(uname)" = "Darwin" ] || [ "$(uname)" = "Linux" ]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi
    
    # Install dependencies
    print_status "📦 Installing dependencies..."
    pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Install PyInstaller
    pip install PyInstaller
    
    # Find main file
    MAIN_FILE=""
    for candidate in src/main.py main.py app.py src/app.py src/__main__.py; do
        if [ -f "$candidate" ]; then
            MAIN_FILE="$candidate"
            break
        fi
    done
    
    if [ -z "$MAIN_FILE" ]; then
        print_error "Cannot find main Python file"
        exit 1
    fi
    
    print_info "Main file: $MAIN_FILE"
    
    # Clean previous builds
    rm -rf dist/ build/
    
    # Configure PyInstaller options
    PYINSTALLER_OPTS="--onedir --windowed"
    
    # Add icon if available
    if [ "$(uname)" = "Darwin" ] && [ -f "resources/icon.icns" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --icon=resources/icon.icns"
    elif [ -f "resources/icon.ico" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --icon=resources/icon.ico"
    elif [ -f "icon.icns" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --icon=icon.icns"
    elif [ -f "icon.ico" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --icon=icon.ico"
    fi
    
    # Add assets if exist
    if [ -d "src" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --add-data src:src"
    fi

    # Add data files
    if [ -f "m3u8-hosts.m3u8" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --add-data m3u8-hosts.m3u8:."
    fi

    if [ -d "resources" ]; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --add-data resources:resources"
    fi
    
    # Handle specific frameworks
    if grep -q "customtkinter" requirements.txt 2>/dev/null; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --collect-all customtkinter --collect-all tkinter"
    fi
    
    # Handle PyQt5
    if grep -q "PyQt5" requirements.txt 2>/dev/null; then
        PYINSTALLER_OPTS="$PYINSTALLER_OPTS --collect-all PyQt5"
    fi
    
    # Build the application
    print_status "🏗️ Building Python application..."
    pyinstaller $PYINSTALLER_OPTS "$MAIN_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Python build completed successfully"
        
        # Platform-specific post-processing
        if [ "$(uname)" = "Darwin" ]; then
            APP_NAME=$(basename "$MAIN_FILE" .py)
            if [ -d "dist/$APP_NAME.app" ]; then
                print_success "Created macOS app: dist/$APP_NAME.app"
            fi
        fi
        
        # List outputs
        if [ -d "dist" ]; then
            print_info "📦 Build outputs in dist/"
        fi
    else
        print_error "Python build failed"
        exit 1
    fi
}

# Build function for Swift projects
build_swift() {
    print_header "🎯 BUILDING SWIFT/MACOS APPLICATION"
    
    # Check macOS
    if [ "$(uname)" != "Darwin" ]; then
        print_error "Swift projects can only be built on macOS"
        exit 1
    fi
    
    # Check Swift
    if ! command_exists swift; then
        print_error "Swift is not installed. Install Xcode Command Line Tools:"
        print_info "  xcode-select --install"
        exit 1
    fi
    
    # Determine build method
    BUILD_METHOD=""
    if [ -f "Package.swift" ]; then
        BUILD_METHOD="spm"
        print_info "Build method: Swift Package Manager"
    elif ls *.xcodeproj >/dev/null 2>&1; then
        BUILD_METHOD="xcodebuild"
        PROJECT_FILE=$(ls *.xcodeproj | head -1)
        print_info "Build method: xcodebuild with $PROJECT_FILE"
    else
        print_error "No Package.swift or .xcodeproj found"
        exit 1
    fi
    
    # Clean previous builds
    rm -rf .build/ build/ dist/
    
    # Create output directories
    mkdir -p build dist
    
    # Build based on method
    if [ "$BUILD_METHOD" = "spm" ]; then
        print_status "Building with Swift Package Manager..."
        swift build -c release
        
        if [ $? -eq 0 ]; then
            # Copy executable to dist
            EXECUTABLE=$(find .build/release -type f -perm +111 | head -1)
            if [ -f "$EXECUTABLE" ]; then
                cp "$EXECUTABLE" "dist/"
                print_success "Swift build completed: dist/$(basename "$EXECUTABLE")"
            fi
        else
            print_error "Swift build failed"
            exit 1
        fi
        
    elif [ "$BUILD_METHOD" = "xcodebuild" ]; then
        print_status "Building with xcodebuild..."
        
        # Get scheme
        SCHEME=$(xcodebuild -list -project "$PROJECT_FILE" | grep -A 1 "Schemes:" | tail -1 | xargs)
        
        xcodebuild -project "$PROJECT_FILE" \
                   -scheme "$SCHEME" \
                   -configuration Release \
                   -derivedDataPath build/DerivedData \
                   CONFIGURATION_BUILD_DIR=build/Release
        
        if [ $? -eq 0 ]; then
            # Find and copy app
            APP_PATH=$(find build -name "*.app" -type d | head -1)
            if [ -d "$APP_PATH" ]; then
                cp -r "$APP_PATH" dist/
                print_success "Swift build completed: dist/$(basename "$APP_PATH")"
                
                # Create ZIP for distribution
                APP_NAME=$(basename "$APP_PATH" .app)
                (cd dist && zip -r "$APP_NAME.zip" "$APP_NAME.app")
                print_success "Created ZIP: dist/$APP_NAME.zip"
            fi
        else
            print_error "xcodebuild failed"
            exit 1
        fi
    fi
}

# Build function for TypeScript projects
build_typescript() {
    print_header "📘 BUILDING TYPESCRIPT PROJECT"
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Detect package manager
    PKG_MANAGER="npm"
    if [ -f "yarn.lock" ]; then
        PKG_MANAGER="yarn"
    elif [ -f "pnpm-lock.yaml" ]; then
        PKG_MANAGER="pnpm"
    fi
    
    print_info "Package manager: $PKG_MANAGER"
    
    # Install dependencies
    print_status "📦 Installing dependencies..."
    case $PKG_MANAGER in
        npm) npm ci || npm install ;;
        yarn) yarn install --frozen-lockfile || yarn install ;;
        pnpm) pnpm install --frozen-lockfile || pnpm install ;;
    esac
    
    # Clean previous builds
    rm -rf dist/ build/ out/
    
    # Build the project
    print_status "🏗️ Building TypeScript project..."
    
    # Check for build script in package.json
    if grep -q '"build"' package.json; then
        $PKG_MANAGER run build
    else
        # Fallback to tsc
        npx tsc
    fi
    
    if [ $? -eq 0 ]; then
        print_success "TypeScript build completed successfully"
        
        # Determine output directory
        OUTPUT_DIR="dist"
        [ -d "build" ] && OUTPUT_DIR="build"
        [ -d "out" ] && OUTPUT_DIR="out"
        
        if [ -d "$OUTPUT_DIR" ]; then
            print_info "📦 Build outputs in $OUTPUT_DIR/"
            
            # Bundle size analysis
            TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" 2>/dev/null | cut -f1)
            print_info "Total build size: $TOTAL_SIZE"
        fi
    else
        print_error "TypeScript build failed"
        exit 1
    fi
}

# Build function for web projects
build_web() {
    print_header "🌐 BUILDING WEB APPLICATION"
    
    # Check if we have HTML files
    if [ ! -d "src" ] && [ ! -f "index.html" ] && [ ! -f "src/index.html" ]; then
        print_error "No HTML source files found"
        exit 1
    fi
    
    # Create dist directory
    mkdir -p dist
    
    # Check if it's a Node.js project
    if [ -f "package.json" ]; then
        # Detect package manager
        PKG_MANAGER="npm"
        if [ -f "yarn.lock" ]; then
            PKG_MANAGER="yarn"
        elif [ -f "pnpm-lock.yaml" ]; then
            PKG_MANAGER="pnpm"
        fi
        
        print_info "Package manager: $PKG_MANAGER"
        
        # Install dependencies
        print_status "📦 Installing dependencies..."
        case $PKG_MANAGER in
            npm) npm ci || npm install ;;
            yarn) yarn install --frozen-lockfile || yarn install ;;
            pnpm) pnpm install --frozen-lockfile || pnpm install ;;
        esac
        
        # Build the project
        if grep -q '"build"' package.json; then
            print_status "🏗️ Building with package.json build script..."
            $PKG_MANAGER run build
        else
            print_status "📁 Copying files to dist..."
            cp -r src/* dist/ 2>/dev/null || cp *.html dist/ 2>/dev/null || true
            cp -r public/* dist/ 2>/dev/null || true
        fi
    else
        # Simple copy for static sites
        print_status "📁 Copying static files to dist..."
        if [ -d "src" ]; then
            cp -r src/* dist/
        else
            cp *.html dist/ 2>/dev/null || true
            cp *.css dist/ 2>/dev/null || true
            cp *.js dist/ 2>/dev/null || true
        fi
        
        if [ -d "assets" ]; then
            cp -r assets dist/
        fi
    fi
    
    # Minification (if tools available)
    if command_exists html-minifier-terser; then
        print_status "🗜️ Minifying HTML..."
        find dist -name "*.html" -exec html-minifier-terser \
            --collapse-whitespace \
            --remove-comments \
            --input {} --output {} \; 2>/dev/null || true
    fi
    
    if command_exists cleancss; then
        print_status "🗜️ Minifying CSS..."
        find dist -name "*.css" -exec cleancss -o {} {} \; 2>/dev/null || true
    fi
    
    if command_exists terser; then
        print_status "🗜️ Minifying JavaScript..."
        find dist -name "*.js" ! -name "*.min.js" \
            -exec sh -c 'terser "$1" -o "$1" -c -m' _ {} \; 2>/dev/null || true
    fi
    
    print_success "Web build completed successfully"
    
    # Display results
    if [ -d "dist" ]; then
        TOTAL_SIZE=$(du -sh dist/ 2>/dev/null | cut -f1)
        print_info "📦 Build output size: $TOTAL_SIZE"
        print_info "📁 Files in dist/"
    fi
}

# Build function for Node.js projects
build_nodejs() {
    print_header "📦 BUILDING NODE.JS APPLICATION"
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Detect package manager
    PKG_MANAGER="npm"
    if [ -f "yarn.lock" ]; then
        PKG_MANAGER="yarn"
    elif [ -f "pnpm-lock.yaml" ]; then
        PKG_MANAGER="pnpm"
    fi
    
    print_info "Package manager: $PKG_MANAGER"
    
    # Install dependencies
    print_status "📦 Installing dependencies..."
    case $PKG_MANAGER in
        npm) npm ci || npm install ;;
        yarn) yarn install --frozen-lockfile || yarn install ;;
        pnpm) pnpm install --frozen-lockfile || pnpm install ;;
    esac
    
    # Clean previous builds
    rm -rf dist/ build/
    
    # Build the project
    print_status "🏗️ Building Node.js application..."
    
    if grep -q '"build"' package.json; then
        $PKG_MANAGER run build
    else
        # No build step needed for pure Node.js
        print_info "No build step defined, project ready to run"
        mkdir -p dist
        cp -r * dist/ 2>/dev/null || true
        rm -rf dist/node_modules dist/dist
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Node.js build completed successfully"
        
        # Check for pkg to create executables
        if command_exists pkg || npm list pkg >/dev/null 2>&1; then
            print_status "Creating standalone executables with pkg..."
            npx pkg . --targets node18-linux-x64,node18-macos-x64,node18-win-x64 --out-path dist/bin
            
            if [ $? -eq 0 ]; then
                print_success "Created standalone executables in dist/bin/"
            fi
        fi
    else
        print_error "Node.js build failed"
        exit 1
    fi
}

# Function to display help
show_help() {
    echo "Universal Multi-Platform Build System"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --type TYPE        Force specific project type"
    echo "                     (electron, python, swift, typescript, web, nodejs)"
    echo "  --no-clean         Skip cleaning build artifacts"
    echo "  --no-temp-clean    Skip system temp cleanup"
    echo "  --platform PLAT    Target platform (mac, win, linux, all)"
    echo "  --optimize         Enable aggressive optimization"
    echo "  --docker           Build Docker image"
    echo "  --help             Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Auto-detect and build"
    echo "  $0 --type python             # Force Python build"
    echo "  $0 --optimize --docker       # Optimized build with Docker"
    echo ""
    echo "The script automatically detects:"
    echo "  • Electron apps (package.json with electron)"
    echo "  • Python apps (requirements.txt or .py files)"
    echo "  • Swift apps (Package.swift or .xcodeproj)"
    echo "  • TypeScript projects (tsconfig.json)"
    echo "  • Node.js apps (package.json)"
    echo "  • Web apps (index.html)"
}

# Parse command line arguments
FORCE_TYPE=""
NO_CLEAN=false
NO_TEMP_CLEAN=false
PLATFORM="all"
OPTIMIZE=false
DOCKER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            FORCE_TYPE="$2"
            shift 2
            ;;
        --no-clean)
            NO_CLEAN=true
            shift
            ;;
        --no-temp-clean)
            NO_TEMP_CLEAN=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --optimize)
            OPTIMIZE=true
            shift
            ;;
        --docker)
            DOCKER=true
            shift
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

# Main execution
print_header "🚀 UNIVERSAL BUILD SYSTEM"
print_info "Platform: $(uname) ($(uname -m))"
print_info "Current directory: $(pwd)"

# Cleanup system temp if not skipped
if [ "$NO_TEMP_CLEAN" = false ]; then
    cleanup_system_temp
fi

# Setup custom build temp
setup_build_temp

# Trap to ensure cleanup on exit
trap cleanup_build_temp EXIT

# Detect or use forced project type
if [ -n "$FORCE_TYPE" ]; then
    PROJECT_TYPE="$FORCE_TYPE"
    print_info "Forced project type: $PROJECT_TYPE"
else
    print_status "🔍 Detecting project type..."
    PROJECT_TYPE=$(detect_project_type 2>&1)
    if [[ $PROJECT_TYPE == error:* ]]; then
        print_error "${PROJECT_TYPE#error: }"
        exit 1
    fi

    # Show detection result
    case $PROJECT_TYPE in
        electron) print_info "Detected: Electron application" ;;
        python) print_info "Detected: Python application" ;;
        swift) print_info "Detected: Swift/macOS application" ;;
        typescript) print_info "Detected: TypeScript project" ;;
        webapp) print_info "Detected: Web application (SSR/SSG)" ;;
        spa) print_info "Detected: Single Page Application" ;;
        nodejs) print_info "Detected: Node.js application" ;;
        web) print_info "Detected: Static web application" ;;
        docker) print_info "Detected: Docker application" ;;
    esac
fi

# Clean previous builds if not skipped
if [ "$NO_CLEAN" = false ]; then
    print_status "🧹 Cleaning previous builds..."
    rm -rf dist/ build/ out/ .next/ .nuxt/
    print_success "Previous builds cleaned"
fi

# Execute appropriate build function
case $PROJECT_TYPE in
    electron)
        build_electron
        ;;
    python)
        build_python
        ;;
    swift)
        build_swift
        ;;
    typescript)
        build_typescript
        ;;
    web|webapp|spa)
        build_web
        ;;
    nodejs)
        build_nodejs
        ;;
    docker)
        print_status "🐳 Building Docker image..."
        docker build -t "$(basename "$(pwd)"):latest" .
        ;;
    *)
        print_error "Unsupported project type: $PROJECT_TYPE"
        exit 1
        ;;
esac

# Docker build (if requested and not already Docker type)
if [ "$DOCKER" = true ] && [ "$PROJECT_TYPE" != "docker" ]; then
    print_status "🐳 Creating Docker image..."
    
    # Create Dockerfile if not exists
    if [ ! -f "Dockerfile" ]; then
        print_status "Creating Dockerfile..."
        
        case $PROJECT_TYPE in
            nodejs|typescript|web|webapp|spa)
                cat > Dockerfile << 'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3000
CMD ["node", "dist/index.js"]
EOF
                ;;
            python)
                cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY dist ./dist
CMD ["python", "dist/main.py"]
EOF
                ;;
            *)
                print_warning "Cannot create Dockerfile for $PROJECT_TYPE"
                ;;
        esac
    fi
    
    if [ -f "Dockerfile" ]; then
        APP_NAME=$(basename "$(pwd)")
        docker build -t "$APP_NAME:latest" .
        
        if [ $? -eq 0 ]; then
            print_success "Docker image created: $APP_NAME:latest"
        fi
    fi
fi

# Final summary
print_header "✅ BUILD COMPLETE"

print_success "🎉 Build completed successfully!"
print_info "Project type: $PROJECT_TYPE"
print_info "Build outputs: ./dist/"

if [ -d "dist" ]; then
    TOTAL_SIZE=$(du -sh dist/ 2>/dev/null | cut -f1)
    FILE_COUNT=$(find dist -type f | wc -l)
    print_info "Total size: $TOTAL_SIZE"
    print_info "Total files: $FILE_COUNT"
fi

# Platform-specific instructions
print_header "📚 NEXT STEPS"

case $PROJECT_TYPE in
    electron)
        print_info "Run locally: npm start"
        print_info "Install packages from: ./dist/"
        ;;
    python)
        print_info "Run executable: ./dist/main/main"
        print_info "Install packages from: ./dist/"
        ;;
    swift)
        print_info "Run app: open ./dist/*.app"
        ;;
    web|webapp|spa)
        print_info "Serve locally: npx serve dist"
        print_info "Deploy to: Netlify, Vercel, or any static host"
        ;;
    nodejs|typescript)
        print_info "Run locally: node dist/index.js"
        ;;
esac

if [ "$DOCKER" = true ]; then
    APP_NAME=$(basename "$(pwd)")
    print_info "Run Docker: docker run -p 3000:3000 $APP_NAME:latest"
fi

print_info ""
print_success "Build system finished successfully! 🚀"