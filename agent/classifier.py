import ollama

def classify_complexity(query: str) -> int:
    """
    Uses local Ollama model to score task complexity 1-5.
    Runs locally so classification is always FREE.
    
    1 = Trivial: definitions, naming, simple syntax
    2 = Simple: basic functions, short explanations, minor fixes
    3 = Moderate: multi-step logic, debugging small snippets
    4 = Complex: full implementations, architecture, algorithms
    5 = Expert: system design, optimization, advanced patterns
    """
    prompt = f"""You are a coding task complexity classifier. Your ONLY job is to output a single digit from 1 to 5.

SCORING RULES:
1 = Trivial (what is a variable, rename this, fix typo)
2 = Simple (write hello world, explain a loop, basic syntax fix, simple algorithmic logic like checking primes/Armstrong numbers)
3 = Moderate (write a function with custom business logic, debug a small snippet, explain an advanced algorithm)
4 = Complex (build a REST API, implement a data structure, write a class with multiple methods)
5 = Expert (system architecture, design patterns, performance optimization, security implementation)

EXAMPLES:
"what is a list in python" → 1
"write a hello world program" → 1
"explain what recursion is" → 2
"write a function to reverse a string" → 2
"check if a number is prime or Armstrong" → 2
"debug why my loop runs infinitely" → 3
"write a binary search algorithm" → 3
"build a REST API with authentication" → 4
"implement a linked list with insert and delete" → 4
"design a microservices architecture for an e-commerce app" → 5
"optimize this database query for 10 million records" → 5

OUTPUT RULES:
- Output ONLY a single digit: 1, 2, 3, 4, or 5
- No explanation, no punctuation, no extra text

Query to classify: {query}
Score:"""

    try:
        response = ollama.chat(
            model="qwen2.5-coder:1.5b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0}
        )
        raw = response["message"]["content"].strip()
        score = int(raw[0])
        return max(1, min(5, score))
    except Exception:
        return 3  # Default to moderate if classification fails