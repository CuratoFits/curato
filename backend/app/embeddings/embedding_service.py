from app.embeddings.base import BaseEmbedding

class EmbeddingService():
    def __init__(self, embedding_model: BaseEmbedding):
        self.embedding_model = embedding_model
        
    def embed(self, text: str) -> list[float]:
        return self.embedding_model.embed(text)