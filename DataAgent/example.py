"""Example usage of the DataAgent."""

import asyncio
from langchain_core.messages import HumanMessage
from .agent import graph

async def main():
    """Run an example conversation with the DataAgent."""
    # Create initial messages
    messages = [
        HumanMessage(content="Get the table from doc1 in the Financial Summary section")
    ]
    
    # Run the agent
    result = await graph.ainvoke(
        {"messages": messages},
        config={
            "model": "gpt-4",
            "azure_api_key": None,  # Will be loaded from environment
            "azure_api_version": "2024-02-15-preview",
            "azure_endpoint": None,  # Will be loaded from environment
            "openai_api_key": None,  # Will be loaded from environment
        }
    )
    
    # Print the result
    print("\nAgent Response:")
    for message in result["messages"]:
        print(f"\n{message.content}")

if __name__ == "__main__":
    asyncio.run(main()) 