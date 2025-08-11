@echo off
echo 🚀 Building and running FRR Problem Solver Agent Docker container...
echo This script should be run from the problem_solver_agent_docker directory

REM Change to parent directory for build context
cd ..

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t frr-problem-solver-agent -f problem_solver_agent_docker/Dockerfile .

if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully!
    
    REM Run the container
    echo 🐳 Starting container...
    docker run -d --name frr-problem-solver-agent -p 8001:8000 -e OPENAI_API_KEY="%OPENAI_API_KEY%" -e LITELLM_MODEL="%LITELLM_MODEL%" --restart unless-stopped frr-problem-solver-agent
    
    if %errorlevel% equ 0 (
        echo ✅ Container started successfully!
        echo 🌐 Problem Solver Agent is running on http://localhost:8001
        echo 🧠 You can now access the problem solver agent API
        echo.
        echo 📋 Container logs:
        docker logs frr-problem-solver-agent
        echo.
        echo 🛑 To stop the container: docker stop frr-problem-solver-agent
        echo 🗑️  To remove the container: docker rm frr-problem-solver-agent
        echo.
        echo ⚠️  Note: Make sure OPENAI_API_KEY and LITELLM_MODEL environment variables are set
    ) else (
        echo ❌ Failed to start container
        exit /b 1
    )
) else (
    echo ❌ Failed to build Docker image
    exit /b 1
)

pause 