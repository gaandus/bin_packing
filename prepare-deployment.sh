#!/bin/bash
# Script to prepare bin packing app for deployment

# Create necessary directories
mkdir -p data

# Ensure file permissions are correct
chmod +x prepare-deployment.sh

# Create a deployment package
echo "Creating deployment package..."
DEPLOY_DIR="bin-packing-deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy necessary files to deployment directory
cp -r static templates solver.py web_app.py Dockerfile docker-compose.yml .dockerignore requirements.txt nginx-config.conf deployment-instructions.md $DEPLOY_DIR/

# Create data directory in deployment package
mkdir -p $DEPLOY_DIR/data

# Print instructions
echo "======================================"
echo "Deployment package created: $DEPLOY_DIR"
echo "======================================"
echo "Upload this directory to your VPS and follow the instructions in deployment-instructions.md"
echo "======================================" 