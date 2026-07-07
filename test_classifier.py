import sys
import os

# Add root directory to path to test classifier module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.classifier import classify_complexity

TEST_CASES = [
    "what is the colour of apple",
    "who is the president of oman",
    "is this movie good or bad",
    "summarize Mount Everest in one sentence",
    "extract locations from: Alice visited Paris",
    "solve for x: 3x + 5 = 20",
    "solve this logic puzzle: A is older than B, B is older than C. Who is older?",
    "explain what list in python is",
    "write a python function to add two numbers",
    "write a binary search algorithm",
    "build a REST API with JWT authentication",
    "design a microservices architecture for an e-commerce platform"
]

print("--- Running Classifier Test Suite ---")
for q in TEST_CASES:
    score = classify_complexity(q)
    print(f"Query: '{q}' -> Complexity Score: {score}")
