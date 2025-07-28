# My A2A Agents

This folder contains two advanced A2A-compatible agents implemented using the [a2a-sdk](https://pypi.org/project/a2a-sdk/) with Google's Agent Development Kit (ADK) and LiteLLM for OpenAI model integration.

- **data_agent**: Advanced data processing and analysis agent with AI-powered insights
- **problem_solver_agent**: Intelligent problem-solving agent with multiple solution approaches

## Features

### Data Agent
- **Data Generation**: Create sample CSV data with meaningful columns
- **Data Analysis**: Statistical analysis, correlation matrices, trend detection
- **Data Filtering**: Filter data based on custom criteria
- **AI-Powered Insights**: Intelligent data interpretation and recommendations

### Problem Solver Agent
- **Problem Analysis**: Break down complex problems into components
- **Solution Generation**: Multiple approaches (algorithmic, heuristic, optimization, creative)
- **Solution Evaluation**: Quality assessment with multiple criteria
- **Solution Optimization**: Improve existing solutions for better performance

## Requirements
- Python 3.10+
- `a2a-sdk` (install with `pip install a2a-sdk`)
- `uvicorn` (for running the server)
- `litellm` (for OpenAI model integration)
- `google-adk` (for Google Agent Development Kit)

## Installation

1. Install dependencies:
```bash
pip install -r ../requirements.txt
```

2. Set up environment variables:
   - Copy `env_example.txt` to `.env`
   - Fill in your API keys and configuration

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID (for Google ADK)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account key file (for Google ADK)

## Running an Agent (All Platforms)

You can run either agent as an A2A server by setting the `A2A_AGENT_TYPE` environment variable.

### macOS / Linux / Linux Server

#### Data Agent
```bash
export A2A_AGENT_TYPE=data
python -m my_a2a_agents
```

#### Problem Solver Agent
```bash
export A2A_AGENT_TYPE=solver
python -m my_a2a_agents
```

#### Custom Host/Port (optional)
```bash
export A2A_HOST=127.0.0.1
export A2A_PORT=8080
python -m my_a2a_agents
```

### Windows (Command Prompt)

#### Data Agent
```bat
set A2A_AGENT_TYPE=data
python -m my_a2a_agents
```

#### Problem Solver Agent
```bat
set A2A_AGENT_TYPE=solver
python -m my_a2a_agents
```

#### Custom Host/Port (optional)
```bat
set A2A_HOST=127.0.0.1
set A2A_PORT=8080
python -m my_a2a_agents
```

### Windows (PowerShell)

#### Data Agent
```powershell
$env:A2A_AGENT_TYPE="data"
python -m my_a2a_agents
```

#### Problem Solver Agent
```powershell
$env:A2A_AGENT_TYPE="solver"
python -m my_a2a_agents
```

#### Custom Host/Port (optional)
```powershell
$env:A2A_HOST="127.0.0.1"
$env:A2A_PORT="8080"
python -m my_a2a_agents
```

The server will start on `0.0.0.0:9999` by default. You can override the host/port as shown above.

## API Endpoints
- `GET /.well-known/agent.json` — Agent card
- `POST /agent/message` — Send a message to the agent

## Example Usage

### Data Agent Examples
```bash
# Get sample data
curl -X POST http://localhost:9999/agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "Generate sample sales data for Q1 2024"}]}}'

# Analyze data
curl -X POST http://localhost:9999/agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "Analyze this data for trends and correlations"}]}}'
```

### Problem Solver Agent Examples
```bash
# Analyze a problem
curl -X POST http://localhost:9998/agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "Analyze this optimization problem for a delivery routing system"}]}}'

# Generate solutions
curl -X POST http://localhost:9998/agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "Generate algorithmic solutions for this sorting problem"}]}}'
```

## Project Structure
```
my_a2a_agents/
  data_agent.py              # Advanced data processing agent
  problem_solver_agent.py    # Intelligent problem-solving agent
  config.py                  # Configuration management
  env_example.txt           # Environment variables template
  __main__.py               # Main entry point
  README.md                 # This file
```

## Technology Stack

- **Google ADK**: Agent Development Kit for advanced agent capabilities with tool integration
- **LiteLLM**: Unified interface for multiple LLM providers, integrated with Google ADK
- **OpenAI GPT-4o-mini**: Primary language model for reasoning via LiteLLM
- **Google Cloud**: Platform for Google ADK services
- **Pandas**: Data manipulation and analysis
- **A2A SDK**: Agent-to-Agent communication protocol

## How It Works

The agents use a hybrid approach:
1. **Primary**: Google ADK agents with LiteLLM models for tool-based reasoning
2. **Fallback**: Direct LiteLLM calls when Google ADK is unavailable
3. **Tools**: Functions as tools for data processing and problem-solving
4. **Modern Implementation**: Uses latest Google ADK patterns with function-based tools

## References
- [A2A Langgraph Sample](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/langgraph)
- [A2A SDK Documentation](https://google.github.io/A2A/)
- [Google ADK Documentation](https://developers.google.com/agent-development-kit)
- [LiteLLM Documentation](https://docs.litellm.ai/) 