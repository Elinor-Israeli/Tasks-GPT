from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, CollectionStatus

class QdrantManager:
    def __init__(self, host="localhost", port=6333, collection_name="tasks", vector_size=384):
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        self._ensure_collection()
        self.vector_size = vector_size

    def _ensure_collection(self):
        if self.collection_name not in  [c.name for c in self.client.get_collections().collections]:
            self.client.recreate_collection( # TODO: in the production state use create with real data
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )             

    def get_client(self):
        return self.client        

# this file connects to a running Qdrant intance , ensures the "tasks" collection exists,
# sets it up to accept 384-dimensional vectors with cosine similarity (same dimension as sentence-transformers model output).    