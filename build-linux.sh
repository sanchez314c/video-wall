#!/bin/bash

# Build VideoWall for Linux using Docker
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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

print_status "Building VideoWall for Linux using Docker..."

# Create a temporary Dockerfile
DOCKERFILE="$PROJECT_DIR/Dockerfile.linux"
cat > "$DOCKERFILE" << 'EOF'
FROM python:3.11-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pyqt5 \
    python3-pyqt5.qtmultimedia \
    python3-pyqt5.qtquick \
    qt5-default \
    libqt5multimedia5-plugins \
    libqt5multimediawidgets5 \
    libqt5multimedia5 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    libqt5network5 \
    libqt5svg5 \
    libglib2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libgirepository-1.0-1 \
    gir1.2-gtk-3.0 \
    gir1.2-gdkpixbuf-2.0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyInstaller
RUN pip install pyinstaller==6.16.0

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install PyQt5 PyQt5Multimedia requests

# Build the application
RUN pyinstaller VideoWall-linux.spec --clean --noconfirm

# Create output directory
RUN mkdir -p /output

# Copy the built binary
RUN cp -r dist/* /output/

# Set permissions
RUN chmod +x /output/VideoWall

EOF

# Build Docker image
print_status "Building Docker image..."
docker build -f "$DOCKERFILE" -t videowall-linux-builder "$PROJECT_DIR"

# Create output directory
mkdir -p "$PROJECT_DIR/dist/Linux"

# Run container and copy output
print_status "Building Linux binary in Docker..."
docker run --rm -v "$PROJECT_DIR/dist/Linux":/output_host videowall-linux-builder bash -c "cp -r /output/* /output_host/"

# Clean up Dockerfile
rm -f "$DOCKERFILE"

print_success "Linux binary built successfully!"
print_status "Binary location: $PROJECT_DIR/dist/Linux/VideoWall"

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
print_warning "To run on Linux: ./run-VideoWall.sh"

# Show the created files
print_status "Created files:"
ls -la "$PROJECT_DIR/dist/Linux/"