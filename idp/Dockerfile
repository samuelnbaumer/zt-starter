# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (certs, curl for debug)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY . .

# Security: run as non-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000
# Uvicorn loads APP instance from app.py
CMD ["uvicorn", "app:APP", "--host", "0.0.0.0", "--port", "8000"]
