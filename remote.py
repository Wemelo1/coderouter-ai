import os
from openai import OpenAI

FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/glm-5p2")
COST_PER_1K_TOKENS = 0.002  # Fireworks AI pricing (USD, blended rate for GLM-5.2)

def call_remote_model(query: str) -> dict:
    """
    Sends query to Fireworks AI via OpenAI-compatible API.
    Raises exception if remote is unavailable or times out.
    """
    client = OpenAI(
        api_key=os.getenv("FIREWORKS_API_KEY"),
        base_url="https://api.fireworks.ai/inference/v1",
        timeout=20.0
    )

    response = client.chat.completions.create(
        model=FIREWORKS_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert coding assistant. Provide detailed, accurate answers."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        max_tokens=1024
    )

    answer = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    cost_incurred = (tokens_used / 1000) * COST_PER_1K_TOKENS

    return {
        "response": answer,
        "model_used": FIREWORKS_MODEL,
        "tokens": tokens_used,
        "cost_saved": 0.0,
        "cost_incurred": round(cost_incurred, 6)
    }