#!/bin/bash
# Script to rebuild the bin packing Docker container

echo "Stopping and removing existing container..."
docker stop bin-packing || true
docker rm bin-packing || true

echo "Building new container..."
docker build -t bin-packing .

echo "Starting new container..."
docker run -d --name bin-packing --restart always -p 127.0.0.1:5000:5000 -v $(pwd)/data:/app/data bin-packing

echo "Checking container status..."
docker ps -a | grep bin-packing

echo "Viewing logs..."
docker logs bin-packing 