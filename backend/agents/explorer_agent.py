from utils.llm import call_claude
from rag.vector_store import get_vector_store
import json

EXPLORER_SYSTEM = """You are the Exploration Agent — you find hidden gems and
off-the-beaten-path experiences. Avoid tourist traps.
For each place include: why it's a hidden gem, best time to visit,
local insider tips, how to get there. Explain why it suits this traveler."""

class ExplorerAgent:
    def __init__(self):
        self.store = get_vector_store()

    async def find_hidden_gems(self, destination, interests, existing_itinerary):
        query = f"hidden gems local secrets {destination} {' '.join(interests)}"
        docs = self.store.retrieve(query=query, top_k=5)
        context = "\n".join([d["text"] for d in docs])
        response = await call_claude(
            system_prompt=EXPLORER_SYSTEM,
            user_message=f"""
Destination: {destination}
Traveler interests: {', '.join(interests)}

Retrieved local knowledge:
{context}

Suggest 3-5 hidden gems not already in this itinerary:
{json.dumps(existing_itinerary, indent=2)}
""",
            max_tokens=1500
        )
        return [{"suggestion": response, "source": "explorer_agent"}]
