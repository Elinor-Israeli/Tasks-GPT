from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient
from .text_embedder import TextEmbedder
from .interfaces import AddableVectorStore, SearchableVectorStore, RemovableVectorStore 
from uuid import uuid4
from src.utils.logger import logger
from typing import Optional
class TaskVectorStore(AddableVectorStore, SearchableVectorStore, RemovableVectorStore):
    """
    A vector store for task data using Qdrant and text embedding.

    This class allows storing, searching, and removing vectorized representations 
    of tasks based on their title. It ensures that tasks are grouped per user 
    using payload metadata.

    Attributes:
        client (QdrantClient): Qdrant client for vector database operations.
        embedder (TextEmbedder): Embedding utility for task titles.
        collection_name (str): The name of the Qdrant collection to use.
    """
    def __init__(self, client: QdrantClient, embedder: TextEmbedder, collection_name: str ="tasks"):
        self.client = client
        self.embedder = embedder
        self.collection_name = collection_name

    def add(self, task_id: int, title: str, user_id: int, due_date: Optional[str]=None):
        """
        Adds a new task vector to the collection.

        Args:
            task_id (int): Unique ID of the task.
            title (str): Title of the task to be embedded.
            user_id (int): ID of the user who owns the task.
            due_date (Optional[str]): Optional due date in string format.
        """
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
        """
        Searches for the top-k most relevant tasks for a given query and user.

        Args:
            query (str): Text to search against stored task titles.
            user_id (int): ID of the user to restrict the search to.
            top_k (int): Maximum number of results to return.

        Returns:
            List[ScoredPoint]: Top matching task vectors.
        """
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
        """
        Removes a task vector from the collection based on task and user ID.

        Args:
            task_id (int): ID of the task to remove.
            user_id (int): ID of the user who owns the task.
        """
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


        

