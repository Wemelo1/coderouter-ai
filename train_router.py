import os
import sys

# Load venv packages
venv_site = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv", "Lib", "site-packages"))
if os.path.exists(venv_site):
    sys.path.insert(0, venv_site)

import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge

# --- Lists of components for template-driven query generation ---

FACTUAL_VERBS = [
    "who is", "what is", "who was", "where is", "tell me about", 
    "explain the concept of", "when did", "who invented", 
    "what is the capital of", "how high is", "what is the color of",
    "what is the formula for", "how far is", "what is the speed of"
]

FACTUAL_SUBJECTS = [
    "the president of oman", "the capital of France", "the color of an apple", 
    "the creator of python", "the speed of light", "mount everest", 
    "the founder of Microsoft", "the distance to Mars", "quantum mechanics", 
    "photosynthesis", "the internet", "the printing press", "the roman empire", 
    "hamlet", "the Mona Lisa", "the black death", "gravity", "the industrial revolution", 
    "dna replication", "mitosis", "artificial intelligence", "the atomic bomb", 
    "world war 2", "the solar system", "the milky way", "the color of grass", 
    "the speed of sound", "water boiling point", "the human brain", 
    "the declaration of independence", "the Eiffel tower", "the Great Wall of China", 
    "the amazon rainforest", "the Sahara desert", "the Pacific ocean", 
    "the theory of relativity", "the cold war", "the French revolution", 
    "the magna carta", "the Rosetta stone", "the pyramids of Giza", 
    "the taj mahal", "the Colosseum", "the grand canyon", "the deep sea", 
    "the human heart", "the periodic table", "the element carbon", 
    "the distance to the moon", "the depth of mariana trench", 
    "the function of chlorophyll", "the role of ribosomes", 
    "the structure of an atom", "the origin of species", "the concept of evolution"
]

LANGUAGES = [
    "Python", "JavaScript", "Go", "Rust", "C++", "Java", "HTML", "SQL", "bash", "TypeScript"
]

CODING_TRIVIAL_TOPICS = [
    "variable declaration", "string concatenation", "comment syntax", 
    "arithmetic operators", "if statement", "while loop", "for loop", 
    "list index", "dictionary lookup", "function declaration"
]

CODING_TRIVIAL_TEMPLATES = [
    "how to do {} in {}", "syntax of {} in {}", "example of {} in {}", 
    "explain {} in {}", "write a simple {} in {}"
]

ALGORITHMS = [
    "binary search", "bubble sort", "quick sort", "merge sort", 
    "factorial using recursion", "fibonacci sequence", "string reversal", 
    "prime number check", "armstrong number check", "palindrome check", 
    "matrix multiplication", "finding the maximum in a list", 
    "removing duplicates from list", "binary tree traversal", "graph depth first search"
]

ALGORITHM_TEMPLATES = [
    "write a function for {} in {}", "implement {} in {}", 
    "how to code {} in {}", "can you write a {} script in {}"
]

COMPLEX_TASKS = [
    "REST API", "JWT authentication middleware", "database schema", 
    "file upload handler", "websocket connection", "multithreaded web scraper", 
    "OAuth2 login integration", "unit tests", "dockerfile", "redis caching layer"
]

COMPLEX_TEMPLATES = [
    "build a {} using {}", "implement a {} in {}", 
    "write code for a {} using {}", "how to create a {} with {}"
]

EXPERT_TASKS = [
    "microservices architecture", "database query optimization", 
    "load balancer configuration", "fault-tolerant clustering", 
    "auto-scaling setup", "distributed transaction handling", 
    "rate limiting middleware", "kubernetes deployment", 
    "performance bottleneck profiling", "zero-downtime deployment pipeline"
]

EXPERT_SYSTEM_CONTEXTS = [
    "for an e-commerce platform", "handling 10 million transactions", 
    "serving 100k requests per second", "on AWS", "for a real-time messaging app", 
    "using Kafka and microservices", "with horizontal scaling", 
    "in a multi-region setup", "for a financial system", "under heavy load"
]

EXPERT_TEMPLATES = [
    "how to design a {} {}", 
    "explain the best way to optimize a {} {}", 
    "write a system architecture plan for a {} {}"
]

def generate_dataset():
    dataset = []
    
    # 1. Generate Factual/General Queries (Complexity 1.0)
    for verb in FACTUAL_VERBS:
        for subj in FACTUAL_SUBJECTS:
            query = f"{verb} {subj}"
            dataset.append((query, 1.0))
            
    # 2. Generate Trivial Coding Queries (Complexity 1.5 - 2.0)
    for topic in CODING_TRIVIAL_TOPICS:
        for lang in LANGUAGES:
            for temp in CODING_TRIVIAL_TEMPLATES:
                query = temp.format(topic, lang)
                dataset.append((query, 1.5))
                
    # 3. Generate Moderate Algorithmic Queries (Complexity 3.0)
    for algo in ALGORITHMS:
        for lang in LANGUAGES:
            for temp in ALGORITHM_TEMPLATES:
                query = temp.format(algo, lang)
                dataset.append((query, 3.0))
                
    # 4. Generate Complex Coding Queries (Complexity 4.0)
    for task in COMPLEX_TASKS:
        for lang in LANGUAGES:
            for temp in COMPLEX_TEMPLATES:
                query = temp.format(task, lang)
                dataset.append((query, 4.0))
                
    # 5. Generate Expert Architecture/Optimization Queries (Complexity 5.0)
    for task in EXPERT_TASKS:
        for ctx in EXPERT_SYSTEM_CONTEXTS:
            for temp in EXPERT_TEMPLATES:
                query = temp.format(task, ctx)
                dataset.append((query, 5.0))
                
    return dataset

def train():
    dataset = generate_dataset()
    print(f"Generated {len(dataset)} high-quality samples using semantic templates.")
    
    X = [item[0] for item in dataset]
    y = [item[1] for item in dataset]
    
    # Train vectorizer
    # Using character and word n-grams to make it extremely robust to spelling/token shifts
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, lowercase=True)
    X_vec = vectorizer.fit_transform(X)
    
    # Model: Ridge Regression (continuous scores 1.0 to 5.0)
    model = Ridge(alpha=0.5)
    model.fit(X_vec, y)
    
    # Save files
    with open("router_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("router_model.pkl", "wb") as f:
        pickle.dump(model, f)
        
    print("Distilled complexity routing model trained and saved successfully.")
    
    # Run test suite
    test_queries = [
        "what is the colour of apple",
        "who is the president of oman",
        "write a python function to add two numbers",
        "write a binary search algorithm",
        "build a REST API with authentication",
        "design a microservices architecture for an e-commerce platform"
    ]
    
    print("\n--- Validation Inference ---")
    for q in test_queries:
        q_vec = vectorizer.transform([q])
        pred = model.predict(q_vec)[0]
        score = max(1, min(5, int(round(pred))))
        print(f"Query: '{q}' -> Raw Score: {pred:.2f} (Final: {score})")

if __name__ == "__main__":
    train()
