# Financial Approval Agent (Python)

> Agentic AI demo — real-time financial PO approval agent powered by Claude.
> Python/Flask port of the original Node.js project.

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Web framework | Flask |
| AI SDK | `anthropic` (official Python SDK) |
| Container | Docker + docker-compose |
| Frontend | Vanilla HTML/CSS/JS (unchanged) |

---

## Project structure

```
financial-approval-agent-python/
├── src/
│   ├── __init__.py
│   ├── agent.py       ← Claude tool-use loop + all 4 guardrail layers
│   └── server.py      ← Flask server + SSE streaming endpoint
├── public/
│   └── index.html     ← Frontend UI (no build step)
├── main.py            ← Entrypoint
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Quick start (local, no Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
cp .env.example .env
# Edit .env → add ANTHROPIC_API_KEY=sk-ant-...

# 4. Run
python main.py

# 5. Open
open http://localhost:3000
```

---

## Quick start (Docker)

```bash
# 1. Set API key
cp .env.example .env
# Edit .env → add ANTHROPIC_API_KEY=sk-ant-...

# 2. Build and run
docker compose up --build

# 3. Open
open http://localhost:3000
```

### Useful Docker commands

```bash
docker compose up --build -d    # run in background
docker compose logs -f          # watch live logs
docker compose down             # stop
docker compose up -d            # restart (uses cached image)
```

---

## Demo scenarios

| Preset | What fires |
|--------|-----------|
| Routine supply | All guardrails pass → auto-approved |
| High-value IT | L1 amount threshold → escalated |
| Risky vendor | L1 vendor risk > 80 → blocked |
| Adversarial PO | L1 injection scan → blocked before Claude called |

---

## Guardrail architecture

```
POST /api/approve
  → L1: Injection scan     (regex, fires before any LLM call)
  → Claude tool-use loop
      ├── erp_lookup()
      ├── vendor_risk_lookup()
      └── policy_rag()
  → L2: Confidence < 0.75  → override to ESCALATE
  → L3: Risk flag audit
  → L4: Audit log write
  → SSE stream → browser
```

---

## Requirements

- Python 3.12+
- Docker Desktop (for Docker workflow)
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)
