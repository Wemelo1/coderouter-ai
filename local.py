import ollama
from dotenv import load_dotenv
load_dotenv()

LOCAL_MODEL = "gemma2:2b"
REMOTE_COST_PER_1K = 0.0009

def call_local_model(query: str) -> dict:
    """
    Sends query to local Ollama model.
    Falls back to remote model if Ollama is unavailable.
    """
    try:
        response = ollama.chat(
            model=LOCAL_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Answer clearly and concisely."
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        answer = response["message"]["content"]
        estimated_tokens = len(answer.split()) * 1.3
        cost_saved = (estimated_tokens / 1000) * REMOTE_COST_PER_1K
        return {
            "response": answer,
            "model_used": LOCAL_MODEL,
            "tokens": int(estimated_tokens),
            "cost_saved": round(cost_saved, 6),
            "cost_incurred": 0.0
        }

    except Exception as e:
        # Ollama unavailable — fall back to remote model
        print(f"[fallback] Local model unavailable: {e}. Routing to remote.")
        from remote import call_remote_model
        result = call_remote_model(query)
        result["model_used"] = f"remote-fallback ({result['model_used']})"
        return result