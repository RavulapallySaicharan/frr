"""DataAgent implementation using LangGraph."""

from datetime import datetime, timezone
from typing import Dict, List, Literal, cast
import asyncio
from openai import AzureOpenAI, OpenAI
import os

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from .configuration import Configuration
from .state import InputState, State
from .tools import TOOLS, initialize_tools

# Initialize MCP tools when module is loaded
config = Configuration()
asyncio.run(initialize_tools())

async def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our agent.

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = Configuration.from_runnable_config(config)

    # Try Azure OpenAI first
    try:
        client = AzureOpenAI(
            api_key=configuration.azure_api_key,
            api_version=configuration.azure_api_version,
            azure_endpoint=configuration.azure_endpoint
        )
        model = configuration.model
    except Exception:
        # Fallback to regular OpenAI
        client = OpenAI(api_key=configuration.openai_api_key)
        model = "gpt-4"

    # Format the system prompt
    system_message = configuration.system_prompt.format(
        system_time=datetime.now(tz=timezone.utc).isoformat()
    )

    # Get the model's response
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_message}, *state.messages],
        tools=[{"type": "function", "function": tool.schema()} for tool in TOOLS],
        tool_choice="auto"
    )

    # Convert response to AIMessage
    message = response.choices[0].message
    ai_message = AIMessage(
        content=message.content,
        tool_calls=message.tool_calls
    )

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and ai_message.tool_calls:
        return {
            "messages": [
                AIMessage(
                    content="Sorry, I could not find an answer to your question in the specified number of steps."
                )
            ]
        }

    # Return the model's response
    return {"messages": [ai_message]}

# Define the graph
builder = StateGraph(State, input=InputState, config_schema=Configuration)

# Define the nodes
builder.add_node(call_model)
builder.add_node("tools", ToolNode(TOOLS))

# Set the entrypoint
builder.add_edge("__start__", "call_model")

def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    # Otherwise we execute the requested actions
    return "tools"

# Add conditional edges
builder.add_conditional_edges(
    "call_model",
    route_model_output,
)

# Add edge from tools back to model
builder.add_edge("tools", "call_model")

# Compile the graph
graph = builder.compile(
    interrupt_before=[],
    interrupt_after=[],
)
graph.name = "DataAgent"  # Customize the name in LangSmith 