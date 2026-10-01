from app.state.userState import UserState
from app.vector_db.vector_store import VectorDBSearchAgent
from app.embeddings.embedding_service import EmbeddingService
from scipy.stats import pearsonr
from app.state.userState import UserState
from app.llm.collaborative_summary_llm import CollaborativeSummaryLLM
from app.postgres.postgres import PostgresHandler
class Collaborative_filter:
    
    def __init__(self,userstate: UserState):
        self.userstate = userstate
        self.user_id = userstate.get_user_id()
        
    def memory_based_cf(self, user_id: int) -> list[dict[str, any]]:
        user_embeddings = EmbeddingService().user_embedding(user_id)
        candidate_users=VectorDBSearchAgent().search_vectors(user_embeddings, top_k=10)
        correlations=[]
        for user in candidate_users:
            correlation, _ = pearsonr(user_embeddings, user['embedding'])
            correlations.append((user['user_id'], correlation))
        top_similar_users = sorted(correlations, key=lambda x: x[1], reverse=True)[:5]
        top_similar_user_ids = [user[0] for user in top_similar_users]
        
        candidate_recommendations_insights = []
        for similar_user_id in top_similar_user_ids:
            profile = PostgresHandler().get_user_profile_from_postgres(similar_user_id)
            product_preferences=profile.get('user_preferences', [])
            candidate_recommendations_insights.extend(product_preferences)
        current_user_profile = self.userstate.get_current_state(user_id)
        user_insights_set=CollaborativeSummaryLLM().summarize_user_insights(candidate_recommendations_insights, current_user_profile)
        products=VectorDBSearchAgent().search_vectors(user_insights_set)  
        self.userstate.add_top_products_to_userState(products)
        print(f"Collaborative filtering completed for user_id: {user_id}. Top products added to user state.")  
            
        
    
        