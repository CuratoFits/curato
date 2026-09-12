from abc import ABC, abstractmethod

class VectorDB(ABC):
    @abstractmethod
    def add(self, vector: list[float],metadata: dict):
        pass
    @abstractmethod
    def search(self, vector: list[float], top_k: int):
        pass
    @abstractmethod
    def delete(self, vector: list[float]):
        pass

    