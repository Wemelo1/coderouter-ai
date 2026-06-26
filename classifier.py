import ollama

def classify_complexity(query: str) -> int:
    """
    Uses local Ollama model to score task complexity from 1-5.
    1-2 = Simple (syntax fix, naming, explanation)
    3-5 = Complex (generation, debugging, architecture)
    Runs locally so classification is always FREE.
    """
    prompt = f"""You are a task complexity classifier for coding questions.
Score the following coding query on a scale of 1 to 5.

1 = Very simple (rename variable, fix typo, basic syntax)
2 = Simple (short explanation, basic logic, small fix)
3 = Moderate (write a function, debug a snippet)
4 = Complex (design a module, debug tricky logic)
5 = Very complex (system architecture, multi-step generation)

Reply with ONLY a single number between 1 and 5. Nothing else.

Query: {query}
Score:"""

    try:
        response = ollama.chat(
            model="qwen2.5-coder:1.5b",
            options={"temperature": 0},
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0}
        )
        score = int(response["message"]["content"].strip()[0])
        return max(1, min(5, score))  # Clamp between 1-5
    except Exception:
        return 3  # Default to moderate if classification fails
