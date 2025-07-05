from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient
from .text_embedder import TextEmbedder
from .interfaces import AddableVectorStore, SearchableVectorStore, RemovableVectorStore 
from uuid import uuid4
from src.utils.logger import logger
from typing import Optional
class TaskVectorStore(AddableVectorStore, SearchableVectorStore, RemovableVectorStore):
    def __init__(self, client: QdrantClient, embedder: TextEmbedder, collection_name: str ="tasks"):
        self.client = client
        self.embedder = embedder
        self.collection_name = collection_name

    def add(self, task_id: int, title: str, user_id: int, due_date: Optional[str]=None):
        vector = self.embedder.embed(title)
        logger.debug(f"Storing vector for task_id={task_id}, title='{title}', user_id={user_id}")
        
        payload = {
        "task_id": task_id,
        "title": title,
        "user": user_id
        }

        if due_date: 
            payload["due_date"] = due_date

        point = PointStruct(
            id = task_id, 
            vector=vector,
            payload=payload
        )

        self.client.upsert(
            collection_name=self.collection_name, 
            points=[point]
        )
        logger.info(f"Vector upserted for task_id={task_id}, user_id={user_id}, title='{title}', due_date={due_date}")


    def search(self, query: str, user_id: int, top_k: int = 5):
        logger.debug(f"Embedding and searching for query='{query}' (user_id={user_id})")
        vector = self.embedder.embed(query)

        user_filter = Filter(
            must=[
                FieldCondition(
                    key="user",
                    match=MatchValue(value=user_id)
                )
            ]
        ) 

        results = self.client.search(
            collection_name = self.collection_name,
            query_vector=vector,
            query_filter=user_filter,
            limit=top_k
        ) 

        logger.info(f"Search completed: query='{query}', top_k={top_k}, user_id={user_id}, results={len(results)}")
        return results

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

        logger.debug(f"Task removal issued for task_id={task_id}, user_id={user_id}")


        

