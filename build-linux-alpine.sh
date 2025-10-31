#!/bin/bash

# Build VideoWall for Linux using Docker with Alpine Linux
# This script creates a Docker container with all dependencies and builds the Linux binary

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

print_status "Building VideoWall for Linux using Docker (Alpine)..."

# Create a temporary Dockerfile with Alpine
DOCKERFILE="$PROJECT_DIR/Dockerfile.alpine"
cat > "$DOCKERFILE" << 'EOF'
FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache \
    xvfb \
    libx11-dev \
    libxtst-dev \
    libxrandr-dev \
    libxss-dev \
    libxcursor-dev \
    libxcomposite-dev \
    libxi-dev \
    libgconf-2-4 \
    libasound2-dev \
    libgbm-dev \
    libxrender-dev \
    libxkbfile-dev \
    pango-dev \
    cairo-dev \
    gdk-pixbuf-dev \
    gtk+3.0-dev \
    gcc \
    musl-dev \
    linux-headers \
    py3-pyqt5 \
    mesa-dev \
    libglvnd-dev

# Install PyInstaller
RUN pip install pyinstaller==6.16.0

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install PyQt5 PyQt5Multimedia requests

# Build the application with display
RUN export DISPLAY=:99 && Xvfb :99 -screen 0 1024x768x24 & && \
    sleep 2 && \
    pyinstaller VideoWall-linux.spec --clean --noconfirm && \
    killall Xvfb || true

# Create output directory
RUN mkdir -p /output

# Copy the built binary
RUN cp -r dist/* /output/ 2>/dev/null || true

# Set permissions
RUN chmod +x /output/VideoWall 2>/dev/null || true

EOF

# Build Docker image
print_status "Building Docker image with Alpine..."
if docker build -f "$DOCKERFILE" -t videowall-linux-alpine "$PROJECT_DIR"; then
    # Create output directory
    mkdir -p "$PROJECT_DIR/dist/Linux"

    # Run container and copy output
    print_status "Extracting Linux binary from Docker..."
    docker run --rm -v "$PROJECT_DIR/dist/Linux":/output_host videowall-linux-alpine bash -c "cp -r /output/* /output_host/ 2>/dev/null || true"

    # Clean up Dockerfile
    rm -f "$DOCKERFILE"

    # Check if binary was created
    if [ -f "$PROJECT_DIR/dist/Linux/VideoWall" ]; then
        print_success "Linux binary built successfully!"
        print_status "Binary location: $PROJECT_DIR/dist/Linux/VideoWall"
    else
        print_error "Binary not found. Build may have failed."
        exit 1
    fi
else
    print_error "Docker build failed. Please check the output above."
    rm -f "$DOCKERFILE"
    exit 1
fi

# Create a run script for Linux
cat > "$PROJECT_DIR/dist/Linux/run-VideoWall.sh" << EOF
#!/bin/bash

# Run VideoWall on Linux
# This script sets up the environment and runs the VideoWall binary

# Get the directory where this script is located
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
BINARY_DIR="\$SCRIPT_DIR"

# Set library path
export LD_LIBRARY_PATH="\$BINARY_DIR:\$LD_LIBRARY_PATH"

# Set Qt plugin path
export QT_PLUGIN_PATH="\$BINARY_DIR/plugins:\$QT_PLUGIN_PATH"

# Set display for headless environments
if [ -z "\$DISPLAY" ]; then
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 &
    XVFB_PID=\$!
    sleep 2
    trap "kill \$XVFB_PID 2>/dev/null || true" EXIT
fi

# Run the application
echo "Starting VideoWall..."
echo "Binary: \$BINARY_DIR/VideoWall"

if [ -f "\$BINARY_DIR/VideoWall" ]; then
    cd "\$BINARY_DIR"
    ./VideoWall "\$@"
else
    echo "Error: VideoWall binary not found at \$BINARY_DIR/VideoWall"
    exit 1
fi
EOF

# Make the run script executable
chmod +x "$PROJECT_DIR/dist/Linux/run-VideoWall.sh"

print_success "Linux run script created: $PROJECT_DIR/dist/Linux/run-VideoWall.sh"
print_warning "To run on Linux:"
print_warning "  1. Copy the entire dist/Linux folder to your Linux machine"
print_warning "  2. Run: ./run-VideoWall.sh"

# Show the created files
print_status "Created files:"
ls -la "$PROJECT_DIR/dist/Linux/" 2>/dev/null || echo "No files found in dist/Linux/"