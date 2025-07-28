#!/usr/bin/env python3
"""
Setup script for A2A Agents with Google ADK and LiteLLM
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables."""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / "env_example.txt"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created. Please edit it with your API keys.")
        print("   Required: OPENAI_API_KEY, GOOGLE_CLOUD_PROJECT")
    else:
        print("✅ .env file already exists")

def validate_config():
    """Validate the configuration."""
    print("\n🔍 Validating configuration...")
    
    try:
        from config import Config
        config = Config()
        
        missing = []
        if not config.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not config.GOOGLE_CLOUD_PROJECT:
            missing.append("GOOGLE_CLOUD_PROJECT")
        
        if missing:
            print(f"⚠️  Missing configuration: {', '.join(missing)}")
            print("   Some features may not work properly")
            return False
        else:
            print("✅ Configuration is complete")
            return True
            
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False

def test_agents():
    """Test the agents."""
    print("\n🧪 Testing agents...")
    
    try:
        # Test data agent
        from data_agent import DataAgent
        data_agent = DataAgent()
        print("✅ Data Agent initialized successfully")
        
        # Test problem solver agent
        from problem_solver_agent import ProblemSolverAgent
        solver_agent = ProblemSolverAgent()
        print("✅ Problem Solver Agent initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 A2A Agents Setup with Google ADK and LiteLLM")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Validate configuration
    config_valid = validate_config()
    
    # Test agents
    agents_working = test_agents()
    
    print("\n" + "=" * 50)
    print("📋 Setup Summary:")
    print(f"   Dependencies: ✅ Installed")
    print(f"   Environment: ✅ Configured")
    print(f"   Configuration: {'✅ Valid' if config_valid else '⚠️  Incomplete'}")
    print(f"   Agents: {'✅ Working' if agents_working else '❌ Failed'}")
    
    if config_valid and agents_working:
        print("\n🎉 Setup completed successfully!")
        print("\n📖 Next steps:")
        print("   1. Edit .env file with your API keys")
        print("   2. Run: export A2A_AGENT_TYPE=data && python -m my_a2a_agents")
        print("   3. Or run: export A2A_AGENT_TYPE=solver && python -m my_a2a_agents")
    else:
        print("\n⚠️  Setup completed with warnings.")
        print("   Please check the configuration and try again.")

if __name__ == "__main__":
    main() 