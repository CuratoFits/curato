from typing import Any

from ..state.userState import UserState


class EventFetcherAgent:
    """Minimal event fetcher node scaffold for LangGraph.

    This node is intended to read incoming event payloads and update the
    user state with the newest event list and preferences.
    """

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
