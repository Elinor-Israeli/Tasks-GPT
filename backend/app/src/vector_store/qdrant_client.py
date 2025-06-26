import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def _ensure_collection(client: QdrantClient, collection_name: str, vector_size: int, reset: bool):
    collections = [c.name for c in client.get_collections().collections]

    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )             
        
    elif collection_name not in collections:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )             

def get_qdrant_client(
        host=None,  
        port=6333, 
        collection_name="tasks", 
        vector_size=384, 
        reset=False
    ) -> QdrantClient:

    host = host or os.getenv("QDRANT_HOST", "localhost")
    client = QdrantClient(host=host, port=port)
    _ensure_collection(client, collection_name, vector_size, reset)
    return client        

# This file connects to a running Qdrant instance, ensures the "tasks" collection exists,
# and sets it up to accept 384-dimensional vectors with cosine similarity (same as sentence-transformers model output).
# Use `reset=True` only in development/testing to forcibly recreate the collection.