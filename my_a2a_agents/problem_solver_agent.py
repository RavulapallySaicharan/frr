import asyncio
from a2a.agent import AgentSkill, AgentCard, AgentCapabilities, AgentAuthentication
from a2a.executor import BaseAgentExecutor
from a2a.protocol import RequestContext, EventQueue, new_agent_text_message
from typing import Any, Dict

# Dummy ProblemSolverAgent logic
class ProblemSolverAgent:
    """Agent that solves a problem based on input data."""
    async def invoke(self, data: str = None, **kwargs) -> Dict[str, Any]:
        # Simulate solving a problem with the data
        solution = f"Processed data: {data if data else 'No data provided'}"
        return {
            "status": "completed",
            "content": solution
        }

class ProblemSolverAgentExecutor(BaseAgentExecutor):
    def __init__(self):
        self.agent = ProblemSolverAgent()

    async def on_message_send(self, request, event_queue: EventQueue, task=None):
        # For simplicity, just echo a dummy solution
        # In a real scenario, extract data from the request
        data = "dummy input data"
        result = await self.agent.invoke(data=data)
        event_queue.enqueue_event(new_agent_text_message(result["content"]))

# Agent skill and card definition
skill = AgentSkill(
    id="solve_problem",
    name="Problem Solver",
    description="Solves a problem using provided data.",
    tags=["problem", "solution"],
    examples=["Solve a problem with this data"]
)

def get_agent_card(host: str, port: int):
    capabilities = AgentCapabilities(streaming=False, pushNotifications=False)
    return AgentCard(
        name="Problem Solver Agent",
        description="Agent that solves problems using data.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        capabilities=capabilities,
        skills=[skill],
        authentication=AgentAuthentication(schemes=["public"]),
    ) 