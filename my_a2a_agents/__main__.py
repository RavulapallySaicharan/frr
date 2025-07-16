import uvicorn
from a2a.server import A2AStarletteApplication, DefaultA2ARequestHandler, InMemoryTaskStore
from a2a.protocol import AgentSkill
from data_agent import DataAgentExecutor, get_agent_card as get_data_agent_card, skill as data_skill
from problem_solver_agent import ProblemSolverAgentExecutor, get_agent_card as get_problem_solver_agent_card, skill as solver_skill

import os

HOST = os.environ.get("A2A_HOST", "0.0.0.0")
PORT = int(os.environ.get("A2A_PORT", 9999))

# Choose which agent to run (for demo, just data_agent)
AGENT_TYPE = os.environ.get("A2A_AGENT_TYPE", "data")  # "data" or "solver"

if AGENT_TYPE == "data":
    executor = DataAgentExecutor()
    get_agent_card = get_data_agent_card
    skills = [data_skill]
    agent_name = "Data Agent"
else:
    executor = ProblemSolverAgentExecutor()
    get_agent_card = get_problem_solver_agent_card
    skills = [solver_skill]
    agent_name = "Problem Solver Agent"

# Set up the A2A app
app = A2AStarletteApplication(
    request_handler=DefaultA2ARequestHandler(executor=executor),
    task_store=InMemoryTaskStore(),
    get_agent_card=lambda: get_agent_card(HOST, PORT),
    skills=skills,
)

if __name__ == "__main__":
    print(f"Starting {agent_name} on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT) 