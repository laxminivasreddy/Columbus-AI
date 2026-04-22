from db.mongodb import get_db
from rag.vector_store import get_vector_store
from utils.llm import call_claude
import json, re

MEMORY_SYSTEM = """You are the Memory Agent. Analyze travel history and extract preferences:
- Preferred budget range
- Travel style
- Interests and enjoyed activities
- Accommodation preferences
- Food preferences
Output as structured JSON."""

class MemoryAgent:
    def __init__(self):
        self.store = get_vector_store()

    async def load_preferences(self, user_id: str) -> dict:
        try:
            db = await get_db()
            if db is None:
                return {}
            user = await db.users.find_one({"user_id": user_id})
            return user.get("preferences", {}) if user else {}
        except Exception:
            return {}

    async def update_preferences(self, user_id: str, feedback: dict):
        prefs = await self.load_preferences(user_id)
        response = await call_claude(
            system_prompt=MEMORY_SYSTEM + " STRICT: Return output as raw JSON only. Without any markdown blocks or conversational text.",
            user_message=f"Current preferences: {json.dumps(prefs)}\nNew feedback: {json.dumps(feedback)}\nReturn merged preference profile as JSON.",
        )
        
        # Clean up possible markdown code blocks
        clean_response = response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.startswith('```'):
            clean_response = clean_response[3:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
            
        clean_response = clean_response.strip()

        try:
            # We attempt to load direct JSON instead of using extremely loose regex matches
            start_idx = clean_response.find('{')
            end_idx = clean_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                clean_response = clean_response[start_idx:end_idx]
                
            updated = json.loads(clean_response)
            db = await get_db()
            if db is not None:
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {"preferences": updated}},
                    upsert=True,
                )
            return updated
        except Exception as e:
            print(f"Memory Agent JSON parse failed: {e}")
            return prefs
