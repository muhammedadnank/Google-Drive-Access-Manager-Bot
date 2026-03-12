# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Google Drive Access Manager Bot — Dockerfile
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Build:  docker build -t gdrive-bot .
# Run:    docker run --env-file .env gdrive-bot
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FROM python:3.11.9-slim

# ── OS deps ───────────────────────────────────────────────────
# gcc + libssl needed by TgCrypto & some motor deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libssl-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────
WORKDIR /app

# ── Python deps (cached layer — only rebuilds on requirements change) ──
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── App source ────────────────────────────────────────────────
COPY . .

# ── Non-root user (security best practice) ───────────────────
RUN useradd -m -u 1000 botuser \
 && chown -R botuser:botuser /app
USER botuser

# ── Port (Flask / health check) ───────────────────────────────
EXPOSE 10000

# ── Health check ─────────────────────────────────────────────
# Docker/Compose will restart container if /health returns non-200
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────
CMD ["python", "-u", "server.py"]
