import os
import sys
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge

# Load venv packages
venv_site = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv", "Lib", "site-packages"))
if os.path.exists(venv_site):
    sys.path.insert(0, venv_site)

# --- 1. Factual Q&A ---
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

# --- 2. Coding (Trivial, Moderate, Complex, Expert) ---
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

# --- 3. Sentiment Analysis ---
SENTIMENT_ADJECTIVES = [
    "good", "bad", "amazing", "terrible", "awful", "great", "excellent", "horrible",
    "wonderful", "disappointing", "fantastic", "poor", "outstanding", "frustrating"
]
SENTIMENT_NOUNS = [
    "movie", "book", "product", "experience", "food", "service", "hotel", "game",
    "delivery", "performance", "interface", "support", "design", "quality"
]
SENTIMENT_TEMPLATES = [
    "is this review positive or negative: '{}'",
    "classify the sentiment of this: '{}'",
    "what is the sentiment of '{}'",
    "would you say this review is positive, neutral, or negative? '{}'",
    "identify the emotion behind: '{}'"
]

# --- 4. Summarization ---
SUMMARIZATION_SUBJECTS = [
    "the history of the printing press", "how photosynthesis works", "the discovery of gravity",
    "the causes of the French Revolution", "how the internet operates", "the structure of DNA",
    "the lifecycle of a star", "the main features of quantum mechanics", "the rise of the Roman Empire",
    "the role of the frontal lobe", "the global water cycle", "plate tectonics and earthquakes"
]
SUMMARIZATION_TEMPLATES_EASY = [
    "summarize this in one sentence: {}",
    "write a very brief summary of {}",
    "give a 1-sentence recap of {}",
    "summarize the main point of {}"
]
SUMMARIZATION_TEMPLATES_HARD = [
    "provide a comprehensive summary of {}",
    "explain and summarize the key arguments of {}",
    "write a detailed tl;dr for the following concept: {}",
    "analyze and summarize the historical significance of {}"
]

# --- 5. Named Entity Recognition (NER) ---
NER_TEMPLATES = [
    "extract the names and locations from: '{}'",
    "find all organizations in the text: '{}'",
    "perform named entity recognition on this: '{}'",
    "list the entities (people, places, dates) in: '{}'",
    "identify the geographical locations mentioned in: '{}'"
]
NER_SAMPLES = [
    "Alice visited Paris last summer.", "Google was founded in California by Larry Page.",
    "Bob went to Tokyo in 2025.", "Microsoft announced a new office in London.",
    "Charlie works at Tesla in Texas.", "The United Nations is headquartered in New York."
]

# --- 6. Math Reasoning ---
MATH_TRIVIAL = [
    "what is 2 + 2", "calculate 15 * 8", "what is 100 / 4", "solve 45 - 19", "what is 9 squared"
]
MATH_EASY = [
    "what is 234 * 45 + 12", "solve for x: 3x + 5 = 20", "find the area of a circle with radius 5",
    "what is the square root of 144", "calculate the average of 10, 20, 30, and 40"
]
MATH_MODERATE = [
    "solve the system of equations: 2x + y = 10 and x - y = 2", "find the derivative of x^2 + 3x + 5",
    "what is the probability of flipping two heads in a row", "calculate the log base 10 of 1000",
    "solve for x: x^2 - 5x + 6 = 0"
]
MATH_COMPLEX = [
    "find the limit as x approaches infinity of (x^2 - 1) / (2x^2 + 5)", "calculate the integral of 3x^2 from 0 to 2",
    "solve the differential equation dy/dx = 3x", "find the eigenvalues of the matrix [[1, 2], [3, 4]]",
    "solve the trigonometric equation sin(x) + cos(x) = 1"
]
MATH_EXPERT = [
    "prove that the square root of 2 is irrational", "explain the Riemann Hypothesis",
    "derive the quadratic formula", "solve the recurrence relation T(n) = 2T(n/2) + n",
    "prove Euler's identity: e^(i*pi) + 1 = 0"
]

# --- 7. Logic Puzzles ---
LOGIC_EASY = [
    "If a card is red, its back is blue. I have a red card, what color is its back?",
    "All humans are mortal. Socrates is human. Is Socrates mortal?",
    "If it rains, the grass gets wet. It is raining. Is the grass wet?",
    "A is older than B, B is older than C. Who is older: A or C?"
]
LOGIC_MODERATE = [
    "A is taller than B, B is shorter than C. Can we determine if A is taller than C?",
    "Solve this riddle: I speak without a mouth and hear without ears. What am I?",
    "If all blips are blops, and some blops are bleeps, are all blips bleeps?",
    "A drawer contains 6 black socks and 6 white socks. How many must you pull to guarantee a pair?"
]
LOGIC_COMPLEX = [
    "Three people tell the truth or lie. A says B lies. B says C lies. C says A and B lie. Who is telling the truth?",
    "A man has 5 sons, each son has a sister. How many children does he have?",
    "There are 3 boxes: one gold, one silver, one lead. Only one has the prize. Gold says: 'Prize is here.' Silver says: 'Prize is not here.' Lead says: 'Prize is not in Gold.' Only one statement is true. Where is the prize?",
    "If today is Tuesday, what day of the week will it be in 1000 days?"
]
LOGIC_EXPERT = [
    "Solve the Monty Hall problem and explain why switching is beneficial.",
    "Explain the prisoners' dilemma Nash equilibrium.",
    "Three gods A, B, and C are called Truth, Lie, and Random. Truth always speaks truly, Lie always lies, and Random decides randomly. You must determine their identities using 3 yes/no questions.",
    "Explain the barber paradox: The barber shaves all men who do not shave themselves. Does the barber shave himself?"
]

