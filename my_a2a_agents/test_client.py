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
            logger.info(f"Fetched agent card for {agent_label}:")
            logger.info(agent_card.model_dump_json(indent=2, exclude_none=True))
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
            print(response.model_dump(mode='json', exclude_none=True))
        except Exception as e:
            logger.error(f"Error getting response from {agent_label}: {e}")
            print(f"Error: {e}")

async def main():
    # Test Data Agent
    await test_agent(
        base_url=f'http://localhost:{DATA_AGENT_PORT}',
        test_message='Get the data table',
        agent_label='Data Agent'
    )
    # Test Problem Solver Agent
    await test_agent(
        base_url=f'http://localhost:{SOLVER_AGENT_PORT}',
        test_message='Solve this problem with the data: 1,2,3',
        agent_label='Problem Solver Agent'
    )

if __name__ == '__main__':
    asyncio.run(main())
