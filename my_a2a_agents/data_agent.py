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
        self.csv_file_path = "sample_soi_data.csv"
        self._initialize_agent()
    
    def process_data(self, query: str) -> str:
        """Process data based on user query."""
        try:
            # Check if CSV file exists
            if not os.path.exists(self.csv_file_path):
                return f"Error: SOI data file '{self.csv_file_path}' not found"
            
            # Read the SOI CSV data
            df = pd.read_csv(self.csv_file_path)
            
            # Process the query
            query_lower = query.lower()
            
            if "total portfolio value" in query_lower or "total value" in query_lower:
                total_invested = df['amount_invested'].sum()
                total_current = df['current_value'].sum()
                total_return = ((total_current - total_invested) / total_invested) * 100
                return f"Portfolio Summary:\nTotal Invested: ${total_invested:,.2f}\nTotal Current Value: ${total_current:,.2f}\nTotal Return: {total_return:.2f}%"
            
            elif "average return" in query_lower:
                avg_return = df['return_percentage'].mean()
                return f"Average Return Percentage: {avg_return:.2f}%"
            
            elif "return percentage" in query_lower and "greater" in query_lower:
                # Extract the percentage value from query
                import re
                match = re.search(r'(\d+)%', query)
                if match:
                    threshold = float(match.group(1))
                    filtered_df = df[df['return_percentage'] > threshold]
                    return f"Investments with return > {threshold}%:\n{filtered_df.to_string(index=False)}"
                else:
                    return "Please specify the percentage threshold (e.g., 'greater than 10%')"
            
            elif "sector" in query_lower and "group" in query_lower:
                sector_summary = df.groupby('sector')['amount_invested'].sum().sort_values(ascending=False)
                return f"Total Investment by Sector:\n{sector_summary.to_string()}"
            
            elif "top" in query_lower and "return" in query_lower:
                # Extract number from query (e.g., "top 5")
                import re
                match = re.search(r'top (\d+)', query_lower)
                if match:
                    n = int(match.group(1))
                    top_investments = df.nlargest(n, 'return_percentage')[['company_name', 'sector', 'return_percentage', 'amount_invested', 'current_value']]
                    return f"Top {n} Investments by Return:\n{top_investments.to_string(index=False)}"
                else:
                    return "Please specify the number (e.g., 'top 5')"
            
            elif "correlation" in query_lower:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 1:
                    corr = df[numeric_cols].corr()
                    return f"Correlation Matrix:\n{corr.to_string()}"
                else:
                    return "Not enough numeric columns for correlation analysis"
            
            elif "statistics" in query_lower or "summary" in query_lower:
                summary = df.describe()
                return f"SOI Data Statistics:\n{summary.to_string()}"
            
            elif "filter" in query_lower:
                # Handle filtering by sector
                if "sector" in query_lower:
                    sectors = ['Technology', 'Healthcare', 'Energy', 'Financial Services', 'Consumer']
                    for sector in sectors:
                        if sector.lower() in query_lower:
                            filtered_df = df[df['sector'] == sector]
                            return f"Investments in {sector} sector:\n{filtered_df.to_string(index=False)}"
                
                # Handle filtering by investment type
                elif "investment type" in query_lower or "type" in query_lower:
                    types = ['Equity', 'Venture Capital', 'Private Equity', 'Series A', 'Series B', 'Series C']
                    for inv_type in types:
                        if inv_type.lower() in query_lower:
                            filtered_df = df[df['investment_type'] == inv_type]
                            return f"Investments of type {inv_type}:\n{filtered_df.to_string(index=False)}"
                
                return "Please specify filter criteria (sector, investment type, etc.)"
            
            else:
                # Default: show all data
                return f"Portfolio Data:\n{df.to_string(index=False)}"
                
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return f"Error: {str(e)}"
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent with data processing capabilities."""
        try:
            # Create agent with single tool
            self.agent = Agent(
                name="data_agent",
                description="Advanced data processing and analysis agent",
                tools=[self.process_data],
                model=LiteLlm(model=self.model_name)
            )
            logger.info("Google ADK data agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google ADK agent: {e}")
            raise e
    
    async def invoke(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process SOI data queries using Google ADK agent with Runner pattern."""
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
            
            # Create session
            session = await session_service.create_session(
                state={}, 
                app_name='data_app', 
                user_id='user_data'
            )

            # Create content for the query
            content = types.Content(role='user', parts=[types.Part(text=query)])
            
            # Create runner
            runner = Runner(
                app_name='data_app',
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

