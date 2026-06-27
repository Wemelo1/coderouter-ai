import ollama

def classify_complexity(query: str) -> int:
    """
<<<<<<< HEAD
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
=======
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
2 = Simple (write hello world, explain a loop, basic syntax fix)
3 = Moderate (write a function with logic, debug a small snippet, explain an algorithm)
4 = Complex (build a REST API, implement a data structure, write a class with multiple methods)
5 = Expert (system architecture, design patterns, performance optimization, security implementation)

EXAMPLES:
"what is a list in python" → 1
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
>>>>>>> 6a39a5ecb65245f7c79e3584624fad5b5bb47fc9
Score:"""

    try:
        response = ollama.chat(
            model="qwen2.5-coder:1.5b",
<<<<<<< HEAD
            options={"temperature": 0},
            messages=[{"role": "user", "content": prompt}]
        )
        score = int(response["message"]["content"].strip()[0])
        return max(1, min(5, score))  # Clamp between 1-5
    except Exception:
        return 3  # Default to moderate if classification fails
=======
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0}
        )
        raw = response["message"]["content"].strip()
        score = int(raw[0])
        return max(1, min(5, score))
    except Exception:
        return 3  # Default to moderate if classification fails
>>>>>>> 6a39a5ecb65245f7c79e3584624fad5b5bb47fc9
