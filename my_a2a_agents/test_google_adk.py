#!/usr/bin/env python3
"""
Test script for Google ADK integration
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_google_adk_import():
    """Test if google-adk can be imported."""
    try:
        from google.adk.agents import Agent, LlmAgent
        print("✅ Successfully imported google-adk")
        return True
    except ImportError as e:
        print(f"❌ Failed to import google-adk: {e}")
        return False

def test_agent_creation():
    """Test if we can create agents with google-adk and LiteLLM."""
    try:
        from google.adk.agents import Agent, LlmAgent
        from config import Config
        
        config = Config()
        
        # Create a simple test function
        def test_tool(input_text: str) -> str:
            return f"Processed: {input_text}"
        
        # Create agent with function as tool
        agent = Agent(
            name="Test Agent",
            description="A test agent",
            tools=[test_tool],
            model=config.LITELLM_MODEL,
            model_config={
                "provider": "openai",
                "api_key": config.OPENAI_API_KEY,
                "temperature": config.LITELLM_TEMPERATURE,
                "max_tokens": config.LITELLM_MAX_TOKENS
            }
        )
        print("✅ Successfully created agent with google-adk and LiteLLM")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False

def test_litellm_integration():
    """Test if LiteLLM works with our configuration."""
    try:
        import litellm
        from litellm import completion
        from config import Config
        
        config = Config()
        
        # Test a simple completion
        response = completion(
            model=config.LITELLM_MODEL,
            messages=[{"role": "user", "content": "Hello, world!"}],
            max_tokens=10
        )
        
        print("✅ Successfully tested LiteLLM integration")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test LiteLLM: {e}")
        return False

def test_agent_execution():
    """Test if the agent can execute with LiteLLM."""
    try:
        from google.adk.agents import Agent, LlmAgent
        from config import Config
        
        config = Config()
        
        # Create a simple test function
        def greet(name: str) -> str:
            return f"Hello, {name}!"
        
        # Create agent with function as tool
        agent = Agent(
            name="Test Agent",
            description="A test agent",
            tools=[greet],
            model=config.LITELLM_MODEL,
            model_config={
                "provider": "openai",
                "api_key": config.OPENAI_API_KEY,
                "temperature": config.LITELLM_TEMPERATURE,
                "max_tokens": config.LITELLM_MAX_TOKENS
            }
        )
        
        # Test agent execution
        result = agent.run("Say hello to John")
        print("✅ Successfully tested agent execution with LiteLLM")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test agent execution: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Google ADK Integration")
    print("=" * 40)
    
    tests = [
        ("Google ADK Import", test_google_adk_import),
        ("Agent Creation", test_agent_creation),
        ("LiteLLM Integration", test_litellm_integration),
        ("Agent Execution", test_agent_execution)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("📋 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Google ADK integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check your installation and configuration.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 