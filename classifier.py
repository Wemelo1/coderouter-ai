import ollama

def classify_complexity(query: str) -> int:
    """
    Uses local Ollama model to score task complexity 1-5.
    Runs locally so classification is always FREE.
    
    1 = Trivial: definitions, naming, simple syntax, general/factual queries
    2 = Simple: basic functions, short explanations, minor fixes
    3 = Moderate: multi-step logic, debugging small snippets
    4 = Complex: full implementations, architecture, algorithms
    5 = Expert: system design, optimization, advanced patterns
    """
    prompt = f"""You are a task complexity classifier for coding and general queries. Your ONLY job is to output a single digit from 1 to 5.

SCORING RULES:
1 = Trivial (general knowledge, what is a variable, rename this, fix typo, factual questions)
2 = Simple (write hello world, explain a loop, basic syntax fix, simple non-coding queries)
3 = Moderate (write a function with logic, debug a snippet, explain an algorithm)
4 = Complex (build a REST API, implement a data structure, write a class with multiple methods)
5 = Expert (system architecture, design patterns, performance optimization, security implementation)

CRITICAL RULE:
- If the query is a general knowledge question, factual query, or non-coding question (e.g. "who invented the GPU", "what is the capital of France"), it MUST be classified as 1 or 2. These do not require complex coding reasoning.

EXAMPLES:
"what is a list in python" → 1
"who invented the GPU" → 1
"write a hello world program" → 1
"explain what recursion is" → 2
"write a function to reverse a string" → 2
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
        # Find the first digit in the response to be robust
        for char in raw:
            if char.isdigit():
                score = int(char)
                return max(1, min(5, score))
        return 3 # Default to moderate if no digit found
    except Exception as e:
        print(f"[warning] Classification failed: {e}")
        return 3  # Default to moderate if classification fails
