from typing import Any

from ..state.userState import UserState
from app.postgres import postgres_handler

class EventFetcherAgent:
    def __init__(self):
        self.user_state = UserState()

    def fetch_events(self, user_id: str) -> Any:
        try:
            events = postgres_handler.get_events_from_postgres(user_id)
        except Exception as e:
            print(f"Error at fetch_events: {e}")
        self.user_state.updateUserState(user_id, events)

