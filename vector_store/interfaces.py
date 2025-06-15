from abc import ABC, abstractmethod

class Addable(ABC):
    @abstractmethod
    def add(self, task_id: int, title: str, user_id: int):
        pass

class Searchable(ABC):
    @abstractmethod
    def search(self, query: str, user_id: int, top_k: int = 5):
        pass

class Removable(ABC):
    @abstractmethod
    def remove (self, task_id: int, user_id: int):
        pass
