# ==============================================================================
# Production Dockerfile for Backend Service (FastAPI + SQLModel + SQLite)
# Multi-stage security profile: Non-root user, slim base, minimal footprint
# ==============================================================================

FROM python:3.12-slim AS production

# Set environment variables for Python runtime optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    DATABASE_URL="sqlite:////app/data/todo.db"

# Install curl for reliable container health checking and remove apt cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root system group and user
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Set working directory
WORKDIR /app

# Install Python dependencies first for caching layers
COPY requirements.txt requirement.txt* ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create data directory for persistent SQLite database and logs
RUN mkdir -p /app/data && \
    chown -R appuser:appgroup /app

# Copy application source code into the image
COPY --chown=appuser:appgroup . /app/

# Switch to non-root user for principle of least privilege
USER appuser

# Expose backend API port
EXPOSE 8000

# Health check probe validating API responsiveness
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Launch ASGI server via Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
