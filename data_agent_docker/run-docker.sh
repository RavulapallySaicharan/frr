#!/bin/bash

# Script to build and run the FRR Data Agent Docker container
# This script should be run from the data_agent_docker directory

echo "🚀 Building and running FRR Data Agent Docker container..."

# Change to parent directory for build context
cd ..

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t frr-data-agent -f data_agent_docker/Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    # Run the container
    echo "🐳 Starting container..."
    docker run -d \
        --name frr-data-agent \
        -p 8000:8000 \
        -v "$(pwd)/data:/app/data" \
        --restart unless-stopped \
        frr-data-agent
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "🌐 Data Agent is running on http://localhost:8000"
        echo "📊 You can now access the data agent API"
        echo ""
        echo "📋 Container logs:"
        docker logs frr-data-agent
        echo ""
        echo "🛑 To stop the container: docker stop frr-data-agent"
        echo "🗑️  To remove the container: docker rm frr-data-agent"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
else
    echo "❌ Failed to build Docker image"
    exit 1
fi 