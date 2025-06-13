import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, cast
from openai import AzureOpenAI, OpenAI
import json
import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

class MCPClient:
    def __init__(self) -> None:
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._tools: Optional[List[Dict[str, Any]]] = None
        
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

    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send a request to the MCP server.
        
        Args:
            method: The method to call (e.g., "tools/list", "tools/call")
            params: Optional parameters for the method
            
        Returns:
            The response from the server
            
        Raises:
            Exception: If the request fails
        """
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_server first.")

        request = {
            "method": method,
            "params": params or {}
        }
        
        # Log the request being sent
        logger.info(f"Sending request to server: {json.dumps(request, indent=2)}")
        
        try:
            if method == "tools/list":
                response = await self.session.list_tools()
                return {"tools": [{"name": tool.name, "description": tool.description, "inputSchema": tool.inputSchema} for tool in response.tools]}
            elif method == "tools/call":
                if not params or "name" not in params or "arguments" not in params:
                    raise ValueError("Missing required parameters for tool call")
                result = await self.session.call_tool(params["name"], params["arguments"])
                return {"content": [{"type": "text", "text": result.content}]}
            else:
                raise ValueError(f"Unknown method: {method}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from the server.
        
        Returns:
            List of tool definitions
        """
        if self._tools is None:
            response = await self._send_request("tools/list")
            self._tools = response.get("tools", [])
        return self._tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool through the server.
        
        Args:
            name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            The tool's response
            
        Raises:
            Exception: If the tool call fails
        """
        # Log the incoming arguments
        logger.info(f"call_tool received arguments: {json.dumps(arguments, indent=2)}")
        
        # If arguments is a string, try to parse it as JSON
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
                logger.info(f"Parsed string arguments into: {json.dumps(arguments, indent=2)}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse arguments string: {e}")
                raise
        
        # Ensure arguments is a dictionary
        if not isinstance(arguments, dict):
            logger.error(f"Arguments must be a dictionary, got {type(arguments)}")
            raise TypeError("Arguments must be a dictionary")
        
        params = {
            "name": name,
            "arguments": arguments
        }
        
        # Log the actual parameters being sent
        logger.info(f"Sending parameters to server: {json.dumps(params, indent=2)}")
        
        response = await self._send_request("tools/call", params)
        
        # Extract text content from response
        if isinstance(response, dict):
            content = response.get("content", [])
            if content and isinstance(content, list):
                first_content = content[0]
                if isinstance(first_content, dict) and first_content.get("type") == "text":
                    return first_content.get("text")
        
        return response

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
                    model=os.getenv("OPENAI_MODEL", "gpt-4"),
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
                if message.content:
                    messages.append({"role": "assistant", "content": message.content})
                    final_text.append(message.content)

                # Check if there are any tool calls
                if message.tool_calls:
                    # Add the assistant's message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                            for tool_call in message.tool_calls
                        ]
                    })

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
                            model=os.getenv("OPENAI_MODEL", "gpt-4"),
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
        
        # Test get_data
        print("\nTesting get_data...")
        # Test case 1: Get all data for a specific client
        response = await client.process_query("Get all data for client1")
        print("\nClient1 data:")
        print(response)
        
        # Test case 2: Get data for a specific document and section
        response = await client.process_query("Get SOI data for doc1")
        print("\nDoc1 SOI data:")
        print(response)
        
        # Test case 3: Get all SOL data
        response = await client.process_query("Get all SOL data")
        print("\nAll SOL data:")
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