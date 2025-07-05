from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AddableVectorStore(ABC):
    @abstractmethod
    def add(self, task_id: int, title: str, user_id: int) -> None:
        pass

class SearchableVectorStore(ABC):
    @abstractmethod
    def search(self, query: str, user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        pass

class RemovableVectorStore(ABC):
    @abstractmethod
    def remove(self, task_id: int, user_id: int) -> None:
        pass
