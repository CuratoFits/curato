from app.service.embedding_db_service import EmbeddingDBService
from app.agents.userBehaviorAgent import UserBehaviorAgent
from app.state.userState import UserState
class VectorDBSearchAgent:
    def __init__(self):
        self.embedding_db_service = EmbeddingDBService()
        self.userstate = UserState()
        self.user_id = self.userstate.get_user_id()
        
    def searchVectorDB(self):
        if self.user_id is None:
            print("User ID is not set. Cannot perform search.")
        else:
            text=self.userstate.get_current_state(self.user_id) 
            print(f"Searching vector database for user_id: {self.user_id} with text: {text}")
            top_products = self.embedding_db_service.search_embedding(text, top_k=100)   
            print(f"Search completed for user_id: {self.user_id} with text: {text}")
            return top_products
    
    def add_top_products_to_userState(self, top_products):
        if self.user_id is None:
            print("User ID is not set. Cannot add top products to user state.")
        else:
            self.userstate.add_top_products_to_userState(top_products)
            print(f"Top products added to user state for user_id: {self.user_id}")    
            