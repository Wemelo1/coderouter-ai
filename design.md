# CodeRouter AI — Design Document

## Overview

CodeRouter AI is a cost-aware coding assistant that intelligently routes programming queries between a **free local model** (Ollama) and a **paid remote model** (Fireworks AI) based on task complexity — minimizing cost without sacrificing accuracy.

## Architecture

```
User Query
    ↓
[Classifier]          — scores complexity 1–5 (always free, runs on Ollama)
    ↓
[Router]              — score ≤ 2 → local | score > 2 → remote
    ↓
[Local Model]         — Ollama (qwen2.5-coder:1.5b) — $0.00
[Remote Model]        — Fireworks AI (glm-5p2) — per-token cost
    ↓
Response + Cost Breakdown
```

## Components

### 1. Classifier (`agent/classifier.py`)
- Uses local Ollama to score task complexity from 1–5
- **1–2**: Simple tasks (syntax fix, naming, explanation) → routed to local
- **3–5**: Complex tasks (generation, debugging, architecture) → routed to remote
- Always runs locally, so classification is always free

### 2. Router (`agent/router.py`)
- Compares complexity score against a configurable threshold (default: 2)
- Returns `"local"` or `"remote"` to decide execution path

### 3. Local Model (`models/local.py`)
- Calls Ollama with `qwen2.5-coder:1.5b`
- Tracks estimated token usage and computes cost saved vs. remote equivalent
- **Cost**: $0.00 (free, runs on local hardware)

### 4. Remote Model (`models/remote.py`)
- Calls Fireworks AI via OpenAI-compatible API
- Uses `glm-5p2`
- Tracks actual token usage and cost incurred
- **Cost**: ~$0.002 per 1K tokens

### 5. Cost Tracker (`utils/cost_tracker.py`)
- In-memory session log of all queries
- Provides aggregate stats (total queries, local/remote split, total saved/spent)

### 6. Workflow (`workflow.py`)
- Built with **LangGraph** (`StateGraph`)
- Nodes: `classifier → router → local/remote → END`
- Compiled graph exported as `coderouter` for use in the frontend

### 7. Frontend

#### Streamlit UI (`app.py`)
- Chat interface with message history
- Displays routing badge, complexity score, tokens, and cost metrics
- Session stats sidebar

#### HTML UI (`code.html`)
- Standalone chatbot interface
- Communicates with the Python backend via REST API
- Responsive, modern dark-theme design

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Workflow orchestration | LangGraph |
| Local model runner | Ollama |
| Remote model API | Fireworks AI |
| UI (Python) | Streamlit |
| UI (Web) | HTML + CSS + JavaScript |
| Language | Python 3 |

## Data Flow

1. User submits a query via the UI
2. Classifier scores complexity (always local, free)
3. Router decides: local (score ≤ 2) or remote (score > 2)
4. Selected model generates a response
5. Cost data is logged and returned to the UI
6. UI displays response + cost breakdown

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FIREWORKS_API_KEY` | API key for Fireworks AI |
| `COMPLEXITY_THRESHOLD` | Threshold for routing (default: 2) |

## Running the App

```bash
# Streamlit UI
streamlit run app.py

# HTML UI — serve with any static server
python -m http.server 8000
# Then open http://localhost:8000/code.html
```
