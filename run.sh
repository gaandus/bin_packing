#!/bin/bash
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# For Windows/WSL users, make sure X server is running
if [[ "$(uname -s)" == "Linux" && -z "$WSL_DISTRO_NAME" ]]; then
    # For native Linux
    # Update Docker config for X server
    sed -i 's/DISPLAY=host.docker.internal:0.0/DISPLAY=$DISPLAY/' docker-compose.yml
    sed -i 's/# network_mode/network_mode/' docker-compose.yml
    sed -i 's/# environment:/environment:/' docker-compose.yml
    sed -i 's/#   - DISPLAY/$DISPLAY/  - DISPLAY=$DISPLAY/' docker-compose.yml
elif [[ "$(uname -s)" == "Linux" && ! -z "$WSL_DISTRO_NAME" ]]; then
    # For WSL
    echo "Running on WSL. Make sure X-server (like VcXsrv) is running on Windows."
    sed -i 's/DISPLAY=host.docker.internal:0.0/DISPLAY=$DISPLAY/' docker-compose.yml
fi

echo "Building Docker container..."
docker-compose build

echo "Starting Bin Packing application..."
docker-compose up 