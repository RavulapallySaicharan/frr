"""Configuration for the DataAgent."""

from typing import Optional
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

class Configuration(BaseModel):
    """Configuration for the DataAgent."""
    
    # Model configuration
    model: str = Field(
        default=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
        description="The model to use for inference"
    )
    
    # Azure OpenAI configuration
    azure_api_key: Optional[str] = Field(
        default=os.getenv("AZURE_OPENAI_API_KEY"),
        description="Azure OpenAI API key"
    )
    azure_api_version: str = Field(
        default=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        description="Azure OpenAI API version"
    )
    azure_endpoint: Optional[str] = Field(
        default=os.getenv("AZURE_OPENAI_ENDPOINT"),
        description="Azure OpenAI endpoint"
    )
    
    # OpenAI configuration (fallback)
    openai_api_key: Optional[str] = Field(
        default=os.getenv("OPENAI_API_KEY"),
        description="OpenAI API key"
    )
    
    # System prompt
    system_prompt: str = Field(
        default="""You are a helpful AI assistant that can analyze financial data and documents.
You have access to various tools to help you:
1. get_table: Extract tables from documents
2. get_prompt: Get prompts for specific sections
3. get_semantic_search: Search through document content
4. get_data: Get data for specific clients or documents

Current time: {system_time}

Use these tools to help answer questions about financial data and documents.
Always explain your reasoning and show your work.""",
        description="System prompt for the agent"
    )
    
    @classmethod
    def from_runnable_config(cls, config: dict) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        return cls(**config) 