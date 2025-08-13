# ===== Multi-stage build for optimization =====
FROM python:3.11-slim as builder

# Build arguments
ARG BUILDTIME
ARG VERSION

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# ===== Production stage =====
FROM python:3.11-slim as production

# Labels for metadata
LABEL maintainer="acthiago" \
      version="${VERSION}" \
      description="API Consulta v2 - FastAPI application with hexagonal architecture" \
      buildtime="${BUILDTIME}"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/home/app/.local/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with specific UID/GID
RUN groupadd -r app -g 1000 && \
    useradd -r -g app -u 1000 -m -s /bin/bash app && \
    mkdir -p /app /app/logs /app/storage && \
    chown -R app:app /app

# Switch to non-root user
USER app

# Set work directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/app/.local

# Copy application code with proper ownership
COPY --chown=app:app . .

# Create necessary directories
RUN mkdir -p logs storage

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application with optimized settings
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log"]