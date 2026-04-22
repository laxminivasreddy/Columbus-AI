from rag.vector_store import get_vector_store
from utils.llm import call_claude

RETRIEVAL_SYSTEM = """You are a travel knowledge synthesizer.
Given retrieved travel documents and a user query, extract only the
relevant facts that will help plan the trip for the requested destination.
CRITICAL: Only extract facts that are explicitly about the requested destination. If the retrieved documents are about completely different cities or places, ignore them and return exactly: 'No specific guide data available — using general knowledge.'
Be concise and factual.
Format: bullet points of key facts."""

class RAGPipeline:
    def __init__(self):
        self.store = get_vector_store()

    async def retrieve_and_synthesize(self, query: str, destination: str, top_k: int = 3) -> str:
        try:
            travel_docs = self.store.retrieve(
                query=f"{destination} {query}",
                collection_name="travel_guides",
                top_k=top_k,
            )
            if not travel_docs:
                return "No specific guide data available — using general knowledge."
        except Exception as e:
            print(f"Gemini API Embedding Error: {e}")
            return "No specific guide data available — using general knowledge."
        context = "\n\n".join([
            f"[Source: {d['metadata'].get('source', 'guide')} | Relevance: {d['score']:.2f}]\n{d['text']}"
            for d in travel_docs
        ])
        synthesized = await call_claude(
            system_prompt=RETRIEVAL_SYSTEM,
            user_message=f"Query: {query}\n\nRetrieved documents:\n{context}",
            max_tokens=1024,
        )
        return synthesized

    async def retrieve_user_history(self, user_id: str, query: str) -> str:
        try:
            docs = self.store.retrieve(query=query, collection_name="user_trips", top_k=3)
            if not docs:
                return "No prior trips found for this user."
            return "\n".join([d["text"] for d in docs])
        except Exception:
            return "No prior trips found for this user."
