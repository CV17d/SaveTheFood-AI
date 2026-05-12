.PHONY: install test lint run format check clean docker-up docker-down seed migrate

# ─── Environment ──────────────────────────────────────────
install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	pre-commit install

# ─── Quality ──────────────────────────────────────────────
lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/
	black src/ tests/

check: lint
	pytest --tb=short -q

# ─── Testing ─────────────────────────────────────────────
test:
	pytest -v --cov=src --cov-report=html --cov-report=term-missing

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

test-e2e:
	pytest -v -m e2e

# ─── Application ─────────────────────────────────────────
run:
	streamlit run src/presentation/app.py --server.port=8501

# ─── Database ────────────────────────────────────────────
seed:
	python scripts/seed_shelf_life.py

migrate:
	python scripts/migrate_db.py

# ─── Docker ──────────────────────────────────────────────
docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down -v

# ─── Cleanup ─────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage dist/ build/ *.egg-info
