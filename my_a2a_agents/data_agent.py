import asyncio
from a2a.agent import AgentSkill, AgentCard, AgentCapabilities, AgentAuthentication
from a2a.executor import BaseAgentExecutor
from a2a.protocol import RequestContext, EventQueue, new_agent_text_message
from typing import Any, Dict

# Dummy DataAgent logic
class DataAgent:
    """Agent that returns dummy tabular data."""
    async def invoke(self, query: str = None, **kwargs) -> Dict[str, Any]:
        # Simulate fetching tabular data
        return {
            "status": "completed",
            "content": "column1,column2\n1,4\n2,5\n3,6"
        }

class DataAgentExecutor(BaseAgentExecutor):
    def __init__(self):
        self.agent = DataAgent()

    async def on_message_send(self, request, event_queue: EventQueue, task=None):
        # For simplicity, just echo a dummy table
        result = await self.agent.invoke()
        event_queue.enqueue_event(new_agent_text_message(result["content"]))

# Agent skill and card definition
skill = AgentSkill(
    id="get_data",
    name="Data Fetcher",
    description="Fetches and returns tabular data.",
    tags=["data", "table"],
    examples=["Get the data table"]
)

def get_agent_card(host: str, port: int):
    capabilities = AgentCapabilities(streaming=False, pushNotifications=False)
    return AgentCard(
        name="Data Agent",
        description="Agent that provides tabular data.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        capabilities=capabilities,
        skills=[skill],
        authentication=AgentAuthentication(schemes=["public"]),
    ) 