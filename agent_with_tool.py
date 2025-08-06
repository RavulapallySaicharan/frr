"""
Agent with Single Tool Template
==============================

A conversational agent that integrates one external tool.
This template shows how to create an agent with a single tool.

TODO: Fill in the TODO sections below to customize your agent and tool.
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

class AgentWithTool:
    """
    Agent with a single tool using Google ADK.
    
    TODO: Update the agent name, description, and model configuration
    """
    
    def __init__(self):
        # TODO: Configure your model name (e.g., "gpt-4", "gpt-3.5-turbo")
        self.model_name = "gpt-4"  # TODO: Change this to your preferred model
        
        # TODO: Update agent name and description
        self.agent_name = "agent_with_tool"  # TODO: Change to your agent name
        self.agent_description = "An agent with a single tool for specific tasks"  # TODO: Update description
        
        self.agent = None
        self._initialize_agent()
    
    def my_tool(self, input_data: str) -> str:
        """
        TODO: Define your tool function here
        
        This is where you implement the logic for your single tool.
        The tool should take input and return a string response.
        
        Examples of tools you could implement:
        - Calculator: Perform mathematical calculations
        - Search: Query external APIs or databases
        - Translator: Translate text between languages
        - Weather: Get weather information
        - File processor: Read/write files
        - Data analyzer: Process and analyze data
        """
        try:
            # TODO: Implement your tool logic here
            # Example: Simple calculator tool
            if not input_data or input_data.strip() == "":
                return "Error: No input provided to tool"
            
            # TODO: Add your tool's specific logic
            # Example: Simple echo tool (replace with your actual tool logic)
            result = f"Tool processed: {input_data}"
            
            # TODO: Add more sophisticated tool logic as needed
            # - Parse input parameters
            # - Call external APIs
            # - Process data
            # - Return formatted results
            
            return result
                
        except Exception as e:
            logger.error(f"Error in tool execution: {e}")
            return f"Tool error: {str(e)}"
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent with a single tool."""
        try:
            # Create agent with single tool
            self.agent = Agent(
                name=self.agent_name,
                description=self.agent_description,
                tools=[self.my_tool],  # TODO: Add your tool function here
                model=LiteLlm(model=self.model_name)
            )
            logger.info(f"Google ADK {self.agent_name} initialized successfully with tool")
            
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
                app_name='tool_app',  # TODO: Change to your app name
                user_id='user_tool'   # TODO: Change to your user ID
            )

            # Create content for the query
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            # Create runner
            runner = Runner(
                app_name='tool_app',  # TODO: Change to your app name
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
            # If no response from agent, provide fallback
            if not result_content:
                result_content = f"I can help you with my tool. Try asking me to use it with: '{query}'"
            
            return {
                "status": "completed",
                "content": result_content if result_content else "No response generated"
            }
            
        except Exception as e:
            logger.error(f"Error in agent with tool invoke: {e}")
            return {
                "status": "error",
                "content": f"Error processing request: {str(e)}"
            }

class AgentWithToolExecutor(AgentExecutor):
    """
    A2A SDK executor for the agent with tool.
    
    TODO: Update the executor name and any custom logic
    """
    
    def __init__(self):
        self.agent = AgentWithTool()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Execute the agent with tool request.
        
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
                name='tool_result',  # TODO: Change artifact name if needed
            )
            updater.complete()
        except Exception as e:
            logger.error(f'An error occurred while processing the agent with tool: {e}')
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
    id="tool_operation",  # TODO: Change to your skill ID
    name="Tool Operation",  # TODO: Change to your skill name
    description="An agent that can use a specific tool to perform tasks.",  # TODO: Update description
    tags=["tool", "operation", "task"],  # TODO: Update tags
    examples=[
        "Use the tool to calculate 2 + 2",
        "Process this data with the tool",
        "Help me with a calculation",
        "Run the tool on this input"
    ]  # TODO: Update examples based on your tool
)

def get_agent_card(host: str, port: int):
    """
    Create the agent card for A2A SDK registration.
    
    TODO: Update the agent card details
    """
    capabilities = AgentCapabilities(streaming=False, pushNotifications=False)
    return AgentCard(
        name="Agent with Tool",  # TODO: Change to your agent name
        description="An agent with a single tool for specific operations.",  # TODO: Update description
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
            agent_executor=AgentWithToolExecutor(),
            task_store=InMemoryTaskStore()),
        agent_card=get_agent_card(host, port)
    )
    uvicorn.run(app.build(), host=host, port=port) 