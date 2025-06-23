from typing import Dict, List, Optional, TypedDict
from enum import Enum
import sqlite3
import json
import logging
from datetime import datetime
import requests
from fastmcp import FastMCP
import os
from dotenv import load_dotenv
import pandas as pd

# Initialize FastMCP server
mcp = FastMCP("frr_mcp_2")

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

@mcp.tool()
async def get_data(
    client_id: Optional[str] = None,
    document_id: Optional[str] = None,
    section: Optional[str] = None
) -> Dict:
    """Get data from the sample CSV file based on filters.
    
    Args:
        client_id: Optional client identifier to filter by
        document_id: Optional document identifier to filter by
        section: Optional section name to filter by (e.g., SOI, SOL)
    
    Returns:
        Dictionary containing the filtered data
    """
    logger.info(f"Getting data for client: {client_id}, document: {document_id}, section: {section}")
    
    try:
        # Read the CSV file
        df = pd.read_csv('sample_data.csv')
        
        # Apply filters if provided
        if client_id:
            df = df[df['client'] == client_id]
        if document_id:
            df = df[df['document'] == document_id]
        if section:
            df = df[df['section'] == section]
        
        # Convert to dictionary format
        result = df.to_dict(orient='records')
        
        return {
            "data": result,
            "count": len(result)
        }
    except Exception as e:
        logger.error(f"Error reading data: {str(e)}")
        raise ValueError(f"Error reading data: {str(e)}")

def main():
    """Entry point for the FRR MCP server 2."""
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    init_db()
    
    # Start MCP server with streamable-http transport on port 8002
    logger.info("Starting FRR MCP server 2 on port 8002")
    mcp.run(transport='streamable-http', port=8002, host='0.0.0.0')

if __name__ == "__main__":
    main() 