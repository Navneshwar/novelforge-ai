# Single-service deploy: build the React frontend, then run the FastAPI
# backend, which serves that build directly (see main.py's static mount +
# SPA catch-all). One container, one URL, no CORS to configure.

# --- Stage 1: build the frontend ---
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: backend + built frontend ---
FROM python:3.12-slim
WORKDIR /app/backend

# System deps some cognee extras need to build wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY backend/ .
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Data dir — mount your host's persistent volume here (sqlite db + cognee's
# local vector/graph stores all live under ./data relative to this WORKDIR).
RUN mkdir -p /app/backend/data /app/backend/logs
VOLUME ["/app/backend/data"]

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
