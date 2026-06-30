# LLM-MemEval

AI Forgetting Benchmark Framework — scientific evaluation of LLM memory retention across long conversations.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11 or higher |
| Node.js | 18 or higher |
| npm | 9 or higher |

---

## Quick Start

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd LLM-MemEval
```

### 2. Configure API keys

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and add at least one LLM provider key:

```env
# Add whichever provider you want to use
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=...
OPENROUTER_API_KEY=...

# Leave the rest as defaults unless you need to change them
DATABASE_URL=sqlite+aiosqlite:///./memeval.db
RESULTS_DIR=./results
```

> If you don't have a `backend/.env.example`, create `backend/.env` directly with the lines above.

### 3. Install dependencies

**Backend:**

```bash
cd backend
pip install -r requirements.txt
cd ..
```

> Tip: use a virtual environment — `python -m venv .venv && source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows).

**Frontend:**

```bash
cd frontend
npm install
cd ..
```

### 4. Set up the database

```bash
cd backend
alembic upgrade head
cd ..
```

This creates `backend/memeval.db` (SQLite — no server needed).

### 5. Start the servers

Open **two terminals** and run one command in each:

**Terminal 1 — Backend (FastAPI):**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend (Next.js):**

```bash
cd frontend
npm run dev
```

### 6. Open the app

```
http://localhost:3000
```

The backend API runs at `http://localhost:8000`. You can explore the API docs at `http://localhost:8000/docs`.

---

## Shortcut: run both with one command

If you have `make` installed:

```bash
make install      # install all dependencies (run once)
make db-migrate   # set up the database (run once)
make dev          # start backend + frontend together
```

---

## Docker (alternative)

If you prefer Docker, run everything — backend, frontend, and ChromaDB — with:

```bash
docker-compose up --build
```

Then open `http://localhost:3000`.

To stop:

```bash
docker-compose down
```

---

## Project structure

```
LLM-MemEval/
├── backend/          # FastAPI app (Python 3.11)
│   ├── app/          # Source code
│   ├── alembic/      # Database migrations
│   ├── tests/        # Unit and integration tests
│   ├── requirements.txt
│   └── .env          # Your API keys (not committed)
├── frontend/         # Next.js app (React 18)
│   └── src/
├── results/          # JSONL experiment logs (auto-created)
├── docker-compose.yml
└── Makefile
```

---

## Troubleshooting

**`alembic: command not found`**
Install dev dependencies instead: `pip install -r backend/requirements-dev.txt`

**Backend starts but frontend shows API errors**
Make sure the backend is running on port 8000. The frontend proxies all `/api/*` requests to `http://localhost:8000`.

**`sentence-transformers` install is slow**
This is normal — it downloads model weights on first use. Let it complete.

**ChromaDB errors on startup**
ChromaDB is only required for the RAG memory strategy. The default strategies (`no_memory`, `sliding_window`) work without it.
