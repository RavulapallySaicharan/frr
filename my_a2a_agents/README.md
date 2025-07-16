# My A2A Agents

This folder contains two A2A-compatible agents implemented using the [a2a-sdk](https://pypi.org/project/a2a-sdk/) and following the conventions of the official A2A langgraph sample.

- **data_agent**: Handles data-related tasks (fetches and returns tabular data)
- **problem_solver_agent**: Solves problems using input data (returns a dummy solution)

## Requirements
- Python 3.10+
- `a2a-sdk` (install with `pip install a2a-sdk`)
- `uvicorn` (for running the server)

## Installation
```bash
pip install a2a-sdk uvicorn
```

## Running an Agent (All Platforms)

You can run either agent as an A2A server by setting the `A2A_AGENT_TYPE` environment variable. See below for OS-specific instructions.

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

## Example Test (with curl)
```bash
curl -X POST http://localhost:9999/agent/message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "Get the data table"}]}}'
```

## Project Structure
```
my_a2a_agents/
  data_agent.py
  problem_solver_agent.py
  __main__.py
  README.md
```

## References
- [A2A Langgraph Sample](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/langgraph)
- [A2A SDK Documentation](https://google.github.io/A2A/) 