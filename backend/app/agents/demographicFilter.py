from typing import Any

from app.models.user import UserProfile
from app.state.userState import UserState
from app.models.product import Product
from sqlalchemy.orm import Session
from app.postgres.postgres import PostgresHandler
from app.llm.userBehaviorLLM import userBehaviorLLM
from app.vector_db.vector_store import VectorDBSearchAgent

class DemographicFilter:
    def __init__(self):
        self.user_id=None
        self.age=None
        self.gender=None
        self.city=None
        self.state=None
        self.country=None

    def initialize_user_demographics(self, user_id: str) -> None:
        user_profile = PostgresHandler().get_user_profile_from_postgres(user_id)
        if user_profile:
            self.user_id = user_id
            self.age = user_profile.age
            self.gender = user_profile.gender
            self.city = user_profile.city
            self.state = user_profile.state
            self.country = user_profile.country
        else:
            print(f"No user profile found for user_id: {user_id}")
            
    def filter_products_by_demographics(self, userState: UserState): 
        if self.age is None or self.gender is None or self.city is None or self.state is None or self.country is None:
            print("Demographic attributes are not initialized.")
            return []
        else:
            current_user_demographics = {
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "state": self.state,
            "country": self.country
            }
        users_ids = PostgresHandler().search_demographic_users_ids(current_user_demographics) 
        users_preferences = []
        current_user_demographic_preferences = []
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
            current_user_demographic_preferences.extend(users_preferences)
        demographic_insights = userBehaviorLLM().analyze_user_behavior(current_user_demographic_preferences)
        userState.update_user_preferences(self.user_id, demographic_insights)
        candidate_products = VectorDBSearchAgent().searchVectorDB(userState.get_current_state(self.user_id))
        userState.add_top_products_to_userState(candidate_products)
        print(f"Demographic filtering completed for user_id: {self.user_id} with candidate products: {candidate_products}")
        
            
            