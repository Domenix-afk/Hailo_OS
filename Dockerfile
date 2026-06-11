# Multi-stage Dockerfile für Nero AI Framework
# Build with: docker build -t nero-ai:latest .
# Run with: docker run --gpus all -p 8000:8000 nero-ai:latest

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 as base

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    build-essential \
    libffi-dev \
    libssl-dev \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# BACKEND STAGE
# ============================================================
FROM base as backend-builder

WORKDIR /app/backend

# Copy requirements
COPY backend/requirements.txt .

# Install Python packages with cache
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# FRONTEND STAGE
# ============================================================
FROM node:20-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy source
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/*.* ./

# Build
RUN npm run build

# ============================================================
# FINAL STAGE
# ============================================================
FROM base as runtime

WORKDIR /app

# Copy Python packages from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create directories
RUN mkdir -p ./temp ./logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health').read()" || exit 1

# Expose ports
EXPOSE 8000

# Start backend
CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================
# LABELS
# ============================================================
LABEL maintainer="Nero AI Framework"
LABEL description="Advanced AI Voice Interaction System"
LABEL version="1.0.0"
