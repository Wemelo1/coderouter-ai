from typing import TypedDict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from agent.classifier import classify_complexity
from agent.router import route_query
from models.local import call_local_model
from models.remote import call_remote_model
from utils.cost_tracker import log_query

load_dotenv()

# ─── State Definition ────────────────────────────────────────────────────────

class AgentState(TypedDict):
    query: str
    complexity_score: int
    model_choice: str
    response: str
    model_used: str
    tokens: int
    cost_saved: float
    cost_incurred: float

# ─── Node Functions ───────────────────────────────────────────────────────────

def classifier_node(state: AgentState) -> AgentState:
    """Scores the complexity of the incoming query."""
    score = classify_complexity(state["query"])
    return {**state, "complexity_score": score}

def router_node(state: AgentState) -> AgentState:
    """Decides local or remote based on complexity score."""
    choice = route_query(state["complexity_score"])
    return {**state, "model_choice": choice}

def local_node(state: AgentState) -> AgentState:
    """Handles query with local Ollama model."""
    result = call_local_model(state["query"])
    log_query(state["query"], state["complexity_score"], "local", result)
    return {
        **state,
        "response": result["response"],
        "model_used": result["model_used"],
        "tokens": result["tokens"],
        "cost_saved": result["cost_saved"],
        "cost_incurred": result["cost_incurred"]
    }

def remote_node(state: AgentState) -> AgentState:
    """Handles query with Fireworks AI remote model."""
    result = call_remote_model(state["query"])
    log_query(state["query"], state["complexity_score"], "remote", result)
    return {
        **state,
        "response": result["response"],
        "model_used": result["model_used"],
        "tokens": result["tokens"],
        "cost_saved": result["cost_saved"],
        "cost_incurred": result["cost_incurred"]
    }

# ─── Routing Logic ────────────────────────────────────────────────────────────

def decide_route(state: AgentState) -> str:
    return state["model_choice"]  # Returns "local" or "remote"

# ─── Build Graph ──────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classifier", classifier_node)
    graph.add_node("router", router_node)
    graph.add_node("local", local_node)
    graph.add_node("remote", remote_node)

    graph.set_entry_point("classifier")
    graph.add_edge("classifier", "router")
    graph.add_conditional_edges(
        "router",
        decide_route,
        {"local": "local", "remote": "remote"}
    )
    graph.add_edge("local", END)
    graph.add_edge("remote", END)

    return graph.compile()

# Compiled graph — import this in app.py
coderouter = build_graph()
