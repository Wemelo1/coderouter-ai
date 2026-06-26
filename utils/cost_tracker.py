from datetime import datetime

# In-memory session log (resets on app restart)
session_log = []

def log_query(query: str, complexity: int, model_choice: str, result: dict):
    """Logs each query with routing decision and cost data."""
    session_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "query": query[:60] + "..." if len(query) > 60 else query,
        "complexity": complexity,
        "routed_to": model_choice,
        "model": result["model_used"],
        "tokens": result["tokens"],
        "cost_saved": result["cost_saved"],
        "cost_incurred": result["cost_incurred"]
    })

def get_session_stats() -> dict:
    """Returns total stats for the current session."""
    if not session_log:
        return {"total_queries": 0, "local_queries": 0,
                "remote_queries": 0, "total_saved": 0.0, "total_spent": 0.0}

    # Count fallback as local since it ran on local model
    local_count = sum(1 for l in session_log if "local" in l["routed_to"])
    remote_count = sum(1 for l in session_log if l["routed_to"] == "remote")

    return {
        "total_queries": len(session_log),
        "local_queries": local_count,
        "remote_queries": remote_count,
        "total_saved": round(sum(l["cost_saved"] for l in session_log), 6),
        "total_spent": round(sum(l["cost_incurred"] for l in session_log), 6)
    }