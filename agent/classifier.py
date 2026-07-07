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
    prompt = f"""You are a task complexity classifier. Your ONLY job is to output a single digit from 1 to 5.

SCORING RULES:
1 = Trivial (simple factual questions, basic sentiment lookup, variable definition, rename this, fix typo)
2 = Simple (short summarization, basic arithmetic/math reasoning, simple entity extraction, explain recursion/loops)
3 = Moderate (standard logic puzzles, multi-entity extraction, write a function, debug small snippets, explain algorithms)
4 = Complex (long text summarization, multi-step math/logic reasoning, build a REST API, implement data structures)
5 = Expert (complex logic/math puzzles, system architecture design, performance profiling, advanced code optimization)

EXAMPLES:
"what is the capital of France" → 1
"is this review positive: 'I love this product!'" → 1
"what is the definition of a list in python" → 1
"summarize the main point of a 1-paragraph text" → 2
"what is 23 * 45 + 12" → 2
"extract the city from: 'I live in Paris.'" → 2
"explain recursion in Python" → 2
"A is taller than B, B is taller than C. Who is tallest?" → 3
"extract all names and locations from this 3-paragraph story" → 3
"write a function to reverse a string" → 2
"debug why my quicksort loop runs infinitely" → 3
"solve for x: 3x^2 + 5x - 2 = 0" → 4
"summarize this 5-page research paper abstract" → 4
"build a Flask REST API with authentication and SQLite" → 4
"design a distributed database replication strategy for 10M users" → 5
"prove that the square root of 2 is irrational" → 5

OUTPUT RULES:
- Output ONLY a single digit: 1, 2, 3, 4, or 5
- No explanation, no punctuation, no extra text

Query to classify: {query}
Score:"""

    try:
        response = ollama.chat(
            model="gemma2:2b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0}
        )
        raw = response["message"]["content"].strip()
        score = int(raw[0])
        return max(1, min(5, score))
    except Exception:
        return 3  # Default to moderate if classification fails