from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

class QdrantManager:
    def __init__(self, host="localhost", port=6333, collection_name="tasks", vector_size=384, reset=False):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = QdrantClient(host=host, port=port)
        self._ensure_collection(reset)

    def _ensure_collection(self, reset: bool=False):
        collections = [c.name for c in self.client.get_collections().collections]

        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )             
            
        elif self.collection_name not in collections:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )             

    def get_client(self):
        return self.client        

# This file connects to a running Qdrant instance, ensures the "tasks" collection exists,
# and sets it up to accept 384-dimensional vectors with cosine similarity (same as sentence-transformers model output).
# Use `reset=True` only in development/testing to forcibly recreate the collection.