# Build context must be repo root (AI-Search-MCP/)
# docker build -f Agents/it-support-agent/Dockerfile .
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files from repo root
COPY pyproject.toml uv.lock .python-version ./

# Install deps
RUN uv sync --frozen --no-dev

# Copy agent code and knowledge base PDFs
COPY Agents/it-support-agent/agent.py .
COPY Agents/it-support-agent/*.pdf ./

EXPOSE 7777

CMD ["uv", "run", "python", "agent.py"]
