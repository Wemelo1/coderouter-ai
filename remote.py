import os
from openai import OpenAI

FIREWORKS_MODEL = "accounts/fireworks/models/llama-v3p1-8b-instruct"
COST_PER_1K_TOKENS = 0.0009  # Fireworks AI pricing (USD)

def call_remote_model(query: str) -> dict:
    """
    Sends query to Fireworks AI via OpenAI-compatible API.
    Falls back to local Ollama model if remote is unavailable or times out.
    """
    try:
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

    except Exception as e:
        # Fallback to local model if remote fails or times out
        import ollama as ol
        fallback_response = ol.chat(
            model="qwen2.5-coder:1.5b",
            messages=[
                {"role": "system", "content": "You are an expert coding assistant."},
                {"role": "user", "content": query}
            ]
        )
        answer = fallback_response["message"]["content"]

        # Calculate what we SAVED by not using remote
        estimated_tokens = len(answer.split()) * 1.3
        cost_saved = round((estimated_tokens / 1000) * COST_PER_1K_TOKENS, 6)

        note = "\n\n> ⚠️ *Remote model unavailable (network timeout). Answered locally as fallback.*"
        return {
            "response": answer + note,
            "model_used": "qwen2.5-coder:1.5b (fallback)",
            "tokens": int(estimated_tokens),
            "cost_saved": cost_saved,
            "cost_incurred": 0.0
        }