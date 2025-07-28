#!/usr/bin/env python3
"""Simple test script to verify agent functionality without A2A server."""

import asyncio
from my_a2a_agents.data_agent import DataAgent
from my_a2a_agents.problem_solver_agent import ProblemSolverAgent

async def test_data_agent():
    """Test the data agent functionality."""
    print("Testing Data Agent...")
    try:
        agent = DataAgent()
        print("✅ Data Agent initialized successfully")
        
        # Test a simple query
        result = await agent.invoke("Get sample data")
        print(f"✅ Data Agent response: {result['status']}")
        return True
    except Exception as e:
        print(f"❌ Data Agent test failed: {e}")
        return False

async def test_problem_solver_agent():
    """Test the problem solver agent functionality."""
    print("Testing Problem Solver Agent...")
    try:
        agent = ProblemSolverAgent()
        print("✅ Problem Solver Agent initialized successfully")
        
        # Test a simple query
        result = await agent.invoke("Analyze this sorting problem")
        print(f"✅ Problem Solver Agent response: {result['status']}")
        return True
    except Exception as e:
        print(f"❌ Problem Solver Agent test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Testing Agent Functionality")
    print("=" * 40)
    
    data_success = await test_data_agent()
    print()
    solver_success = await test_problem_solver_agent()
    
    print("\n" + "=" * 40)
    print("📋 Test Results:")
    print(f"   Data Agent: {'✅ Passed' if data_success else '❌ Failed'}")
    print(f"   Problem Solver Agent: {'✅ Passed' if solver_success else '❌ Failed'}")
    
    if data_success and solver_success:
        print("\n🎉 All tests passed! The agents are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 