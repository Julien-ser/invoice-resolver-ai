# Multi-stage build for FastAPI application
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies to a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


# Final stage
FROM python:3.12-slim

# Create non-root user
RUN addgroup --system --gid 1001 invoice && \
    adduser --system --uid 1001 --gid 1001 invoice

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=invoice:invoice ./src /app/src
COPY --chown=invoice:invoice alembic.ini /app/alembic.ini
COPY --chown=invoice:invoice alembic /app/alembic

# Create necessary directories with correct permissions
RUN mkdir -p /app/logs /app/media && \
    chown -R invoice:invoice /app

# Switch to non-root user
USER invoice

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
