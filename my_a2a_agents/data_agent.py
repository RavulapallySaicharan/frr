import asyncio
import os
import json
import pandas as pd
from typing import Any, Dict, List, Optional
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message, new_task
from a2a.types import UnsupportedOperationError, InvalidParamsError, InternalError, TaskState, Part, TextPart
from a2a.utils.errors import ServerError
from a2a.server.tasks import TaskUpdater
import logging

# Google ADK and LiteLLM imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types
# import litellm
from my_a2a_agents.config import Config

logger = logging.getLogger(__name__)

# Configure LiteLLM for OpenAI
# litellm.set_verbose = False

class DataAgent:
    """Advanced Data Agent using Google ADK with OpenAI models."""
    
    def __init__(self):
        self.config = Config()
        self.model_name = self.config.LITELLM_MODEL
        self.agent = None
        self._initialize_agent()
    
    def fetch_csv_data(self, data_source: str, columns: List[str], rows: int) -> str:
        """Fetch or generate CSV data."""
        try:
            if data_source == "sample":
                # Generate sample data
                if not columns or len(columns) == 0:
                    columns = ["id", "name", "value", "category"]
                
                import random
                categories = ["A", "B", "C", "D"]
                names = ["Item_" + str(i) for i in range(1, rows + 1)]
                
                data = []
                for i in range(rows):
                    data.append([
                        i + 1,
                        names[i],
                        round(random.uniform(10, 100), 2),
                        random.choice(categories)
                    ])
                
                df = pd.DataFrame(data, columns=columns)
                return df.to_csv(index=False)
            
            elif os.path.exists(data_source):
                # Read from file
                df = pd.read_csv(data_source)
                return df.to_csv(index=False)
            
            else:
                return "Error: Data source not found"
                
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return f"Error: {str(e)}"
    
    def analyze_data(self, data: str, analysis_type: str) -> str:
        """Analyze CSV data and provide insights."""
        try:
            df = pd.read_csv(pd.StringIO(data))
            
            if analysis_type == "summary":
                summary = df.describe()
                return f"Data Summary:\n{summary.to_string()}"
            
            elif analysis_type == "statistics":
                stats = {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict(),
                    "missing_values": df.isnull().sum().to_dict()
                }
                return f"Data Statistics:\n{json.dumps(stats, indent=2)}"
            
            elif analysis_type == "correlation":
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 1:
                    corr = df[numeric_cols].corr()
                    return f"Correlation Matrix:\n{corr.to_string()}"
                else:
                    return "Not enough numeric columns for correlation analysis"
            
            elif analysis_type == "trends":
                # Simple trend analysis
                numeric_cols = df.select_dtypes(include=['number']).columns
                trends = {}
                for col in numeric_cols:
                    if len(df[col].dropna()) > 1:
                        trend = "increasing" if df[col].iloc[-1] > df[col].iloc[0] else "decreasing"
                        trends[col] = trend
                
                return f"Trend Analysis:\n{json.dumps(trends, indent=2)}"
            
            else:
                return "Unknown analysis type"
                
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            return f"Error: {str(e)}"
    
    def filter_data(self, data: str, column: str, condition: str) -> str:
        """Filter CSV data based on criteria."""
        try:
            df = pd.read_csv(pd.StringIO(data))
            
            if column not in df.columns:
                return f"Error: Column '{column}' not found in data"
            
            # Simple filtering logic
            if ">" in condition:
                value = float(condition.split(">")[1].strip())
                filtered_df = df[df[column] > value]
            elif "<" in condition:
                value = float(condition.split("<")[1].strip())
                filtered_df = df[df[column] < value]
            elif "==" in condition:
                value = condition.split("==")[1].strip().strip('"')
                filtered_df = df[df[column] == value]
            else:
                return f"Error: Unsupported condition '{condition}'"
            
            return filtered_df.to_csv(index=False)
            
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            return f"Error: {str(e)}"
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent with data processing capabilities."""
        try:
            # Create agent with functions as tools
            self.agent = Agent(
                name="data_agent",
                description="Advanced data processing and analysis agent",
                tools=[self.fetch_csv_data, self.analyze_data, self.filter_data],
                model=LiteLlm(model=self.model_name)
            )
            logger.info("Google ADK agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google ADK agent: {e}")
            raise e
    
    async def invoke(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process data-related queries using Google ADK agent with Runner pattern."""
        try:
            if not query or query.strip() == "":
                return {
                    "status": "error",
                    "content": "No query provided"
                }
            
            if not self.agent:
                raise Exception("Google ADK agent not initialized")
            
            # Initialize session and artifact services
            session_service = InMemorySessionService()
            artifacts_service = InMemoryArtifactService()

            print(f"Session service: {session_service}")
            print(f"Artifacts service: {artifacts_service}")
            
            # Create session
            session = await session_service.create_session(
                state={}, 
                app_name='data_agent_app', 
                user_id='user_data'
            )
            
            print(f"Session: {session}")

            # Create content for the query
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            # Create runner
            runner = Runner(
                app_name='data_agent_app',
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
            
            print({
                "status": "completed",
                "content": result_content if result_content else "No response generated"
            })
            
            return {
                "status": "completed",
                "content": result_content if result_content else "No response generated"
            }
            
        except Exception as e:
            logger.error(f"Error in data agent invoke: {e}")
            return {
                "status": "error",
                "content": f"Error processing request: {str(e)}"
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
            updater.add_artifact(
                [Part(root=TextPart(text=result['content']))],
                name='data_result',
            )
            updater.complete()
        except Exception as e:
            logger.error(f'An error occurred while processing the data agent: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())

# Enhanced agent skill and card definition
skill = AgentSkill(
    id="get_data",
    name="Advanced Data Processor",
    description="Fetches, analyzes, and processes tabular data using AI-powered insights.",
    tags=["data", "table", "analysis", "csv", "insights"],
    examples=[
        "Get sample data table",
        "Analyze this CSV data for trends",
        "Filter data where value > 50",
        "Generate correlation analysis"
    ]
)

def get_agent_card(host: str, port: int):
    capabilities = AgentCapabilities(streaming=False, pushNotifications=False)
    return AgentCard(
        name="Advanced Data Agent",
        description="AI-powered data processing and analysis agent using Google ADK and OpenAI models via LiteLLM.",
        url=f"http://{host}:{port}/",
        version="2.0.0",
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        capabilities=capabilities,
        skills=[skill]
    ) 

