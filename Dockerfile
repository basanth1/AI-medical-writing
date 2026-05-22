FROM node:20-alpine AS frontend

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS backend

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgomp1 poppler-utils curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend /frontend/dist /app/frontend/dist
RUN mkdir -p /app/data/faiss_index

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8765/api/v1/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8765"]
