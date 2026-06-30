.PHONY: install dev test lint format clean

# ── Setup ────────────────────────────────────────────────────
install:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

# ── Development ──────────────────────────────────────────────
dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	make -j2 dev-backend dev-frontend

# ── Testing ──────────────────────────────────────────────────
test:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:
	cd backend && pytest tests/unit/ -v

test-integration:
	cd backend && pytest tests/integration/ -v

# ── Code quality ─────────────────────────────────────────────
lint:
	cd backend && ruff check app/ tests/
	cd frontend && npm run lint

format:
	cd backend && ruff format app/ tests/

type-check:
	cd backend && mypy app/
	cd frontend && npm run type-check

# ── Docker ───────────────────────────────────────────────────
docker-up:
	docker-compose up --build

docker-down:
	docker-compose down -v

# ── Database ─────────────────────────────────────────────────
db-migrate:
	cd backend && alembic upgrade head

db-revision:
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ── Clean ────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/.pytest_cache backend/htmlcov backend/memeval.db
