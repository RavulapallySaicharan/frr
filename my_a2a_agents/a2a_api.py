import os
import json
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from typing import Any
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from uuid import uuid4

app = FastAPI(title="A2A Agent Registration API")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("a2a_api")

AGENT_CARDS_DIR = "agent_cards"
os.makedirs(AGENT_CARDS_DIR, exist_ok=True)

class RegisterAgentRequest(BaseModel):
    agent_name: str
    a2a_url: str

@app.post("/register-agent")
async def register_agent(req: RegisterAgentRequest):
    result = {
        "agent_name": req.agent_name,
        "status": None,
        "card_saved": False,
        "execution_test": {
            "success": False,
            "response": None,
            "error": None
        },
        "errors": []
    }
    # Step 1: Validate A2A server by fetching agent card using A2ACardResolver
    card_path = os.path.join(AGENT_CARDS_DIR, f"{req.agent_name}.json")
    agent_card = None
    try:
        async with httpx.AsyncClient(timeout=10) as httpx_client:
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=req.a2a_url)
            logger.info(f"Fetching agent card from {req.a2a_url}")
            agent_card = await resolver.get_agent_card()
            card_json = agent_card.model_dump(exclude_none=True)
            # Check for required fields in agent card (customize as needed)
            if not ("name" in card_json and "skills" in card_json):
                raise ValueError("Agent card missing required fields (name, skills)")
            with open(card_path, "w", encoding="utf-8") as f:
                json.dump(card_json, f, indent=2)
            logger.info(f"Agent card saved to {card_path}")
            result["card_saved"] = True
    except Exception as e:
        logger.error(f"Agent card fetch/save failed: {e}")
        result["status"] = "card_fetch_failed"
        result["errors"].append(f"Agent card fetch/save failed: {e}")
        return JSONResponse(result, status_code=400)

    # Step 2: Test agent execution using A2AClient
    try:
        async with httpx.AsyncClient(timeout=10) as httpx_client:
            client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': 'Hello world'}
                    ],
                    'messageId': uuid4().hex,
                },
            }
            request = SendMessageRequest(
                id=str(uuid4()), params=MessageSendParams(**send_message_payload)
            )
            logger.info(f"Sending test message to agent at {req.a2a_url}")
            response = await client.send_message(request)
            logger.info(f"Agent execution test succeeded: {response.model_dump(mode='json', exclude_none=True)}")
            result["execution_test"]["success"] = True
            result["execution_test"]["response"] = response.model_dump(mode='json', exclude_none=True)
    except Exception as e:
        logger.error(f"Agent execution test failed: {e}")
        result["execution_test"]["error"] = str(e)
        result["status"] = "execution_failed"
        return JSONResponse(result, status_code=400)

    result["status"] = "registered"
    return result 