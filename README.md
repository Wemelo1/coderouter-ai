# ⚡ CodeRouter AI

> A cost-aware AI coding assistant that intelligently routes tasks between local and remote models based on complexity — minimizing cost without sacrificing accuracy.

Built for the **AMD Developer Hackathon: ACT II** on lablab.ai

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Powered-green?style=flat-square)
![Fireworks AI](https://img.shields.io/badge/Fireworks-AI-orange?style=flat-square)
![Ollama](https://img.shields.io/badge/Ollama-Local-purple?style=flat-square)

---

## 🧠 How It Works

```
User Query
    ↓
[Classifier] — Scores complexity 1-5 using local model (always free)
    ↓
Score ≤ 3 → 🟢 Local Model (Ollama) — Free, instant
Score > 3 → 🔴 Remote Model (Fireworks AI GLM 5.2) — Powerful, used sparingly
    ↓
Response + Full Cost Breakdown
```

The classifier runs **entirely locally** — so even the routing decision costs zero credits. Only genuinely complex tasks are escalated to the remote model.

---

## ✨ Features

- **Intelligent Routing** — complexity-based decisions, not random assignment
- **Cost Transparency** — every response shows tokens used, cost saved, and cost incurred
- **User Authentication** — login/register system with per-user data isolation
- **Persistent Query History** — SQLite database stores all sessions across restarts
- **Real-time Analytics** — live dashboard showing local vs remote usage and total savings
- **Syntax Highlighting** — code responses rendered with full highlighting
- **Dark/Light Mode** — toggle between themes
- **FastAPI Backend** — clean REST API architecture
- **Graceful Error Handling** — descriptive error messages when remote is unavailable

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Workflow | LangGraph |
| Local Model | Ollama (qwen2.5-coder:1.5b) |
| Remote Model | Fireworks AI (GLM 5.2) |
| Backend | FastAPI + Uvicorn |
| Database | SQLite (persistent storage) |
| Frontend | HTML / CSS / JavaScript |
| Authentication | Token-based session management |

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed locally
- Fireworks AI account with API key

### 1. Clone the repo
```bash
git clone https://github.com/Wemelo1/coderouter-ai
cd coderouter-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull the local model
```bash
ollama pull qwen2.5-coder:1.5b
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` and fill in your values:
```env
FIREWORKS_API_KEY=your_fireworks_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
FIREWORKS_MODEL=accounts/fireworks/models/glm-5p2
COMPLEXITY_THRESHOLD=3
```

### 5. Run the server
```bash
python server.py
```

Open your browser at `http://localhost:8000`

---

## 📁 Project Structure

```
coderouter-ai/
├── server.py           ← FastAPI server (entry point)
├── workflow.py         ← LangGraph routing workflow
├── classifier.py       ← Complexity scoring (runs locally)
├── router.py           ← Routing decision logic
├── remote.py           ← Fireworks AI integration
├── local.py            ← Ollama integration
├── cost_tracker.py     ← SQLite logging + session stats
├── code.html           ← Frontend UI
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variable template
└── README.md
```

---

## 🎯 Complexity Scoring Guide

| Score | Type | Example | Model |
|---|---|---|---|
| 1 | Trivial | "what is a variable" | 🟢 Local |
| 2 | Simple | "write hello world" | 🟢 Local |
| 3 | Moderate | "write a binary search" | 🟢 Local |
| 4 | Complex | "build a REST API with JWT" | 🔴 Remote |
| 5 | Expert | "design a microservices system" | 🔴 Remote |

---

## 👥 Team

Built by **Team CodeRouter AI** for AMD Developer Hackathon: ACT II

| Member | Role |
|---|---|
| **Wemelo (Pe-MI)** | LangGraph architecture, routing logic, backend |
| **LJ (SoldierofGod-8)** | Frontend UI, chat interface, design system |
| **sleepykaneki (debraj7777)** | FastAPI, SQLite database, auth, classifier tuning |

---

## 📄 License

MIT License — feel free to build on this.
