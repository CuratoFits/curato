from typing import Any

from app.models.user import UserProfile
from app.state.userState import UserState
from app.models.product import Product
from sqlalchemy.orm import Session
from app.postgres.postgres import PostgresHandler
from app.llm.collaborative_summary_llm import CollaborativeSummaryLLM
from app.vector_db.vector_store import VectorStore
from app.embeddings.embedding_service import EmbeddingDBService
class DemographicFilter:
    def __init__(self,userstate: UserState,embeddingservice: EmbeddingDBService,
                 vectorstore: VectorStore):
        self.userstate = userstate
        self.user_id=userstate.get_user_id()
        self.embedding_db_service = embeddingservice
        self.vector_store = vectorstore
        self.age=None
        self.gender=None
        self.city=None
        self.state=None
        self.country=None

    def initialize_user_demographics(self) -> None:
        user_profile = PostgresHandler().get_user_profile_from_postgres(self.user_id)
        if user_profile:
            self.age = user_profile.age
            self.gender = user_profile.gender
            self.city = user_profile.city
            self.state = user_profile.state
            self.country = user_profile.country
        else:
            print(f"No user profile found for user_id: {self.user_id}")
            
    def filter_products_by_demographics(self): 
        if self.age is None and self.gender is None and self.city is None and self.state is None and self.country is None:
            print("Demographic attributes are not initialized.")
            return []
        else:
            current_user_demographics = f"Age: {self.age}, Gender: {self.gender}, City: {self.city}, State: {self.state}, Country: {self.country}"
            vector = self.embedding_db_service.get_vector(current_user_demographics)
        users_list= self.vector_store.search_users(vector, top_k=15)
        users_ids=users_list["ids"][0]
        users_preferences = []
        for i in users_ids:
            users_profile = PostgresHandler().get_user_profile_from_postgres(i)   
            users_preferences.append({
                "preferred_min_price": users_profile.preferred_min_price,
                "preferred_max_price": users_profile.preferred_max_price,
                "preferred_rating": users_profile.preferred_rating,
                "preferred_categories": users_profile.preferred_categories,
                "preferred_brands": users_profile.preferred_brands,
                "preferred_colors": users_profile.preferred_colors,
                "preferred_materials": users_profile.preferred_materials,
                "preferred_styles": users_profile.preferred_styles,
                "preferred_occasions": users_profile.preferred_occasions
            })
        current_activity=PostgresHandler().get_current_interaction_events(self.user_id)    
        demographic_insights = CollaborativeSummaryLLM().get_insight_summary(users_preferences, current_activity)
        insight_vector = self.embedding_db_service.get_vector(demographic_insights)
        candidate_products = self.vector_store.search_products(insight_vector, top_k=100)
        product_ids=candidate_products['ids'][0]
        self.userstate.add_top_products_to_userState(product_ids)
        print(f"Demographic filtering completed for user_id: {self.user_id}")
        
            
            