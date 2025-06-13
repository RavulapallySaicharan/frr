import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, cast
from openai import AzureOpenAI, OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    def __init__(self) -> None:
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Try Azure OpenAI first
        try:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            self.is_azure = True
        except Exception:
            # Fallback to regular OpenAI
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.is_azure = False
            
        self.stdio = None
        self.write = None

    async def connect_to_server(self, server_script_path: str) -> None:
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        if self.session:
            await self.session.initialize()

            # List available tools
            response = await self.session.list_tools()
            tools = response.tools
            print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Azure OpenAI and available tools

        Args:
            query: The user's query to process

        Returns:
            The formatted response from Azure OpenAI and tool calls
        """
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_server first.")

        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                }
            }
            for tool in response.tools
        ]

        try:
            # Initial API call
            if self.is_azure:
                response = self.client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=messages,
                    tools=available_tools,
                    tool_choice="auto"
                )
            else:
                response = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    messages=messages,
                    tools=available_tools,
                    tool_choice="auto"
                )

            # Process response and handle tool calls
            tool_results = []
            final_text = []

            while True:
                message = response.choices[0].message
                
                # Add assistant's message to the conversation
                messages.append({"role": "assistant", "content": message.content or ""})
                
                if message.content:
                    final_text.append(message.content)

                # Check if there are any tool calls
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        # Execute tool call
                        result = await self.session.call_tool(tool_name, tool_args)
                        tool_results.append({"call": tool_name, "result": result})
                        final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                        # Add tool response to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result.content
                        })

                    # Get next response
                    if self.is_azure:
                        response = self.client.chat.completions.create(
                            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                            messages=messages,
                            tools=available_tools,
                            tool_choice="auto"
                        )
                    else:
                        response = self.client.chat.completions.create(
                            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                            messages=messages,
                            tools=available_tools,
                            tool_choice="auto"
                        )
                else:
                    break

            return "\n".join(final_text)
            
        except Exception as e:
            if self.is_azure:
                print("Azure OpenAI failed, switching to regular OpenAI...")
                self.client = OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                self.is_azure = False
                return await self.process_query(query)  # Retry with regular OpenAI
            else:
                raise e  # If regular OpenAI also fails, raise the error

    async def chat_loop(self) -> None:
        """Run an interactive chat loop"""
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_server first.")

        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources"""
        await self.exit_stack.aclose()


async def test_frr_mcp_tools():
    """Test the FRR MCP server tools."""
    client = MCPClient()
    
    try:
        # Connect to the FRR MCP server
        await client.connect_to_server("mcp_server.py")
        
        # Test get_table
        print("\nTesting get_table...")
        response = await client.process_query("Get the table from doc1 in the Financial Summary section")
        print(response)
        
        # Test get_prompt
        print("\nTesting get_prompt...")
        response = await client.process_query("Get the prompt for the Financial Summary section")
        print(response)
        
        # Test get_semantic_search
        print("\nTesting get_semantic_search...")
        response = await client.process_query("Search for financial performance in doc1")
        print(response)
        
        # Test error handling
        print("\nTesting error handling...")
        response = await client.process_query("Get the table from non_existent_doc")
        print(response)
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
    finally:
        await client.cleanup()

async def interactive_mode():
    """Run the client in interactive mode."""
    client = MCPClient()
    
    try:
        # Connect to the FRR MCP server
        await client.connect_to_server("mcp_server.py")
        
        # Run the chat loop
        await client.chat_loop()
        
    except Exception as e:
        print(f"Error during interactive mode: {str(e)}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='FRR MCP Client')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_frr_mcp_tools())
    else:
        asyncio.run(interactive_mode()) 