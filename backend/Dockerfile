FROM python:3.11-slim

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    git curl build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Gereksinimler
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Python path'e backend klasörünü ekle
ENV PYTHONPATH=/app/backend

# FastAPI + Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
