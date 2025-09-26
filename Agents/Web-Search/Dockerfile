# Multi-stage build for production optimization
FROM python:3.12-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim as production

# Set labels for metadata
LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.title="Brave Search MCP Server" \
      org.opencontainers.image.description="MCP server for Brave Search API integration" \
      org.opencontainers.image.vendor="Your Organization" \
      org.opencontainers.image.licenses="MIT"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser -d /app -s /bin/bash mcpuser

# Create app directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=mcpuser:mcpuser server.py .
COPY --chown=mcpuser:mcpuser .env.example .env.example

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port for HTTP transport
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=streamable-http
ENV MCP_PORT=8080
ENV MCP_HOST=0.0.0.0

# Start command
CMD ["python", "server.py"]