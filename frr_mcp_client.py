import asyncio
from mcp_client_base import MCPClient

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