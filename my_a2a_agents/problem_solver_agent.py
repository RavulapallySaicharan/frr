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

class ProblemSolverAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = ProblemSolverAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())
        data = context.get_user_input() if hasattr(context, 'get_user_input') else None
        task = getattr(context, 'current_task', None)
        if not task:
            task = new_task(context.message)  # type: ignore
            event_queue.enqueue_event(task)  # Do NOT await
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        try:
            result = await self.agent.invoke(data=data)
            await updater.add_artifact(
                [Part(root=TextPart(text=result['content']))],
                name='solution_result',
            )
            await updater.complete()
        except Exception as e:
            logger.error(f'An error occurred while processing the problem solver agent: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())

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
        skills=[skill]
    ) 