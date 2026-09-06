from chromadb import Client
from app.vector_db.base import VectorDB
class VectorStore(VectorDB):
    def __init__(self):
        self.client = Client()
        self.collection=self.client.get_or_create_collection(name="curato_products")

    def add(self, Pid: str, vector: list[float], metadata: dict):
        self.collection.add(id=Pid, embedding=vector, metadata=metadata)

    def search(self, vector: list[float], top_k: int):
        return self.collection.search(embedding=vector, top_k=top_k)

    def delete(self,pid:list[str]):
        self.collection.delete(ids=pid)
