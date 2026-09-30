# syntax=docker/dockerfile:1

# ========== Stage 1: builder – cài Poetry và thư viện ==========
FROM python:3.14-slim AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install --no-cache-dir poetry "poetry==2.5.1"

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# ========== Stage 2: runtime – image gọn, không chứa Poetry ==========
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app ./app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]