import os
import sys
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Ensure virtual environment packages are loaded if present (for local testing)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
venv_site = os.path.join(ROOT_DIR, "venv", "Lib", "site-packages")
if os.path.exists(venv_site):
    sys.path.insert(0, venv_site)

# Load env variables from .env file (for local development fallback)
load_dotenv()

from agent.classifier import classify_complexity

# --- Mock OpenAI Client for Offline Testing ---
class MockChoices:
    def __init__(self, content):
        self.message = type('Message', (object,), {'content': content})

class MockUsage:
    def __init__(self):
        self.total_tokens = 50

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoices(content)]
        self.usage = MockUsage()

class MockChatCompletions:
    def create(self, model, messages, temperature=0.1, max_tokens=1024):
        # Determine the category from messages
        system_content = next((m["content"] for m in messages if m["role"] == "system"), "").lower()
        user_content = next((m["content"] for m in messages if m["role"] == "user"), "")
        
        if "sentiment classification assistant" in system_content:
            content = '{"sentiment": "negative", "justification": "The review explicitly states the movie is the worst and a waste of time."}'
        elif "named entity recognition" in system_content:
            content = '{"persons": ["John Smith"], "organizations": [], "locations": ["Rome"], "dates": ["Wednesday"]}'
        elif "summarization assistant" in system_content:
            content = "The search for more efficient solar energy cells is accelerating."
        elif "math reasoning assistant" in system_content:
            content = "The shirt costs $20. A 15% discount is $3. The final price is $17."
        elif "code debugging assistant" in system_content:
            content = "The bug is using a mutable default argument list. Corrected implementation:\n```python\ndef add_to_list(val, lst=None):\n    if lst is None:\n        lst = []\n    lst.append(val)\n    return lst\n```"
        elif "code generation assistant" in system_content:
            content = "```python\ndef is_prime(n):\n    if n <= 1:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n```"
        elif "logical reasoning assistant" in system_content:
            content = "Yes, Alice is taller than Charlie because height is transitive (Alice > Bob > Charlie)."
        else:
            content = "This is a mock response for: " + user_content
            
        return MockResponse(content)

class MockOpenAI:
    def __init__(self, **kwargs):
        self.chat = type('Chat', (object,), {'completions': MockChatCompletions()})


def select_model(query: str, complexity_score: int, allowed_models: list) -> str:
    """
    Selects the best available model from allowed_models list based on
    query keywords and complexity score.
    """
    if not allowed_models:
        raise ValueError("No allowed models provided in environment variable.")

    # 1. Identify specific model groups
    # Code models (Kimi, qwen-coder, etc.)
    code_models = [m for m in allowed_models if "kimi" in m.lower() or "code" in m.lower()]
    # Large reasoning/smart models (Gemma-4-31B dense or quantized nvfp4)
    nvfp4_models = [m for m in allowed_models if "nvfp4" in m.lower()]
    gemma_31b = [m for m in allowed_models if "gemma-4-31b-it" in m.lower() and "nvfp4" not in m.lower()]
    # Smaller/cheaper/efficient models (Gemma-4-26B, minimax, etc.)
    gemma_26b = [m for m in allowed_models if "gemma-4-26b" in m.lower()]
    minimax = [m for m in allowed_models if "minimax" in m.lower()]

    # Detect code-related tasks
    code_keywords = ["code", "function", "debug", "python", "javascript", "c++", "java", "bug", "compile", "exception", "programming", "sql", "html", "css"]
    is_code_task = any(kw in query.lower() for kw in code_keywords)

    # Routing Logic:
    # A. Code-specific query
    if is_code_task:
        if code_models:
            return code_models[0]
        # Fall back to smart Gemma models if no code-specific model
        if nvfp4_models:
            return nvfp4_models[0]
        if gemma_31b:
            return gemma_31b[0]

    # B. Complex task (Complexity score >= 3) or general reasoning
    if complexity_score >= 3:
        if nvfp4_models:
            return nvfp4_models[0]
        if gemma_31b:
            return gemma_31b[0]
        if code_models:
            return code_models[0]
        return allowed_models[0]

    # C. Simple/Efficient task (Complexity score 1-2)
    else:
        if gemma_26b:
            return gemma_26b[0]
        if minimax:
            return minimax[0]
        # If nvfp4 is the only option, use it (it is also very token-efficient)
        if nvfp4_models:
            return nvfp4_models[0]
        return allowed_models[0]

