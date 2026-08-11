from app.state.userState import UserState
from app.postgres import postgres_handler
from app.llm.userBehaviorLLM import userBehaviorLLM

class UserBehaviorAgent:
    
    def user_history(self, user_id: str) -> list[dict[str, any]]:
        try:
            events = postgres_handler.get_events_from_postgres(user_id)
        except Exception as e:
            print(f"Error at user_history: {e}")
            return []
        return events
    
    def user_current_state(self, user_id: str) -> dict[str, any]:
        try:
            current_state = UserState.get_current_state(user_id)
        except Exception as e:
            print(f"Error at user_current_state: {e}")
            return {}
        return current_state

    def user_behavior(self, user_id: str) -> dict[str, any]:
        try:
            past_user_behavior = self.user_history(user_id)
            current_state = self.user_current_state(user_id)
            user_behavior = {
                "user_id": user_id,
                "events": past_user_behavior,
                "current_state": current_state
            }
            insight = userBehaviorLLM().analyze_user_behavior(user_behavior)
            print(f"User behavior insights for {user_id}: {insight}")
        except Exception as e:
            print(f"Error at user_behavior: {e}")
            return {}
        return insight
 