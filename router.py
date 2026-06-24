import os

COMPLEXITY_THRESHOLD = int(os.getenv("COMPLEXITY_THRESHOLD", 2))

def route_query(complexity_score: int) -> str:
    """
    Decides which model to use based on complexity score.
    Score <= threshold → local (free, Ollama)
    Score >  threshold → remote (costs credits, Fireworks AI)
    """
    if complexity_score <= COMPLEXITY_THRESHOLD:
        return "local"
    else:
        return "remote"
