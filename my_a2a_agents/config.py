import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the A2A agents."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Google ADK Configuration
    GOOGLE_ADK_MODEL = os.getenv("GOOGLE_ADK_MODEL", "gemini-1.5-flash")
    
    # LiteLLM Configuration
    LITELLM_MODEL = os.getenv("LITELLM_MODEL", "openai/gpt-4o-mini")
    LITELLM_TEMPERATURE = float(os.getenv("LITELLM_TEMPERATURE", "0.1"))
    LITELLM_MAX_TOKENS = int(os.getenv("LITELLM_MAX_TOKENS", "1000"))
    
    # Agent Configuration
    AGENT_HOST = os.getenv("A2A_HOST", "127.0.0.1")
    AGENT_DATA_PORT = int(os.getenv("A2A_DATA_PORT", "9999"))
    AGENT_SOLVER_PORT = int(os.getenv("A2A_SOLVER_PORT", "9998"))
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        missing_configs = []
        
        if not cls.OPENAI_API_KEY:
            missing_configs.append("OPENAI_API_KEY")
        
        if not cls.GOOGLE_CLOUD_PROJECT:
            missing_configs.append("GOOGLE_CLOUD_PROJECT")
        
        if missing_configs:
            print(f"Warning: Missing configuration for: {', '.join(missing_configs)}")
            print("Some features may not work properly without these configurations.")
            return False
        
        return True
    
    @classmethod
    def get_litellm_config(cls):
        """Get LiteLLM configuration dictionary."""
        return {
            "model": cls.LITELLM_MODEL,
            "temperature": cls.LITELLM_TEMPERATURE,
            "max_tokens": cls.LITELLM_MAX_TOKENS,
            "api_key": cls.OPENAI_API_KEY
        }
    
    @classmethod
    def get_google_adk_config(cls):
        """Get Google ADK configuration dictionary."""
        return {
            "project": cls.GOOGLE_CLOUD_PROJECT,
            "model": cls.GOOGLE_ADK_MODEL
        } 