# Build stage
FROM python:3.9-slim AS builder
ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "projectmeats.wsgi:application", "--workers=3"]