def clean_json_response(text: str) -> str:
    """
    Cleans raw response to extract valid JSON payload.
    Strips markdown code fences (```json ... ```) or extracts first { and last }.
    """
    cleaned = text.strip()
    
    # Remove markdown code block wrapping if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    # If it still doesn't parse, try to locate first { and last }
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        # Attempt pattern matching
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            candidate = match.group(1)
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass
        
        # Build a safe JSON structure if parsing fails completely
        return json.dumps({
            "error": "Failed to parse structured JSON response from model.",
            "raw_response": text
        })

def get_category_config(query: str):
    """
    Detects the capability category from prompt keywords and returns
    the custom system prompt and whether JSON formatting is required.
    """
    q_lower = query.lower()

    # Regex definitions with word boundaries to avoid substring match issues
    sentiment_rx = r"\b(sentiment|emotion|positive|negative|neutral|classify sentiment|label sentiment)\b"
    ner_rx = r"\b(named entity|ner|entities|extract names|extract locations|extract organizations|extract dates)\b"
    summarize_rx = r"\b(summarize|summarise|condensation|condense|tldr|tl;dr|summary)\b"
    math_rx = r"\b(solve for|calculate|derivative|integral|arithmetic|equation|math|percentage|word problem|discount|price|costs|final price)\b|[\+\-\*\/=]"
    debug_rx = r"\b(debug|bug|fix this code|error in|syntax error|exception)\b"
    codegen_rx = r"\b(write a function|implement a|code in|program to|write a python|write a javascript|write a script|write an algorithm|function to)\b"
    logic_rx = r"\b(logic puzzle|riddle|knights and knaves|constraints|sudoku|grid|taller than|older than)\b"

    # Match in specific order of precedence
    # 1. Sentiment (JSON format required)
    if re.search(sentiment_rx, q_lower):
        system_prompt = (
            "You are a sentiment classification assistant. Analyze the text and label its sentiment. "
            "You MUST return a JSON object with exactly two keys:\n"
            "1. 'sentiment' (string, e.g. 'positive', 'negative', 'neutral')\n"
            "2. 'justification' (string, a brief explanation of why)\n"
            "Return ONLY the raw JSON object. Do not include markdown code block formatting or backticks."
        )
        return system_prompt, True

    # 2. Named Entity Recognition (JSON format required)
    elif re.search(ner_rx, q_lower):
        system_prompt = (
            "You are a Named Entity Recognition (NER) assistant. Extract all persons, organizations, locations, and dates from the text. "
            "You MUST return a JSON object with exactly these four keys mapping to lists of strings:\n"
            "1. 'persons' (list of strings)\n"
            "2. 'organizations' (list of strings)\n"
            "3. 'locations' (list of strings)\n"
            "4. 'dates' (list of strings)\n"
            "Return ONLY the raw JSON object. Do not include markdown code block formatting or backticks."
        )
        return system_prompt, True

    # 3. Code Debugging (High precedence to prevent matching '=' in code as math)
    elif re.search(debug_rx, q_lower):
        system_prompt = (
            "You are a code debugging assistant. Identify the bug in the provided code snippet, explain it in one sentence, "
            "and provide the corrected implementation. Keep code clean and explanation minimal."
        )
        return system_prompt, False

    # 4. Code Generation (High precedence to prevent matching math operators in specifications)
    elif re.search(codegen_rx, q_lower):
        system_prompt = (
            "You are a code generation assistant. Write correct, well-structured code based on the specification. "
            "Provide only the code and minimal documentation comments. Avoid conversational introductions or conclusions."
        )
        return system_prompt, False

    # 5. Summarization
    elif re.search(summarize_rx, q_lower):
        system_prompt = (
            "You are a summarization assistant. Condense the text according to the user instructions. "
            "Be extremely direct, precise, and concise. Do not include introductory text like 'Here is the summary:'."
        )
        return system_prompt, False

    # 6. Logical Reasoning
    elif re.search(logic_rx, q_lower):
        system_prompt = (
            "You are a logical reasoning assistant. Solve the constraint-based puzzle. Satisfy all conditions. "
            "Keep explanations extremely brief."
        )
        return system_prompt, False

    # 7. Mathematical Reasoning
    elif re.search(math_rx, q_lower):
        system_prompt = (
            "You are a math reasoning assistant. Solve the user's math problem. Show step-by-step logic. "
            "Keep explanations brief to minimize token usage. End your response with the final answer clearly marked."
        )
        return system_prompt, False

    # 8. Factual Knowledge (Default)
    else:
        system_prompt = (
            "You are a general-purpose AI assistant. Answer the user query accurately and directly. "
            "Avoid conversational fluff to conserve tokens."
        )
        return system_prompt, False

