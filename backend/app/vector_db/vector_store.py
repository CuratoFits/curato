from chromadb import Client
from app.vector_db.base import VectorDB

class VectorStore(VectorDB):

    def __init__(self):
        self.client = Client()
        self.product_collection = self.client.get_or_create_collection(name="curato_products", configuration={"hnsw": {"space": "cosine"}})
        self.user_collection = self.client.get_or_create_collection(name="curato_users", configuration={"hnsw": {"space": "cosine"}})

    def add_product(self, product_id: str, vector: list[float], metadata: dict):
        self.product_collection.add(ids=[product_id], embeddings=[vector], metadatas=[metadata])

    def add_user(self, user_id: str, vector: list[float], metadata: dict):
        self.user_collection.add(ids=[user_id], embeddings=[vector], metadatas=[metadata])

    def search_products(self, vector: list[float], top_k: int):
        return self.product_collection.query(query_embeddings=[vector], n_results=top_k, include=["metadatas", "distances"])

    def search_users(self, vector: list[float], top_k: int):
        return self.user_collection.query(query_embeddings=[vector], n_results=top_k, include=["metadatas", "distances"])

    def delete_product(self, product_id: str):
        self.product_collection.delete(ids=[product_id])

    def delete_user(self, user_id: str):
        self.user_collection.delete(ids=[user_id])