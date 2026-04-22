import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.chroma = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.travel_collection = self.chroma.get_or_create_collection(
            name="travel_guides",
            metadata={"hnsw:space": "cosine"},
        )
        self.trips_collection = self.chroma.get_or_create_collection(name="user_trips")
        self.reviews_collection = self.chroma.get_or_create_collection(name="reviews")

    def embed(self, texts: list) -> np.ndarray:
        return self.embedder.encode(texts, normalize_embeddings=True)

    def upsert_travel_guide(self, doc_id: str, text: str, metadata: dict):
        embedding = self.embed([text])[0].tolist()
        self.travel_collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

    def retrieve(self, query: str, collection_name: str = "travel_guides", top_k: int = 5, filter_meta: dict = None) -> list:
        collection = self.chroma.get_collection(collection_name)
        query_embedding = self.embed([query])[0].tolist()
        kwargs = {"query_embeddings": [query_embedding], "n_results": top_k}
        if filter_meta:
            kwargs["where"] = filter_meta
        results = collection.query(**kwargs)
        docs = []
        for i, doc in enumerate(results["documents"][0]):
            docs.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i],
            })
        return docs

_store = None

def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
