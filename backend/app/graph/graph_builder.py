from __future__ import annotations

from typing import Any
from ..agents.userBehaviorAgent import UserBehaviorAgent
from ..agents.vectorDB_search_agent import VectorDBSearchAgent as vectorDB_search_agent
from ..agents.DL_ranker import dl_ranker
from ..state.userState import UserState
from ..agents.demographicFilter import DemographicFilter
from ..agents.collaborative_filter import Collaborative_filter

try:
    from langgraph.graph import END, START, StateGraph
except Exception:  # pragma: no cover - optional dependency during setup
    StateGraph = None
    END = START = None


class GraphBuilder:
    def build(self) -> Any:
        if StateGraph is None:
            return {
                "entry": UserBehaviorAgent,
                "nodes": [UserBehaviorAgent, vectorDB_search_agent, DemographicFilter, Collaborative_filter, dl_ranker],
                "edges": [],
            }

        workflow = StateGraph(UserState)
        workflow.add_node("user_behavior_agent", UserBehaviorAgent)
        workflow.add_node("vector_db_search_agent", vectorDB_search_agent)
        workflow.add_node("demographic_filter", DemographicFilter)
        workflow.add_node("collaborative_filter", Collaborative_filter)
        workflow.add_node("dl_ranker", dl_ranker)
        
        workflow.add_edge(START, "user_behavior_agent")
        workflow.add_edge("user_behavior_agent", "vector_db_search_agent")
        workflow.add_edge("user_behavior_agent", "demographic_filter")
        workflow.add_edge("user_behavior_agent", "collaborative_filter")
        workflow.add_edge("vector_db_search_agent", "dl_ranker")
        workflow.add_edge("demographic_filter", "dl_ranker")
        workflow.add_edge("collaborative_filter", "dl_ranker")
        workflow.add_edge("dl_ranker", END)
        return workflow.compile()


graph_builder = GraphBuilder()
