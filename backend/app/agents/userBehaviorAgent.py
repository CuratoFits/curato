from app.state.userState import UserState
from app.postgres import PostgresHandler
from app.llm.userBehaviorLLM import userBehaviorLLM

class UserBehaviorAgent:

    def user_behavior(user_id: str) -> dict[str, any]:
        try:
            interaction_history= PostgresHandler().get_events_from_postgres(user_id)
            current_activity= PostgresHandler().get_current_interaction_events(user_id)
            user_behavior = {
                "user_id": user_id,
                "events": interaction_history,
                "current_state": current_activity
            }
            insight = userBehaviorLLM().analyze_user_behavior(user_behavior)
            print(f"User behavior insights for {user_id}: {insight}")
        except Exception as e:
            print(f"Error at user_behavior: {e}")
            return {}
        return insight
 