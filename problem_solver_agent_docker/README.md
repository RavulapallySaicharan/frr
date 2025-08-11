# Problem Solver Agent Docker Setup

This folder contains Docker files for running the FRR Problem Solver Agent.

## 📁 Files Included

- **`Dockerfile`** - Container with Python 3.13 and dependencies
- **`.dockerignore`** - Build exclusions
- **`docker-compose.yml`** - Service orchestration
- **`run-docker.sh`** - Linux/Mac run script
- **`run-docker.bat`** - Windows run script
- **`README.md`** - This documentation

## 🚀 Quick Start

### Prerequisites
```bash
export OPENAI_API_KEY="your_openai_api_key"
export LITELLM_MODEL="gpt-4"
```

### Using Docker Compose
```bash
# From problem_solver_agent_docker directory
docker-compose up -d
```

### Using Run Scripts
```bash
# Linux/Mac
./run-docker.sh

# Windows
run-docker.bat
```

## 🌐 Access
- **URL**: http://localhost:8001
- **Port**: 8001 (different from data agent)

## 🛠️ Management
```bash
# View logs
docker logs frr-problem-solver-agent

# Stop container
docker stop frr-problem-solver-agent

# Remove container
docker rm frr-problem-solver-agent
```

## 🔧 Configuration
- **Environment Variables**: OPENAI_API_KEY, LITELLM_MODEL
- **Port Mapping**: 8001:8000
- **Health Checks**: Every 30 seconds

## 🐛 Troubleshooting
- Ensure environment variables are set
- Check port 8001 availability
- Verify Docker resources
- Review container logs 