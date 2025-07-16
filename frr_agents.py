from fastapi import FastAPI
from pydantic import BaseModel, RootModel
from typing import Optional, Dict, Any, Literal, Field
import pandas as pd
import uvicorn

from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from prompts import DATA_AGENT_PROMPT, PROBLEM_SOLVER_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class SupervisorState(AgentState):
    document_id: str
    document_version: str
    data: Optional[dict] = None
    solution: Optional[str] = None
    next_step: Optional[str] = None
    structured_response: Optional[dict] = None

class CheckOutputResponse(BaseModel):
    check_status: Literal["pass", "fail"] = Field(...)
    details: str = Field(...,
                         description="Details about the check status")

app = FastAPI()

# Pydantic model matching SupervisorState
class SupervisorStateInput(RootModel[Dict[str, Any]]):
    pass

# implement a tool with dummy data to get the selection data for a document
@tool
def get_selection_data_for_document(document_id: str, document_version: str) -> dict:
    """
    Get the selection data for a document
    """
    print(f"Getting selection data for document {document_id} and version {document_version}")
    # return a dummy SOI data in tabular format
    return {"data": pd.DataFrame({
        "column1": [1, 2, 3],
        "column2": [4, 5, 6]
    })}

def create_data_agent():
    return create_react_agent(
        model=llm,
        tools=[get_selection_data_for_document],
        prompt=DATA_AGENT_PROMPT,
        state_schema=SupervisorState
    )

def create_problem_solver():
    return create_react_agent(
        model=llm,
        tools=[],
        prompt=PROBLEM_SOLVER_PROMPT,
        response_format=CheckOutputResponse
    )

# Initialize agents
data_agent = create_data_agent()
problem_solver_agent = create_problem_solver()




@app.post("/run-data-agent")
def run_data_agent(state_input: SupervisorStateInput):
    try:
        print("\n\n-------------State Input -------------")
        print(f"State: {state_input}")
        state = SupervisorState(**state_input.dict())
        print("\n--- Data Agent State ---")
        print("Current messages:", state.messages)
        response = data_agent.invoke({
            "messages": state.messages,
            "document_id": state.document_id,
            "document_version": state.document_version
        })
        print("Data gathered:", response['content'][:100])
        return {
            "data": response['content'],
            "next_step": "supervisor"
        }
    except Exception as e:
        print(f"Error in data agent: {e}")
        return {
            "error": str(e)
        }

@app.post("/run-problem-solver")
def run_problem_solver(state_input: SupervisorStateInput):
    try:
        state = SupervisorState(**state_input.dict())
        print("\n\n-------------State Input -------------")
        print(f"State: {state}")
        print("\n--- Problem Solver State ---")
        print("Current messages:", state.messages)
        response = problem_solver_agent.invoke({
            "messages": state.messages,
            "data": state.data.get("content", "")[:100]
        })
        print("Solution provided:", response['content'][:100])
        return {
            "solution": response['content'],
            "next_step": "supervisor"
        }
    except Exception as e:
        print(f"Error in problem solver: {e}")
        return {
            "error": str(e)
        }



if __name__ == "__main__":
    uvicorn.run(app, port=8000)