def main():
    print("--- Starting CodeRouter AI Batch Runner ---")

    # 1. Read environment variables
    api_key = os.environ.get("FIREWORKS_API_KEY")
    base_url = os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")
    allowed_models_env = os.environ.get("ALLOWED_MODELS")
    mock_inference = os.environ.get("MOCK_INFERENCE", "false").lower() == "true"

    if not api_key and not mock_inference:
        print("[error] FIREWORKS_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    if not allowed_models_env:
        print("[error] ALLOWED_MODELS environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    allowed_models = [m.strip() for m in allowed_models_env.split(",") if m.strip()]
    if not allowed_models:
        print("[error] ALLOWED_MODELS contains no valid model IDs.", file=sys.stderr)
        sys.exit(1)

    print(f"Allowed models: {allowed_models}")
    print(f"Using base URL: {base_url}")
    print(f"Mock inference mode: {mock_inference}")

    # 2. Read tasks from /input/tasks.json
    input_path = "/input/tasks.json"
    
    # Fallback to local inputs/tasks.json for testing if path does not exist
    if not os.path.exists(input_path):
        input_path = os.path.join(ROOT_DIR, "inputs", "tasks.json")
        print(f"Evaluation path /input/tasks.json not found. Falling back to local development path: {input_path}")

    if not os.path.exists(input_path):
        print(f"[error] Task input file does not exist at {input_path}.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"[error] Failed to parse task input file as JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(tasks, list):
        print("[error] Task input JSON must be a list of task objects.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(tasks)} tasks to process.")

    # 3. Initialize Fireworks API OpenAI Client
    # Ensure client uses the base_url routed through the harness proxy
    if mock_inference:
        print("[info] Using Mock OpenAI Client for testing/validation.")
        client = MockOpenAI()
    else:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    results = []

    # 4. Process each task
    for idx, task in enumerate(tasks):
        task_id = task.get("task_id")
        prompt = task.get("prompt", "")

        if not task_id:
            print(f"[warning] Skipping task at index {idx} due to missing task_id.")
            continue

        print(f"[{idx + 1}/{len(tasks)}] Processing task {task_id}...")

        # A. Local Complexity Classification (TF-IDF + Ridge Regression, no Ollama)
        complexity = classify_complexity(prompt)
        print(f"  -> Complexity score: {complexity}")

        # B. Model Selection
        selected_model = select_model(prompt, complexity, allowed_models)
        print(f"  -> Selected model: {selected_model}")

        # C. Category Detection and Prompt Preparation
        system_prompt, is_json_task = get_category_config(prompt)
        
        # D. Execute API call with error handling and retry
        answer = ""
        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for highly precise and predictable output
                max_tokens=1024
            )
            raw_answer = response.choices[0].message.content
            
            # E. Response Sanitization (especially JSON formatting)
            if is_json_task:
                answer = clean_json_response(raw_answer)
            else:
                answer = raw_answer.strip()

        except Exception as e:
            print(f"  -> API call failed for task {task_id}: {e}", file=sys.stderr)
            # Safe fallback if model fails
            if is_json_task:
                answer = json.dumps({"error": f"Model inference failed: {str(e)}"})
            else:
                answer = f"Inference error: {str(e)}"

        results.append({
            "task_id": task_id,
            "answer": answer
        })

    # 5. Write results to /output/results.json
    output_path = "/output/results.json"
    
    # Fallback to local outputs/results.json for testing if path does not exist
    if not os.path.exists(os.path.dirname(output_path)):
        output_path = os.path.join(ROOT_DIR, "outputs", "results.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"Evaluation path /output/ not found. Writing to local development path: {output_path}")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Successfully wrote results to {output_path}")
    except Exception as e:
        print(f"[error] Failed to write results.json: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- Batch Runner Completed Successfully ---")
    sys.exit(0)

if __name__ == "__main__":
    main()
