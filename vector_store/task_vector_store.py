from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient
from .embedder import TextEmbedder
from .interfaces import Addable, Searchable, Removable 
from uuid import uuid4

class TaskVectorStore(Addable, Searchable, Removable):
    def __init__(self, client: QdrantClient, embedder: TextEmbedder, collection_name: str ="tasks"):
        self.client = client
        self.embedder = embedder
        self.collection_name = collection_name

    def add(self, task_id: int, title: str, user_id: int):
        vector = self.embedder.embed(title)
        point = PointStruct(
            id = uuid4().int >> 64, #generate 64-bit int ID
            vector=vector,
            payload={
                "task_id": task_id,
                "title": title, 
                "user": user_id
            } 
        )

        self.client.upsert(collection_name=self.collection_name, points=[point])


    def search(self, query: str, user_id:int, top_k: int = 5):
        vector = self.embedder.embed(query)

        user_filter = Filter(
            must=[
                FieldCondition(
                    key="user",
                    match=MatchValue(value=user_id)
                )
            ]
        ) 

        return self.client.search(
            collection_name = self.collection_name,
            query_vector=vector,
            query_filter=user_filter,
            limit=top_k
        )  

    def remove(self, task_id: int, user_id: int):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(key="task_id", match=MatchValue(value=task_id)),
                    FieldCondition(key="user", match=MatchValue(value=user_id))
                ]
            )
        )

           

        

