from chromadb import Client
from abc import ABC, abstractmethod

class VectorDB(ABC):
    def __init__(self):
        self.client = Client()

    