from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schema import User
from app.agents.orchestrator import create_market_agent
import logging

agent_router = APIRouter()
logger = logging.getLogger(__name__)

# Cache the agent instance globally so we don't recreate the graph on every request
_agent_instance = None

def get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = create_market_agent()
    return _agent_instance

class MessageItem(BaseModel):
    role: str
    content: str

class ChatPayload(BaseModel):
    messages: List[MessageItem]

@agent_router.post("/chat")
async def chat_with_agent(
    payload: ChatPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        agent = get_agent()
        
        # Convert frontend messages dicts to the tuple format expected by the LangGraph agent
        chat_history = []
        for msg in payload.messages:
            # We map 'assistant' to 'assistant' and anything else to 'user' 
            # (as the agent currently expects ("user", "...") and ("assistant", "..."))
            role = "assistant" if msg.role == "assistant" else "user"
            chat_history.append((role, msg.content))
            
        logger.info(f"Invoking agent with {len(chat_history)} messages.")
        response = agent.invoke({"messages": chat_history})
        
        raw_bot_reply = "The Oracle was unable to formulate a response."
        if "messages" in response and len(response["messages"]) > 0:
            raw_bot_reply = response["messages"][-1].content
            
        return {
            "response": raw_bot_reply
        }
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

