# ─── Stage 1: Builder ───────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /src

# tell uv exactly where to create the venv
ENV UV_PROJECT_ENVIRONMENT=/src/.venv

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

# ─── Stage 2: Production image ──────────────────────────────────
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/src/.venv/bin:$PATH"

WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

COPY --from=builder /src/.venv /src/.venv
COPY . .

RUN chown -R appuser:appgroup /src

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]