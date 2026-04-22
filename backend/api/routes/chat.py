from fastapi import APIRouter
from pydantic import BaseModel
from utils.llm import call_claude
from rag.pipeline import RAGPipeline
from db.redis_client import get_redis
import json

router = APIRouter()
rag = RAGPipeline()

CHAT_SYSTEM = """You are Columbus AI, a conversational travel assistant.
Help users refine travel plans through natural conversation.
Remember context. When constraints change, acknowledge and offer to regenerate.
Be friendly, knowledgeable, and enthusiastic about travel."""

class ChatMessage(BaseModel):
    user_id: str
    message: str
    session_id: str

@router.post("/message")
async def chat_message(body: ChatMessage):
    redis = await get_redis()
    history_raw = await redis.get(f"chat:{body.session_id}")
    history = json.loads(history_raw) if history_raw else []
    rag_context = await rag.retrieve_and_synthesize(body.message, "")
    enriched_msg = f"{body.message}\n\n[Context]: {rag_context}"
    response = await call_claude(
        system_prompt=CHAT_SYSTEM,
        user_message=enriched_msg,
        conversation_history=history,
    )
    history.append({"role": "user", "content": body.message})
    history.append({"role": "assistant", "content": response})
    await redis.setex(f"chat:{body.session_id}", 3600, json.dumps(history[-20:]))
    return {"response": response, "session_id": body.session_id}
