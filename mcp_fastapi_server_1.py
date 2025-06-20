from typing import Dict, List, Optional, TypedDict
from enum import Enum
import sqlite3
import json
import logging
from datetime import datetime
import requests
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import os
from dotenv import load_dotenv
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Your API app
api_app = FastAPI(title="FRR API", description="Financial Report Reader API")

# A separate app for the MCP server
mcp_app = FastAPI()

# Create MCP server from the API app
mcp = FastApiMCP(api_app)

# Mount the MCP server to the separate app
mcp.mount(mcp_app)

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

# API Endpoints
@api_app.get("/")
async def root():
    """Root endpoint for the FRR API."""
    return {"message": "Financial Report Reader API is running"}

@api_app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@api_app.get("/documents")
async def list_documents():
    """List all available documents."""
    return {"documents": list(DUMMY_DOCUMENTS.keys())}

@api_app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get document metadata by ID."""
    if doc_id not in DUMMY_DOCUMENTS:
        raise ValueError(f"Document {doc_id} not found")
    return {"document": DUMMY_DOCUMENTS[doc_id]}

@api_app.get("/documents/{doc_id}/tables")
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

@api_app.get("/prompts/{section}")
async def get_prompt(section: str) -> str:
    """Fetch extraction prompt for the given section.
    
    Args:
        section: Section name to get prompt for
    
    Returns:
        The prompt text for the section
    """
    logger.info(f"Getting prompt for section: {section}")
    return {"section": section, "prompt": prompt_hub.get_prompt(section)}

def main():
    """Entry point for the FRR FastAPI server."""
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    init_db()
    
    # Start FastAPI server with uvicorn
    import uvicorn
    logger.info("Starting FRR FastAPI server on port 8001")
    uvicorn.run(api_app, host="0.0.0.0", port=8001)
    logger.info("Starting FRR FastAPI MCP server on port 8000")
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 