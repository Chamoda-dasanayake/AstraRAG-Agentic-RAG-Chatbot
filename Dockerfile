# AstraRAG — FastAPI backend only (deploy UI separately on Streamlit Cloud)
FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0

EXPOSE 8001

# Render / Railway / Fly inject PORT at runtime
CMD ["sh", "-c", "exec uvicorn src.backend_src.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