# --- 8. Code Debugging ---
DEBUGGING_LANGUAGES = ["Python", "JavaScript", "C++", "Java", "Go"]
DEBUGGING_CODES = [
    "an infinite loop while updating index",
    "a division by zero error in my average calculation",
    "a null pointer exception when accessing a dictionary",
    "an index out of bounds error",
    "a variable scope issue inside a function"
]
DEBUGGING_TEMPLATES = [
    "find the bug in this {} code: {}",
    "why does this {} code fail: {}",
    "debug this {} function: {}",
    "how do I fix a {} error in {}"
]

def generate_dataset():
    dataset = []
    
    # 1. Factual/General Queries (Complexity 1.0)
    for verb in FACTUAL_VERBS:
        for subj in FACTUAL_SUBJECTS:
            query = f"{verb} {subj}"
            dataset.append((query, 1.0))
            
    # 2. Coding (Trivial: 1.5, Algorithmic: 3.0, Complex: 4.0, Expert: 5.0)
    for topic in CODING_TRIVIAL_TOPICS:
        for lang in LANGUAGES:
            for temp in CODING_TRIVIAL_TEMPLATES:
                query = temp.format(topic, lang)
                dataset.append((query, 1.5))
                
    for algo in ALGORITHMS:
        for lang in LANGUAGES:
            for temp in ALGORITHM_TEMPLATES:
                query = temp.format(algo, lang)
                dataset.append((query, 3.0))
                
    for task in COMPLEX_TASKS:
        for lang in LANGUAGES:
            for temp in COMPLEX_TEMPLATES:
                query = temp.format(task, lang)
                dataset.append((query, 4.0))
                
    for task in EXPERT_TASKS:
        for ctx in EXPERT_SYSTEM_CONTEXTS:
            for temp in EXPERT_TEMPLATES:
                query = temp.format(task, ctx)
                dataset.append((query, 5.0))
                
    # 3. Sentiment Analysis (Complexity 1.0 - 1.5)
    for adj in SENTIMENT_ADJECTIVES:
        for noun in SENTIMENT_NOUNS:
            text = f"The {noun} was {adj}."
            for temp in SENTIMENT_TEMPLATES:
                dataset.append((temp.format(text), 1.2))
                
    # 4. Summarization (Complexity 2.0 / 4.0)
    for subj in SUMMARIZATION_SUBJECTS:
        for temp in SUMMARIZATION_TEMPLATES_EASY:
            dataset.append((temp.format(subj), 2.0))
        for temp in SUMMARIZATION_TEMPLATES_HARD:
            dataset.append((temp.format(subj), 4.0))
            
    # 5. NER (Complexity 2.5)
    for sample in NER_SAMPLES:
        for temp in NER_TEMPLATES:
            dataset.append((temp.format(sample), 2.5))
            
    # 6. Math Reasoning (Complexity 1.0 - 5.0)
    for q in MATH_TRIVIAL:
        dataset.append((q, 1.0))
        dataset.append((f"solve {q}", 1.0))
    for q in MATH_EASY:
        dataset.append((q, 2.0))
        dataset.append((f"solve the math problem: {q}", 2.0))
    for q in MATH_MODERATE:
        dataset.append((q, 3.0))
        dataset.append((f"can you solve this: {q}", 3.0))
    for q in MATH_COMPLEX:
        dataset.append((q, 4.0))
        dataset.append((f"solve this calculus problem: {q}", 4.0))
    for q in MATH_EXPERT:
        dataset.append((q, 5.0))
        dataset.append((f"mathematical proof: {q}", 5.0))
        
    # 7. Logic Puzzles (Complexity 2.0 - 5.0)
    for q in LOGIC_EASY:
        dataset.append((q, 2.0))
        dataset.append((f"solve this logic question: {q}", 2.0))
    for q in LOGIC_MODERATE:
        dataset.append((q, 3.0))
        dataset.append((f"logical puzzle: {q}", 3.0))
    for q in LOGIC_COMPLEX:
        dataset.append((q, 4.0))
        dataset.append((f"solve this hard puzzle: {q}", 4.0))
    for q in LOGIC_EXPERT:
        dataset.append((q, 5.0))
        dataset.append((f"expert riddle: {q}", 5.0))
        
    # 8. Code Debugging (Complexity 3.5)
    for lang in DEBUGGING_LANGUAGES:
        for code in DEBUGGING_CODES:
            for temp in DEBUGGING_TEMPLATES:
                query = temp.format(lang, code)
                dataset.append((query, 3.5))
                
    return dataset

def train():
    dataset = generate_dataset()
    print(f"Generated {len(dataset)} high-quality samples using semantic templates.")
    
    X = [item[0] for item in dataset]
    y = [item[1] for item in dataset]
    
    # Train vectorizer
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, lowercase=True)
    X_vec = vectorizer.fit_transform(X)
    
    # Model: Ridge Regression
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
        "is this movie good or bad",
        "summarize Mount Everest in one sentence",
        "extract locations from: Alice visited Paris",
        "solve for x: 3x + 5 = 20",
        "solve this logic puzzle: A is older than B, B is older than C. Who is older?",
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
