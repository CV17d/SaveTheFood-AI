# ─── SaveTheFood AI — Multi-Stage Dockerfile ─────────────
FROM python:3.11-slim AS base

# System dependencies for OpenCV & Tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─── Dependencies ─────────────────────────────────────────
FROM base AS dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# ─── Application ─────────────────────────────────────────
FROM dependencies AS app
COPY . .

# Create data directories
RUN mkdir -p data/db data/raw data/processed

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "src/presentation/app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
