import os
import sys
import pickle
import ollama

# Set up paths for site-packages in virtual environment
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site = os.path.join(ROOT_DIR, "venv", "Lib", "site-packages")
if os.path.exists(venv_site):
    sys.path.insert(0, venv_site)

# Path to trained model files
VECTORIZER_PATH = os.path.join(ROOT_DIR, "router_vectorizer.pkl")
MODEL_PATH = os.path.join(ROOT_DIR, "router_model.pkl")

def classify_complexity(query: str) -> int:
    """
    Classifies task complexity 1-5.
    Tries to load and use the local distilled machine learning model.
    Falls back to zero-shot Ollama qwen2.5-coder if model files are missing.
    """
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(MODEL_PATH):
        try:
            with open(VECTORIZER_PATH, "rb") as f:
                vectorizer = pickle.load(f)
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)

            # Predict score using TF-IDF and Ridge regression
            vec = vectorizer.transform([query])
            pred = model.predict(vec)[0]
            # Clip predicted score between 1 and 5
            score = max(1, min(5, int(round(pred))))
            return score
        except Exception as e:
            print(f"[warning] Distilled router failed: {e}. Falling back to Ollama.")

    # Fallback to local Ollama zero-shot complexity classification
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