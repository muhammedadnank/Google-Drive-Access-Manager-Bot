# Google Drive Access Manager Bot — Dockerfile

# Build:  docker build -t gdrive-bot .
# Run:    docker run --env-file .env gdrive-bot

FROM python:3.11.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libssl-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 botuser \
 && chown -R botuser:botuser /app
USER botuser

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

CMD ["python", "-u", "server.py"]
