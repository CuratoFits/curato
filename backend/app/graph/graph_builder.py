from __future__ import annotations

from typing import Any

from ..agents.event_fetcher import event_fetcher
from ..agents.userBehaviorAgent import UserBehaviorAgent
from ..agents.vectorDB_search_agent import VectorDBSearchAgent as vectorDB_search_agent
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
                "nodes": [event_fetcher, UserBehaviorAgent, vectorDB_search_agent],
                "edges": [],
            }

        workflow = StateGraph(UserState)
        workflow.add_node("event_fetcher", event_fetcher)
        workflow.add_node("user_behavior_agent", UserBehaviorAgent)
        workflow.add_node("vector_db_search_agent", vectorDB_search_agent)
        workflow.add_edge(START, "event_fetcher")
        workflow.add_edge("event_fetcher", "user_behavior_agent")
        workflow.add_edge("user_behavior_agent", "vector_db_search_agent")
        workflow.add_edge("vector_db_search_agent", END)
        return workflow.compile()


graph_builder = GraphBuilder()
