import logging

from typing import Any
from uuid import uuid4

import httpx
import asyncio

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)


PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'

# Ports must match those in __main__.py
DATA_AGENT_PORT = 9999
SOLVER_AGENT_PORT = 9998

async def test_agent(base_url: str, test_message: str, agent_label: str):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    print(f"\n--- Testing {agent_label} at {base_url} ---")
    
    # Configure httpx client with longer timeouts
    timeout = httpx.Timeout(120.0, connect=10.0)  # 120 second total timeout, 10 second connect timeout
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        try:
            agent_card = await resolver.get_agent_card()
            # logger.info(f"Fetched agent card for {agent_label}:")
            # logger.info(agent_card.model_dump_json(indent=2, exclude_none=True))
        except Exception as e:
            logger.error(f"Failed to fetch agent card for {agent_label}: {e}")
            return
        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
        send_message_payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': test_message}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )
        
        try:
            response = await client.send_message(request)
            print(f"Response from {agent_label}:")
            
            response_dict = response.__dict__
            logger.info(response_dict)
            
            # Extract and print only the text content from artifacts
            if hasattr(response_dict, 'result') and hasattr(response_dict.result, 'artifacts'):
                for artifact in response.result.artifacts:
                    if hasattr(artifact, 'parts'):
                        for part in artifact.parts:
                            if hasattr(part, 'text') and part.text:
                                # Handle the case where text contains a Part object representation
                                text_content = part.text
                                print(f"DEBUG: Raw text content: {repr(text_content)}")
                                
                                if "text='" in text_content and "role=" in text_content:
                                    # Extract the actual text from the Part representation
                                    import re
                                    # Look for text='...' pattern
                                    match = re.search(r"text='([^']*)'", text_content)
                                    if match:
                                        extracted_text = match.group(1)
                                        # Clean up any escaped characters
                                        extracted_text = extracted_text.replace("\\n", "\n")
                                        print(extracted_text)
                                    else:
                                        # Try alternative pattern if the first one doesn't work
                                        match = re.search(r"text=\"([^\"]*)\"", text_content)
                                        if match:
                                            extracted_text = match.group(1)
                                            extracted_text = extracted_text.replace("\\n", "\n")
                                            print(extracted_text)
                                        else:
                                            # Try a more flexible approach
                                            match = re.search(r"text=.*?['\"]([^'\"]*)['\"]", text_content)
                                            if match:
                                                extracted_text = match.group(1)
                                                extracted_text = extracted_text.replace("\\n", "\n")
                                                print(extracted_text)
                                            else:
                                                print(f"Could not parse text from: {text_content}")
                                else:
                                    print(text_content)
                                break
                        else:
                            continue
                        break
                else:
                    print("No text content found in response")
            else:
                print("No artifacts found in response")
                
        except Exception as e:
            logger.error(f"Error getting response from {agent_label}: {e}")
            print(f"Error: {e}")

async def test_simple_queries():
    """Test the problem solver with various simple queries that should work quickly."""
    simple_queries = [
        "What is 2 + 2?",
        "How do I find the maximum value in a list?"
    ]
    
    for i, query in enumerate(simple_queries, 1):
        print(f"\n--- Testing Simple Query {i}: {query} ---")
        await test_agent(
            base_url=f'http://localhost:{SOLVER_AGENT_PORT}',
            test_message=query,
            agent_label=f'Problem Solver Agent (Query {i})'
        )

async def test_data_agent_queries():
    """Test the data agent with proper table and column information."""
    data_queries = [
        "Fetch sample data with columns: id, name, age, salary, department. Generate 10 rows.",
        "Analyze the data and provide a summary of the table structure.",
        "Filter the data where age is greater than 25.",
        "Show me the correlation between age and salary in the data.",
        "Get statistics for all numeric columns in the dataset."
    ]
    
    for i, query in enumerate(data_queries, 1):
        print(f"\n--- Testing Data Agent Query {i}: {query} ---")
        await test_agent(
            base_url=f'http://localhost:{DATA_AGENT_PORT}',
            test_message=query,
            agent_label=f'Data Agent (Query {i})'
        )

async def main():
    # Test Data Agent with proper table information
    await test_agent(
        base_url=f'http://localhost:{DATA_AGENT_PORT}',
        test_message='Create a sample dataset with columns: id, name, age, salary, department. Generate 15 rows of employee data.',
        agent_label='Data Agent'
    )
    
    # Test Data Agent with analysis
    await test_agent(
        base_url=f'http://localhost:{DATA_AGENT_PORT}',
        test_message='Analyze the employee data and show me the summary statistics for age and salary columns.',
        agent_label='Data Agent'
    )
    
    # Test multiple data agent queries
    # await test_data_agent_queries()
    
    # # Test Problem Solver Agent with simple queries
    # await test_agent(
    #     base_url=f'http://localhost:{SOLVER_AGENT_PORT}',
    #     test_message='How do I calculate the average of numbers 1, 2, 3, 4, 5?',
    #     agent_label='Problem Solver Agent'
    # )
    
    # # Test with another simple problem
    # await test_agent(
    #     base_url=f'http://localhost:{SOLVER_AGENT_PORT}',
    #     test_message='What is the best way to sort a list of numbers?',
    #     agent_label='Problem Solver Agent'
    # )
    
    # # Test multiple simple queries
    # await test_simple_queries()

if __name__ == '__main__':
    asyncio.run(main())
