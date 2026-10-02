from app.embeddings.embedding_service import EmbeddingService
from app.vector_db.vector_store import VectorStore
from app.embeddings.providers.huggingface import HuggingFaceEmbedding
from app.state.userState import UserState

class EmbeddingDBService:

    def __init__(self):
        embedding_model = HuggingFaceEmbedding()
        self.embedding_service = EmbeddingService(embedding_model)
        self.vector_store = VectorStore()

    def add_product_embedding(self, product_id: str, text: str, metadata: dict):
        vector = self.embedding_service.embed(text)
        self.vector_store.add_product(product_id, vector, metadata)

    def search_products(self, vector: list[float], top_k: int):
        return self.vector_store.search_products(vector, top_k)

    def delete_product_embedding(self, product_id: str):
        self.vector_store.delete_product(product_id)

    def add_user_embedding(self, user_id: str, text: str, metadata: dict):
        vector = self.embedding_service.embed(text)
        self.vector_store.add_user(user_id, vector, metadata)

    def search_users(self, vector: list[float], top_k: int):
        return self.vector_store.search_users(vector, top_k)

    def delete_user_embedding(self, user_id: str):
        self.vector_store.delete_user(user_id)

    def get_vector(self, text: str) -> list[float]:
        return self.embedding_service.embed(text)