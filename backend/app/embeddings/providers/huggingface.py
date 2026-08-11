from app.embeddings.base import BaseEmbedding
from app.embeddings.embedding_service import EmbeddingService
from sentence_transformers import SentenceTransformer

class HuggingFaceEmbedding(BaseEmbedding):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def embed(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()