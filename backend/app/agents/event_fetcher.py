from typing import Any

from ..state.userState import UserState


class EventFetcherAgent:
    def __call__(self, state: UserState) -> dict[str, Any]:
        user_id = state.get("user_id")
        events = state.get("events", [])
        preferences = state.get("preferences", {})

        fetched_events = list(events)
        fetched_preferences = dict(preferences)

        return {
            "user_id": user_id,
            "events": fetched_events,
            "preferences": fetched_preferences,
            "updated_at": None,
        }


event_fetcher = EventFetcherAgent()
