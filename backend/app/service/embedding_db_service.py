from app.embeddings.embedding_service import EmbeddingService
from app.vector_db.vector_store import VectorStore
from app.embeddings.providers.huggingface import HuggingFaceEmbedding
class EmbeddingDBService:
    def __init__(self):
        embedding_model = HuggingFaceEmbedding()
        self.embedding_service = EmbeddingService(embedding_model)
        self.vector_store = VectorStore()

    def add_embedding(self, Pid: str, text: str, metadata: dict):
        vector = self.embedding_service.embed(text)
        self.vector_store.add(Pid, vector, metadata)

    def search_embedding(self, text: str, top_k: int):
        vector = self.embedding_service.embed(text)
        return self.vector_store.search(vector, top_k)

    def delete_embedding(self, pid: list[str]):
        self.vector_store.delete(pid)