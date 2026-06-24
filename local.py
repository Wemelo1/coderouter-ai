import ollama

LOCAL_MODEL = "qwen2.5-coder:1.5b"

# Approximate cost of equivalent remote call (in USD per 1K tokens)
REMOTE_COST_PER_1K = 0.0009  # Fireworks AI pricing

def call_local_model(query: str) -> dict:
    """
    Sends query to local Ollama model.
    Returns response text, estimated tokens, and cost saved.
    """
    response = ollama.chat(
        model=LOCAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful coding assistant. Answer clearly and concisely."
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )

    answer = response["message"]["content"]
    # Estimate tokens (Ollama doesn't always return exact count)
    estimated_tokens = len(answer.split()) * 1.3
    cost_saved = (estimated_tokens / 1000) * REMOTE_COST_PER_1K

    return {
        "response": answer,
        "model_used": LOCAL_MODEL,
        "tokens": int(estimated_tokens),
        "cost_saved": round(cost_saved, 6),
        "cost_incurred": 0.0
    }
