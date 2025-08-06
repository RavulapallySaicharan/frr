"""
Simple Agent Template
====================

A basic conversational agent without any tools.
This template provides a minimal working setup for creating a simple agent.

TODO: Fill in the TODO sections below to customize your agent.
"""

import asyncio
import logging
import sys
import argparse
from typing import Any, Dict
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message, new_task
from a2a.types import UnsupportedOperationError, InvalidParamsError, InternalError, TaskState, Part, TextPart
from a2a.utils.errors import ServerError
from a2a.server.tasks import TaskUpdater
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
import uvicorn

# Google ADK imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types

logger = logging.getLogger(__name__)

class SimpleAgent:
    """
    Simple conversational agent using Google ADK.
    
    TODO: Update the agent name, description, and model configuration
    """
    
    def __init__(self):
        # TODO: Configure your model name (e.g., "gpt-4", "gpt-3.5-turbo")
        self.model_name = "gpt-4"  # TODO: Change this to your preferred model
        
        # TODO: Update agent name and description
        self.agent_name = "simple_agent"  # TODO: Change to your agent name
        self.agent_description = "A simple conversational agent"  # TODO: Update description
        
        self.agent = None
        self._initialize_agent()
    
    def process_conversation(self, query: str) -> str:
        """
        Process user conversation and generate response.
        
        TODO: Implement your conversation logic here
        This is where you define how your agent responds to user input.
        """
        try:
            # TODO: Add your conversation logic here
            # Examples:
            # - Simple echo response
            # - Pattern matching for specific commands
            # - Integration with external APIs
            # - Custom business logic
            
            # Default response - replace with your logic
            if not query or query.strip() == "":
                return "Hello! I'm a simple agent. How can I help you today?"
            
            # TODO: Add your custom conversation logic here
            # Example: Simple echo with some processing
            response = f"I received your message: '{query}'. This is a placeholder response."
            
            # TODO: Add more sophisticated logic as needed
            # - Analyze user intent
            # - Generate contextual responses
            # - Handle different conversation flows
            
            return response
                
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent."""
        try:
            # Create agent without tools (simple conversational agent)
            self.agent = Agent(
                name=self.agent_name,
                description=self.agent_description,
                tools=[],  # No tools for simple agent
                model=LiteLlm(model=self.model_name)
            )
            logger.info(f"Google ADK {self.agent_name} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google ADK agent: {e}")
            raise e
    
    async def invoke(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process user queries using Google ADK agent with Runner pattern.
        
        TODO: Customize the session and app configuration if needed
        """
        try:
            if not query or query.strip() == "":
                return {
                    "status": "error",
                    "content": "No query provided"
                }
            
            if not self.agent:
                raise Exception("Google ADK agent not initialized")
            
            # TODO: Customize session and artifact services if needed
            session_service = InMemorySessionService()
            artifacts_service = InMemoryArtifactService()
            
            # TODO: Update app_name and user_id as needed
            session = await session_service.create_session(
                state={}, 
                app_name='simple_app',  # TODO: Change to your app name
                user_id='user_simple'   # TODO: Change to your user ID
            )

            # Create content for the query
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            # Create runner
            runner = Runner(
                app_name='simple_app',  # TODO: Change to your app name
                agent=self.agent,
                artifact_service=artifacts_service,
                session_service=session_service,
            )
            
            # Run the agent and collect results
            result_content = ""
            events_async = runner.run_async(
                session_id=session.id, 
                user_id=session.user_id, 
                new_message=content
            )
            
            async for event in events_async:
                if hasattr(event, 'content') and event.content:
                    result_content += str(event.content)
                elif hasattr(event, 'text') and event.text:
                    result_content += str(event.text)
                elif hasattr(event, 'message') and event.message:
                    result_content += str(event.message)
            
            # TODO: Add custom response processing if needed
            # If no response from agent, use our custom logic
            if not result_content:
                result_content = self.process_conversation(query)
            
            return {
                "status": "completed",
                "content": result_content if result_content else "No response generated"
            }
            
        except Exception as e:
            logger.error(f"Error in simple agent invoke: {e}")
            return {
                "status": "error",
                "content": f"Error processing request: {str(e)}"
            }

class SimpleAgentExecutor(AgentExecutor):
    """
    A2A SDK executor for the simple agent.
    
    TODO: Update the executor name and any custom logic
    """
    
    def __init__(self):
        self.agent = SimpleAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Execute the simple agent request.
        
        TODO: Add custom validation or preprocessing if needed
        """
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())
        
        # TODO: Customize how you extract the user input
        query = context.get_user_input() if hasattr(context, 'get_user_input') else None
        task = getattr(context, 'current_task', None)
        if not task:
            task = new_task(context.message)  # type: ignore
            event_queue.enqueue_event(task)  # Do NOT await
        
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        
        try:
            result = await self.agent.invoke(query)
            updater.add_artifact(
                [Part(root=TextPart(text=result['content']))],
                name='simple_result',  # TODO: Change artifact name if needed
            )
            updater.complete()
        except Exception as e:
            logger.error(f'An error occurred while processing the simple agent: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        """
        Validate the incoming request.
        
        TODO: Add custom validation logic if needed
        """
        return False

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle cancellation requests."""
        raise ServerError(error=UnsupportedOperationError())

# TODO: Update the skill definition for your agent
skill = AgentSkill(
    id="simple_conversation",  # TODO: Change to your skill ID
    name="Simple Conversation",  # TODO: Change to your skill name
    description="A simple conversational agent for basic interactions.",  # TODO: Update description
    tags=["conversation", "simple", "chat"],  # TODO: Update tags
    examples=[
        "Hello, how are you?",
        "What can you do?",
        "Tell me a joke",
        "Help me with a question"
    ]  # TODO: Update examples
)

def get_agent_card(host: str, port: int):
    """
    Create the agent card for A2A SDK registration.
    
    TODO: Update the agent card details
    """
    capabilities = AgentCapabilities(streaming=False, pushNotifications=False)
    return AgentCard(
        name="Simple Agent",  # TODO: Change to your agent name
        description="A simple conversational agent using Google ADK.",  # TODO: Update description
        url=f"http://{host}:{port}/",
        version="1.0.0",  # TODO: Update version
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        capabilities=capabilities,
        skills=[skill]
    )

if __name__ == "__main__":
    # get the host and port from the command line like --host 0.0.0.0 --port 8000 using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    host = args.host
    port = args.port
    print(f"Running on {host}:{port}")
    app = A2AStarletteApplication(
        http_handler=DefaultRequestHandler(
            agent_executor=SimpleAgentExecutor(),
            task_store=InMemoryTaskStore()),
        agent_card=get_agent_card(host, port)
    )
    uvicorn.run(app.build(), host=host, port=port) 