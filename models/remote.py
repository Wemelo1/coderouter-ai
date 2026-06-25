import os
from openai import OpenAI, APIStatusError, APIConnectionError

FIREWORKS_MODEL = "accounts/fireworks/models/llama4-maverick-instruct-basic"
COST_PER_1K_TOKENS = 0.0009  # Fireworks AI pricing (USD)


class RemoteModelError(Exception):
    """Raised when the remote (Fireworks) model call fails for any reason."""
    pass


def call_remote_model(query: str) -> dict:
    """
    Sends query to Fireworks AI via OpenAI-compatible API.
    Returns response, tokens used, and actual cost incurred.

    Raises RemoteModelError if the call fails (billing, rate limit,
    network issue, etc.) so callers can catch it and fall back.
    """
    client = OpenAI(
        api_key=os.getenv("FIREWORKS_API_KEY"),
        base_url="https://api.fireworks.ai/inference/v1"
    )

    try:
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
    except APIStatusError as e:
        # e.g. account suspended, spending limit reached, invalid request
        raise RemoteModelError(f"Fireworks API rejected the request: {e}") from e
    except APIConnectionError as e:
        # e.g. no internet, DNS failure, Fireworks is down
        raise RemoteModelError(f"Could not reach Fireworks API: {e}") from e
    except Exception as e:
        # catch-all so callers can rely on RemoteModelError consistently
        raise RemoteModelError(f"Unexpected error calling Fireworks API: {e}") from e

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
