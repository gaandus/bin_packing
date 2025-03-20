#!/bin/bash
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Build the Docker container
echo "Building Docker container..."
docker build -t bin-packing .

echo "Starting Bin Packing Web Application..."
echo "The application will be available at http://localhost:5000"

# Run Docker container with port mapping
docker run --rm -p 5000:5000 bin-packing

# Open browser
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start http://localhost:5000
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:5000
else
    # Linux
    xdg-open http://localhost:5000 &> /dev/null || echo "Please open your browser and navigate to http://localhost:5000"
fi 