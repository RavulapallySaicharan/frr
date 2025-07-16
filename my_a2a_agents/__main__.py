import uvicorn
import httpx
import threading
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, InMemoryPushNotifier
# from a2a.protocol import AgentSkill
from .data_agent import DataAgentExecutor, get_agent_card as get_data_agent_card, skill as data_skill
from .problem_solver_agent import ProblemSolverAgentExecutor, get_agent_card as get_problem_solver_agent_card, skill as solver_skill

import os

HOST = os.environ.get("A2A_HOST", "127.0.0.1")
PORT_DATA = int(os.environ.get("A2A_DATA_PORT", 9999))
PORT_SOLVER = int(os.environ.get("A2A_SOLVER_PORT", 9998))

AGENT_TYPE = os.environ.get("A2A_AGENT_TYPE")  # "data", "solver", or None

httpx_client = httpx.AsyncClient()

def make_app(executor, get_agent_card, host, port):
    return A2AStarletteApplication(
        http_handler=DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client)
        ),
        agent_card=get_agent_card(host, port)
    )

def run_uvicorn(app, host, port, agent_name):
    print(f"Starting {agent_name} on {host}:{port}")
    uvicorn.run(app.build(), host=host, port=port)

if AGENT_TYPE == "data":
    app = make_app(DataAgentExecutor(), get_data_agent_card, HOST, PORT_DATA)
    run_uvicorn(app, HOST, PORT_DATA, "Data Agent")
elif AGENT_TYPE == "solver":
    app = make_app(ProblemSolverAgentExecutor(), get_problem_solver_agent_card, HOST, PORT_SOLVER)
    run_uvicorn(app, HOST, PORT_SOLVER, "Problem Solver Agent")
else:
    # Run both agents at once in separate threads
    data_app = make_app(DataAgentExecutor(), get_data_agent_card, HOST, PORT_DATA)
    solver_app = make_app(ProblemSolverAgentExecutor(), get_problem_solver_agent_card, HOST, PORT_SOLVER)

    t1 = threading.Thread(target=run_uvicorn, args=(data_app, HOST, PORT_DATA, "Data Agent"), daemon=True)
    t2 = threading.Thread(target=run_uvicorn, args=(solver_app, HOST, PORT_SOLVER, "Problem Solver Agent"), daemon=True)
    t1.start()
    t2.start()
    print(f"Both agents are running: Data Agent on {HOST}:{PORT_DATA}, Problem Solver Agent on {HOST}:{PORT_SOLVER}")
    t1.join()
    t2.join() 