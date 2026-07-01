# CodeRouter AI ⚡
### Cost-aware AI coding assistant that routes tasks intelligently between local and remote models

---

## 🧩 The Problem

Every developer using AI coding assistants faces the same hidden cost: every query — whether it's "what is a variable?" or "design a microservices architecture" — gets sent to an expensive remote model. Simple tasks waste credits. Complex tasks deserve more power. There's no intelligence in between.

---

## 💡 Our Solution

CodeRouter AI is a cost-aware coding assistant that **thinks before it spends**.

Before answering any query, CodeRouter classifies its complexity on a scale of 1–5 using a local model (completely free). Based on that score, it routes the query to the right model:

- **Simple tasks (score 1–2)** → Local model via Ollama — instant, free, private
- **Complex tasks (score 3–5)** → Remote model via Fireworks AI — powerful, accurate, used only when needed

The result: developers get accurate answers at a fraction of the cost, with full transparency into every routing decision.

---

## 🧠 How It Works

```
User Query
    ↓
[Classifier Node] — Scores complexity 1-5 (runs locally, always free)
    ↓
[Router Node] — Score ≤ 2 → Local | Score > 2 → Remote
    ↓
[Local Model]  → Ollama (qwen2.5-coder) — FREE
[Remote Model] → Fireworks AI (glm-5p2) — Credits, used sparingly
    ↓
Response + Full Cost Breakdown
```

Built on **LangGraph**, the workflow is a stateful multi-node graph where each step — classification, routing, inference — is a dedicated node with clean separation of concerns.

---

## ✨ Key Features

- **Intelligent routing** — complexity-based decisions, not random assignment
- **Cost transparency** — every response shows tokens used, cost saved, and cost incurred
- **Persistent query history** — SQLite database stores all sessions across restarts
- **User authentication** — login/register system with per-user history
- **Graceful fallback** — network failures fall back to local automatically, never crashing
- **Real-time session stats** — live dashboard showing local vs remote usage and total savings
- **Syntax highlighting** — code responses rendered with full highlighting

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Workflow | LangGraph |
| Local Model | Ollama (qwen2.5-coder:1.5b) |
| Remote Model | Fireworks AI (glm-5p2) |
| Backend Server | Python HTTP Server |
| Database | SQLite (persistent storage) |
| Frontend | HTML/CSS/JavaScript |
| Auth | Username/password with session management |

---

## 📊 Results

In testing, CodeRouter AI routes over **60% of typical developer queries locally**, eliminating those costs entirely while reserving remote model credits for queries that genuinely benefit from more powerful inference.

---

## 👥 Team CodeRouter AI

Built for the AMD Developer Hackathon: ACT II on lablab.ai

- **Pr0_M1se** — LangGraph architecture, routing logic, backend
- **leonard_sesugh_shilgba71** — Frontend UI, chat interface, server integration  
- **Kaneki** — SQLite database, user authentication, query history
