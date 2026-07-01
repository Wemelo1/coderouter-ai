# ⚡ CodeRouter AI

A cost-aware AI coding assistant that intelligently routes tasks between a **local model (Ollama)** and a **remote model (Fireworks AI)** based on task complexity — minimizing cost without sacrificing accuracy.

Built for the **AMD Developer Hackathon: ACT II** on lablab.ai.

---

## 🧠 How It Works

```
User Query
    ↓
[Classifier] — Scores complexity 1-5 (runs locally, always free)
    ↓
[Router] — Score ≤ 2 → Local | Score > 2 → Remote
    ↓
[Local Model]  → Ollama (qwen2.5-coder:1.5b) — FREE
[Remote Model] → Fireworks AI (glm-5p2) — Credits
    ↓
Response + Cost Breakdown
```

---

## 🛠️ Tech Stack

- **LangGraph** — agent workflow orchestration
- **Ollama** — local model runner (free)
- **Fireworks AI** — remote model API
- **Streamlit** — web UI
- **Python** — core language

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/Wemelo1/coderouter-ai
cd coderouter-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama + pull model
```bash
# Install from https://ollama.com
ollama pull qwen2.5-coder:1.5b
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Add your FIREWORKS_API_KEY to .env
```

### 5. Run the app
```bash
streamlit run app.py
```

### 6. Run with Docker (Containerized)
As an alternative to setting up Python locally, you can run CodeRouter AI containerized:
```bash
# 1. Start the container
docker compose up --build
# 2. Open http://localhost:8000 in your browser
```
Note: Ensure your local Ollama instance is running on the host machine.

---

## 👥 Team
Built by Team CodeRouter AI for AMD Developer Hackathon ACT II
## Now to run app
python server.py