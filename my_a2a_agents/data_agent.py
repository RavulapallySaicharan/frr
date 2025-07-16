import asyncio
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message, new_task
from a2a.types import UnsupportedOperationError, InvalidParamsError, InternalError, TaskState, Part, TextPart
from a2a.utils.errors import ServerError
from a2a.server.tasks import TaskUpdater
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

# Dummy DataAgent logic
class DataAgent:
    """Agent that returns dummy tabular data."""
    async def invoke(self, query: str = None, **kwargs) -> Dict[str, Any]:
        # Simulate fetching tabular data
        return {
            "status": "completed",
            "content": "column1,column2\n1,4\n2,5\n3,6"
        }

class DataAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = DataAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())
        query = context.get_user_input() if hasattr(context, 'get_user_input') else None
        task = getattr(context, 'current_task', None)
        if not task:
            task = new_task(context.message)  # type: ignore
            event_queue.enqueue_event(task)  # Do NOT await
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        try:
            result = await self.agent.invoke(query)
            await updater.add_artifact(
                [Part(root=TextPart(text=result['content']))],
                name='data_result',
            )
            await updater.complete()
        except Exception as e:
            logger.error(f'An error occurred while processing the data agent: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())

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
        skills=[skill]
    ) 

