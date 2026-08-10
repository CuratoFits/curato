from __future__ import annotations

from typing import Any

from ..agents.event_fetcher import event_fetcher
from ..state.userState import UserState

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover - optional dependency during setup
    StateGraph = None
    END = START = None


class GraphBuilder:
    def build(self) -> Any:
        if StateGraph is None:
            return {
                "entry": event_fetcher,
                "nodes": [event_fetcher],
                "edges": [],
            }

        workflow = StateGraph(UserState)
        workflow.add_node("event_fetcher", event_fetcher)
        workflow.add_edge(START, "event_fetcher")
        workflow.add_edge("event_fetcher", END)
        return workflow.compile()


graph_builder = GraphBuilder()
