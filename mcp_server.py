from typing import Dict, List, Optional, TypedDict
from enum import Enum
import sqlite3
import json
import logging
from datetime import datetime
import requests
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

# Initialize FastMCP server
mcp = FastMCP("frr_mcp")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
def init_db():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect('frr_mcp.db')
    c = conn.cursor()
    
    # Create documents table
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            client_id TEXT,
            upload_date TIMESTAMP,
            metadata TEXT,
            status TEXT
        )
    ''')
    
    # Create parsed_sections table
    c.execute('''
        CREATE TABLE IF NOT EXISTS parsed_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT,
            section_name TEXT,
            content TEXT,
            content_type TEXT,
            FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
        )
    ''')
    
    # Create prompts table for caching
    c.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            section TEXT PRIMARY KEY,
            prompt_text TEXT,
            last_updated TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on module load
init_db()

# Dummy data for testing
DUMMY_DOCUMENTS = {
    "doc1": {
        "client_id": "client1",
        "metadata": {"title": "Financial Report 2023", "pages": 10},
        "sections": {
            "Financial Summary": {
                "type": "table",
                "content": [["Revenue", "2023", "2022"], ["100M", "80M"]]
            },
            "Executive Summary": {
                "type": "text",
                "content": "This report presents the financial performance..."
            }
        }
    }
}

class PromptHub:
    """Mock Prompt Hub for demonstration."""
    def __init__(self, base_url: str = "http://prompt-hub.example.com"):
        self.base_url = base_url
        self.cache = {}
    
    def get_prompt(self, section: str) -> str:
        """Get prompt for a section, with caching."""
        # Check cache first
        if section in self.cache:
            return self.cache[section]
        
        # Mock API call
        # In real implementation, this would be:
        # response = requests.get(f"{self.base_url}/prompts/{section}")
        # return response.json()["prompt"]
        
        # Dummy prompts for testing
        prompts = {
            "Financial Summary": "Extract all financial metrics and their values",
            "Executive Summary": "Summarize the key points and recommendations",
            "default": "Extract all relevant information from this section"
        }
        
        prompt = prompts.get(section, prompts["default"])
        self.cache[section] = prompt
        return prompt

# Initialize Prompt Hub
prompt_hub = PromptHub()

@mcp.tool()
async def get_table(
    doc_id: str,
    section: Optional[str] = None
) -> Dict:
    """Extract tabular sections from the parsed PDF content.
    
    Args:
        doc_id: Document identifier
        section: Optional section name to filter by
    
    Returns:
        Dictionary containing the extracted table data
    """
    logger.info(f"Getting table for doc_id: {doc_id}, section: {section}")
    
    # In real implementation, this would query the database
    # For now, use dummy data
    if doc_id not in DUMMY_DOCUMENTS:
        raise ValueError(f"Document {doc_id} not found")
    
    doc = DUMMY_DOCUMENTS[doc_id]
    sections = doc["sections"]
    
    if section:
        if section not in sections:
            raise ValueError(f"Section {section} not found in document {doc_id}")
        if sections[section]["type"] != "table":
            raise ValueError(f"Section {section} is not a table")
        return {"table": sections[section]["content"]}
    
    # Return all tables if no section specified
    tables = {
        name: data["content"]
        for name, data in sections.items()
        if data["type"] == "table"
    }
    return {"tables": tables}

@mcp.tool()
async def get_prompt(section: str) -> str:
    """Fetch extraction prompt for the given section.
    
    Args:
        section: Section name to get prompt for
    
    Returns:
        The prompt text for the section
    """
    logger.info(f"Getting prompt for section: {section}")
    return prompt_hub.get_prompt(section)

@mcp.tool()
async def get_semantic_search(
    doc_id: str,
    section: Optional[str] = None,
    top_k: int = 5,
    retriever: str = "default"
) -> Dict:
    """Perform semantic similarity search on document content.
    
    Args:
        doc_id: Document identifier
        section: Optional section name to filter by
        top_k: Number of top results to return
        retriever: Retriever type to use
    
    Returns:
        Dictionary containing the top k matching passages
    """
    logger.info(f"Performing semantic search for doc_id: {doc_id}, section: {section}")
    
    # In real implementation, this would use a proper semantic search engine
    # For now, return dummy results
    if doc_id not in DUMMY_DOCUMENTS:
        raise ValueError(f"Document {doc_id} not found")
    
    doc = DUMMY_DOCUMENTS[doc_id]
    sections = doc["sections"]
    
    if section:
        if section not in sections:
            raise ValueError(f"Section {section} not found in document {doc_id}")
        content = sections[section]["content"]
        return {
            "passages": [content[:100] + "..."] * top_k,
            "scores": [0.9] * top_k
        }
    
    # Return results from all sections if no section specified
    all_passages = []
    for name, data in sections.items():
        if isinstance(data["content"], str):
            all_passages.append(data["content"][:100] + "...")
    
    return {
        "passages": all_passages[:top_k],
        "scores": [0.9] * min(top_k, len(all_passages))
    }

def main():
    """Entry point for the FRR MCP server."""
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    init_db()
    
    # Start MCP server
    logger.info("Starting FRR MCP server")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main() 