# CodeRouter AI ⚡
### Cost-aware AI multitask assistant that routes tasks intelligently between local and remote models

---

## 🧩 The Problem

Every developer using AI assistants faces the same hidden cost problem: whether you ask *"what is a variable?"* or *"design a distributed microservices architecture"*, most tools send everything to an expensive remote model. Simple questions waste credits. Complex questions deserve more power. There's no intelligence in between.

We built CodeRouter AI to fix that.

---

## 💡 What We Built

CodeRouter AI is a **cost-aware AI multitask assistant** that classifies the complexity of every query before deciding how to answer it.

Simple tasks stay **local** — handled by a lightweight model running on your own machine, completely free. Complex tasks are **escalated** to a powerful remote model on Fireworks AI — but only when they genuinely need it.

The result: developers get accurate answers at a fraction of the cost, with full transparency into every routing decision made on their behalf.

---

## 🧠 How It Works

```
User Query
     ↓
[Classifier Node] — Scores complexity 1-5 (runs locally, always free)
     ↓
[Router Node] — Score ≤ 2 → Local | Score > 2 → Remote
     ↓
[Local Model]  → Ollama (gemma2:2b) — FREE
[Remote Model] → Fireworks AI (MiniMax M3) — Credits, used sparingly
     ↓
Response + Full Cost Breakdown
```

The classifier itself runs **entirely on the local model** (using a lightweight distilled machine learning model) — meaning even the routing decision costs zero credits. Only tasks that genuinely require deeper reasoning are escalated to Fireworks AI.

---

## ✨ Key Features

**Intelligent Routing**
Queries are scored 1–5 for complexity using a tuned classifier prompt with concrete examples. Scores 1–2 stay local. Scores 3–5 go remote. The threshold is configurable via environment variable.

**Full Cost Transparency**
Every response displays the model used, complexity score, tokens consumed, credits saved, and credits spent. Users always know exactly what their queries cost.

**User Authentication & Data Isolation**
Full login/register system with token-based sessions. Each user's query history is completely isolated — no cross-user data leakage.

**Persistent Query History**
SQLite database stores every query, response, routing decision, and cost metric across sessions. History survives server restarts.

**Real-time Analytics Dashboard**
Live panel showing total queries, local vs remote split, local handling rate, total saved, and total spent — updated after every message.

**Syntax Highlighting**
Code blocks in responses are automatically highlighted using Prism.js for readability.

**Dark / Light Mode**
Full theme toggle built into the UI with system preference detection.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent Workflow | LangGraph | Stateful multi-node routing graph |
| Local Model | Ollama (gemma2:2b) | Free local inference |
| Remote Model | Fireworks AI (MiniMax M3) | Powerful remote inference for complex tasks |
| Backend | HTTP / Streamlit Server | Python web services |
| Database | SQLite | Persistent storage |
| Frontend | HTML / CSS / JavaScript | Chat UI with analytics |
| Auth | Token-based sessions | Per-user data isolation |
| Containerization | Docker & Docker Compose | Headless batch and dev environments |

---

## 📊 Results

In testing, CodeRouter AI routes over **60% of typical multitask queries locally**, eliminating those costs entirely while reserving remote model credits for queries that genuinely benefit from more powerful inference.

**Complexity distribution from real testing:**

| Complexity | Type | Routing | Example |
|---|---|---|---|
| 1 | Trivial | 🟢 Local | "what is the capital of France" |
| 2 | Simple | 🟢 Local | "summarize this passage in a sentence" |
| 3 | Moderate | 🔴 Remote | "write a python function to check if a number is prime" |
| 4 | Complex | 🔴 Remote | "build a REST API with JWT auth" |
| 5 | Expert | 🔴 Remote | "design a microservices architecture for an e-commerce platform" |

---

## 🏗️ Architecture

The core of CodeRouter AI is a **3-node LangGraph workflow**:

**Node 1 — Classifier**
Takes the raw user query and scores its complexity from 1 to 5 using the local model or offline machine learning classifier.

**Node 2 — Router**
Reads the complexity score and the configurable threshold from `.env`. Makes a binary decision: local or remote.

**Node 3 — Inference**
Calls the appropriate model. Returns the response along with token count and cost metadata. On remote failure, returns a descriptive error message rather than silently falling back.

---

## 🔐 Security & Data Isolation

User sessions are managed with cryptographically random tokens generated via Python's `secrets` module. Each user's query history, analytics, and session data are scoped to their user ID in SQLite — verified to prevent cross-user data access.

---

## 👥 Team CodeRouter AI

| Member | Role |
|---|---|
| **Pr0_M1se (Wemelo1)** | LangGraph architecture, routing logic, backend integration |
| **leonard_sesugh_shilgba71 (SoldierofGod-8)** | Frontend UI, design system, chat interface |
| **sleepykaneki (debraj7777)** | FastAPI, SQLite, authentication, classifier tuning, security |

---

## 🔗 Links
- **Demo:** https://drive.google.com/file/d/1fZrjSs2utazACgnxlDAcpl3Eu3u5PSSK/view?usp=drivesdk
- **GitHub:** https://github.com/Wemelo1/coderouter-ai
- **Track:** Track 1 — AI Workflow Automation Agents
- **Hackathon:** AMD Developer Hackathon: ACT II on lablab.ai