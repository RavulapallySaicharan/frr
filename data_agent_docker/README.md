# Data Agent Docker Setup

This folder contains all the Docker-related files for running the FRR Data Agent in a containerized environment.

## 📁 Files Included

- **`Dockerfile`** - Container definition with Python 3.13 and all dependencies
- **`.dockerignore`** - Excludes unnecessary files from build context
- **`docker-compose.yml`** - Service orchestration and configuration
- **`run-docker.sh`** - Linux/Mac script to build and run the container
- **`run-docker.bat`** - Windows batch file to build and run the container
- **`README.md`** - This documentation file

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# From the data_agent_docker directory
docker-compose up -d
```

### Option 2: Using Run Scripts

#### Linux/Mac
```bash
# From the data_agent_docker directory
./run-docker.sh
```

#### Windows
```cmd
# From the data_agent_docker directory
run-docker.bat
```

### Option 3: Manual Docker Commands

```bash
# From the parent directory (frr/)
docker build -t frr-data-agent -f data_agent_docker/Dockerfile .
docker run -d --name frr-data-agent -p 8000:8000 frr-data-agent
```

## 🌐 Access

Once running, your data agent will be available at:
- **URL**: http://localhost:8000
- **API Endpoints**: Available through the A2A framework

## 📊 Data Files

The container automatically includes:
- `sample_soi_data.csv` - Built into the image
- Additional data can be mounted via volumes

## 🛠️ Container Management

```bash
# View logs
docker logs frr-data-agent

# Stop container
docker stop frr-data-agent

# Remove container
docker rm frr-data-agent

# Restart container
docker restart frr-data-agent
```

## 🔧 Configuration

### Environment Variables
- `PYTHONUNBUFFERED=1` - Ensures Python output is not buffered
- `PYTHONDONTWRITEBYTECODE=1` - Prevents writing .pyc files

### Ports
- **8000** - Main application port

### Volumes
- `../data:/app/data` - Persistent data storage

## 📋 Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB available RAM
- At least 1GB available disk space

## 🐛 Troubleshooting

### Build Issues
- Ensure you're running from the `data_agent_docker` directory
- Check that all required files exist in the parent directory
- Verify Docker has sufficient resources

### Runtime Issues
- Check container logs: `docker logs frr-data-agent`
- Verify port 8000 is not already in use
- Ensure the CSV data file is accessible

### Performance Issues
- Increase Docker memory allocation if needed
- Monitor resource usage with `docker stats frr-data-agent` 