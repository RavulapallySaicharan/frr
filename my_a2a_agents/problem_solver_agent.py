import asyncio
import os
import json
import re
from typing import Any, Dict, List, Optional
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message, new_task
from a2a.types import UnsupportedOperationError, InvalidParamsError, InternalError, TaskState, Part, TextPart
from a2a.utils.errors import ServerError
from a2a.server.tasks import TaskUpdater
import logging

# Google ADK and OpenAI imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types
from openai import OpenAI
from my_a2a_agents.config import Config

logger = logging.getLogger(__name__)

# Configure OpenAI client
client = OpenAI(api_key=Config().OPENAI_API_KEY)

class ProblemSolverAgent:
    """Advanced Problem Solver Agent using Google ADK with OpenAI models."""
    
    def __init__(self):
        self.config = Config()
        self.model_name = self.config.OPENAI_MODEL
        self.agent = None
        self._initialize_agent()
    
    def analyze_problem(self, problem_description: str, context: str) -> str:
        """Analyze a problem and break it down into components."""
        try:
            # Handle empty context
            if not context or context.strip() == "":
                context = "No additional context provided"
                
            analysis_prompt = f"""
            Problem: {problem_description}
            Context: {context}
            
            Please analyze this problem and provide:
            1. Problem type and category
            2. Key components and variables
            3. Potential challenges
            4. Required resources or data
            5. Success criteria
            """
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error analyzing problem: {e}")
            return f"Error: {str(e)}"
    
    def generate_solutions(self, problem: str, approach: str, constraints: str) -> str:
        """Generate multiple solution approaches for a problem."""
        try:
            # Handle empty constraints
            if not constraints or constraints.strip() == "":
                constraints = "No specific constraints"
                
            solution_prompt = f"""
            Problem: {problem}
            Approach: {approach}
            Constraints: {constraints}
            
            Generate 3-5 different solutions using the {approach} approach.
            For each solution, provide:
            1. Brief description
            2. Pros and cons
            3. Implementation complexity
            4. Expected outcomes
            """
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": solution_prompt}],
                temperature=0.3,
                max_tokens=1200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating solutions: {e}")
            return f"Error: {str(e)}"
    
    def evaluate_solution(self, solution: str, criteria: List[str]) -> str:
        """Evaluate the quality and feasibility of a solution."""
        try:
            if not criteria or len(criteria) == 0:
                criteria = ["efficiency", "cost", "feasibility", "scalability", "maintainability"]
            
            evaluation_prompt = f"""
            Solution: {solution}
            Evaluation Criteria: {', '.join(criteria)}
            
            Please evaluate this solution against each criterion:
            1. Rate each criterion (1-10 scale)
            2. Provide justification for each rating
            3. Overall assessment
            4. Recommendations for improvement
            """
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error evaluating solution: {e}")
            return f"Error: {str(e)}"
    
    def optimize_solution(self, current_solution: str, optimization_goal: str) -> str:
        """Optimize an existing solution."""
        try:
            optimization_prompt = f"""
            Current Solution: {current_solution}
            Optimization Goal: {optimization_goal}
            
            Please provide an optimized version of this solution that focuses on {optimization_goal}.
            Include:
            1. Changes made
            2. Expected improvements
            3. Trade-offs
            4. Implementation steps
            """
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": optimization_prompt}],
                temperature=0.2,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error optimizing solution: {e}")
            return f"Error: {str(e)}"
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent with problem-solving capabilities."""
        try:
            # Create agent with functions as tools
            self.agent = Agent(
                name="problem_solver_agent",
                description="Advanced problem-solving agent with multiple approaches",
                tools=[self.analyze_problem, self.generate_solutions, self.evaluate_solution, self.optimize_solution],
                model=LiteLlm(model=self.config.LITELLM_MODEL)
            )
            logger.info("Google ADK problem solver agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google ADK agent: {e}")
            raise e
    
    async def invoke(self, data: str, **kwargs) -> Dict[str, Any]:
        """Process problem-solving queries using Google ADK agent with Runner pattern."""
        try:
            if not data or data.strip() == "":
                return {
                    "status": "error",
                    "content": "No problem description provided"
                }
            
            if not self.agent:
                raise Exception("Google ADK agent not initialized")
            
            # Initialize session and artifact services
            session_service = InMemorySessionService()
            artifacts_service = InMemoryArtifactService()
            
            # Create session
            session = await session_service.create_session(
                state={}, 
                app_name='problem_solver_app', 
                user_id='user_problem'
            )
            
            # Create content for the query
            content = types.Content(role='user', parts=[types.Part(text=data)])
            
            # Create runner
            runner = Runner(
                app_name='problem_solver_app',
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
            logger.error(f"Error in problem solver agent invoke: {e}")
            return {
                "status": "error",
                "content": f"Error processing request: {str(e)}"
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
            updater.add_artifact(
                [Part(root=TextPart(text=result['content']))],
                name='solution_result',
            )
            updater.complete()
        except Exception as e:
            logger.error(f'An error occurred while processing the problem solver agent: {e}')
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())

# Enhanced agent skill and card definition
skill = AgentSkill(
    id="solve_problem",
    name="Advanced Problem Solver",
    description="Analyzes complex problems and generates multiple solution approaches using AI-powered reasoning.",
    tags=["problem", "solution", "analysis", "optimization", "algorithm"],
    examples=[
        "Analyze this optimization problem",
        "Generate solutions for this algorithm challenge",
        "Evaluate the quality of this solution approach",
        "Optimize this solution for better efficiency"
    ]
)

def get_agent_card(host: str, port: int):
    capabilities = AgentCapabilities(streaming=False, pushNotifications=False)
    return AgentCard(
        name="Advanced Problem Solver Agent",
        description="AI-powered problem-solving agent using Google ADK and OpenAI models via LiteLLM with multiple solution approaches.",
        url=f"http://{host}:{port}/",
        version="2.0.0",
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        capabilities=capabilities,
        skills=[skill]
    ) 