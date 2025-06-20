"""Tools for the DataAgent."""

from typing import Dict, List, Optional, Any
from langchain_core.tools import BaseTool
import asyncio
from mcp_client import MCPClient

# Initialize MCP client
client = MCPClient()

async def initialize_tools():
    """Initialize the MCP client and tools."""
    await client.connect_to_server("mcp_server.py")

# Define the tools
class GetTableTool(BaseTool):
    name = "get_table"
    description = "Extract tabular sections from the parsed PDF content"
    
    async def _arun(self, doc_id: str, section: Optional[str] = None) -> Dict:
        """Run the tool asynchronously."""
        return await client.call_tool("get_table", {"doc_id": doc_id, "section": section})
    
    def _run(self, doc_id: str, section: Optional[str] = None) -> Dict:
        """Run the tool synchronously."""
        return asyncio.run(self._arun(doc_id, section))

class GetPromptTool(BaseTool):
    name = "get_prompt"
    description = "Fetch extraction prompt for the given section"
    
    async def _arun(self, section: str) -> str:
        """Run the tool asynchronously."""
        return await client.call_tool("get_prompt", {"section": section})
    
    def _run(self, section: str) -> str:
        """Run the tool synchronously."""
        return asyncio.run(self._arun(section))

class GetSemanticSearchTool(BaseTool):
    name = "get_semantic_search"
    description = "Perform semantic similarity search on document content"
    
    async def _arun(
        self,
        doc_id: str,
        section: Optional[str] = None,
        top_k: int = 5,
        retriever: str = "default"
    ) -> Dict:
        """Run the tool asynchronously."""
        return await client.call_tool(
            "get_semantic_search",
            {
                "doc_id": doc_id,
                "section": section,
                "top_k": top_k,
                "retriever": retriever
            }
        )
    
    def _run(
        self,
        doc_id: str,
        section: Optional[str] = None,
        top_k: int = 5,
        retriever: str = "default"
    ) -> Dict:
        """Run the tool synchronously."""
        return asyncio.run(self._arun(doc_id, section, top_k, retriever))

class GetDataTool(BaseTool):
    name = "get_data"
    description = "Get data from the sample CSV file based on filters"
    
    async def _arun(
        self,
        client_id: Optional[str] = None,
        document_id: Optional[str] = None,
        section: Optional[str] = None
    ) -> Dict:
        """Run the tool asynchronously."""
        return await client.call_tool(
            "get_data",
            {
                "client_id": client_id,
                "document_id": document_id,
                "section": section
            }
        )
    
    def _run(
        self,
        client_id: Optional[str] = None,
        document_id: Optional[str] = None,
        section: Optional[str] = None
    ) -> Dict:
        """Run the tool synchronously."""
        return asyncio.run(self._arun(client_id, document_id, section))

# List of available tools
TOOLS = [
    GetTableTool(),
    GetPromptTool(),
    GetSemanticSearchTool(),
    GetDataTool()
] 