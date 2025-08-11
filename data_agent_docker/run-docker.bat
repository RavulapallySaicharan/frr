@echo off
echo 🚀 Building and running FRR Data Agent Docker container...
echo This script should be run from the data_agent_docker directory

REM Change to parent directory for build context
cd ..

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t frr-data-agent -f data_agent_docker/Dockerfile .

if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully!
    
    REM Run the container
    echo 🐳 Starting container...
    docker run -d --name frr-data-agent -p 8000:8000 -v "%cd%\data:/app/data" --restart unless-stopped frr-data-agent
    
    if %errorlevel% equ 0 (
        echo ✅ Container started successfully!
        echo 🌐 Data Agent is running on http://localhost:8000
        echo 📊 You can now access the data agent API
        echo.
        echo 📋 Container logs:
        docker logs frr-data-agent
        echo.
        echo 🛑 To stop the container: docker stop frr-data-agent
        echo 🗑️  To remove the container: docker rm frr-data-agent
    ) else (
        echo ❌ Failed to start container
        exit /b 1
    )
) else (
    echo ❌ Failed to build Docker image
    exit /b 1
)

pause 