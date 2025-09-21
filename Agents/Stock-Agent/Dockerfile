# Simple Python 3.12 build with pip
FROM python:3.12-slim-bookworm AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 1: Install dependencies only (for better caching)
FROM base AS builder

# Copy requirements file
COPY requirements.txt ./

# Install dependencies using pip with caching
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Stage 2: Copy application and install project
FROM builder AS final

# Copy application code
COPY agent-api.py ./
COPY base-agent.py ./
COPY improved-agent.py ./
COPY advisor-agent.py ./

# No additional installation needed since we used pip install above

# Create tmp directory for SQLite database
RUN mkdir -p /app/tmp

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 7777

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7777/health')" || exit 1

# Run the application
CMD ["python", "agent-api.py"]