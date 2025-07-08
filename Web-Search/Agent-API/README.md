# Agent API

Production-ready Agent API server with search capabilities, built following the Agent API documentation standards.

## Features

- **FastAPI-based REST API** with comprehensive endpoints
- **PostgreSQL database** for sessions, knowledge, and memories  
- **Enhanced Agent** with persistent memory and search tools
- **Search capabilities** using Brave Search API (web, news, smart, research)
- **Production deployment** ready with Docker and Docker Compose
- **Agent API compliant** folder structure and architecture

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- Brave Search API key

### Installation

1. **Clone and setup**:
```bash
cd Agent-API
cp .env.example .env
# Edit .env with your configuration
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
# OR generate from pyproject.toml:
python scripts/requirements_generator.py
```

3. **Initialize database**:
```bash
python scripts/init_db.py
```

4. **Start the server**:
```bash
python scripts/run_server.py
```

### Docker Deployment

1. **Build and start services**:
```bash
docker-compose up -d
```

2. **Initialize database**:
```bash
docker-compose exec agent-api python scripts/init_db.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Core Endpoints

- `GET /` - API information and available tools
- `GET /health` - Health check
- `GET /tools` - Available search tools

### Chat & Sessions

- `POST /chat` - Chat with the agent
- `POST /sessions` - Create/load session
- `GET /sessions/{user_id}` - Get user sessions
- `GET /sessions/{user_id}/{session_id}/history` - Get conversation history

### Search

- `POST /search` - Direct search using available tools
- Available tools: `web_search`, `news_search`, `smart_search`, `research_search`

### Metrics

- `GET /metrics/{user_id}` - Get user/session metrics

## Architecture

### Folder Structure
```
Agent-API/
├── agents/                 # Agent implementations
│   ├── enhanced_agent.py   # Main agent class
│   ├── search_tools.py     # Search tool implementations
│   └── __init__.py
├── api/                    # FastAPI routes
│   ├── main.py            # Main application
│   └── __init__.py
├── db/                     # Database models and config
│   ├── models.py          # SQLAlchemy models
│   ├── database.py        # Database configuration
│   └── __init__.py
├── scripts/               # Helper scripts
│   ├── init_db.py         # Database initialization
│   ├── run_server.py      # Server startup
│   └── requirements_generator.py
├── pyproject.toml         # Project configuration
├── Dockerfile             # Production container
├── docker-compose.yml     # Multi-service deployment
└── README.md
```

### Database Models

- **AgentSession**: Session management and configuration
- **AgentMessage**: Conversation messages with metadata
- **AgentMemory**: Persistent memories (facts, preferences, context)
- **AgentKnowledge**: Searchable knowledge base
- **AgentTool**: Available tools configuration
- **AgentMetrics**: Usage and performance tracking
- **AgentConfig**: User and agent configurations

### Agent Features

- **Persistent Memory**: Conversation history across sessions
- **Search Tools**: Web, news, smart, and research search
- **Metrics Tracking**: Usage analytics and performance monitoring
- **Session Management**: Multi-user session handling
- **PostgreSQL Storage**: Production-ready data persistence

## Usage Examples

### Chat with Agent
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Research the latest AI developments in 2025",
    "user_id": "1"
  }'
```

### Direct Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence trends 2025",
    "tool": "research_search",
    "parameters": {"depth": "medium", "include_news": true}
  }'
```

### Create Session
```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123"
  }'
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `BRAVE_API_KEY`: Brave Search API key
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: info)
- `OLLAMA_MODEL`: Ollama model ID

### Agent Configuration

The agent uses:
- **Model**: Ollama yasserrmd/jan-nano-4b:latest
- **Storage**: PostgreSQL with session persistence
- **Tools**: Brave Search API integration
- **Memory**: 25 message history with context awareness

## Production Deployment

### Docker Production
```bash
# Build production image
docker build -t agent-api:latest .

# Run with docker-compose
docker-compose -f docker-compose.yml up -d
```

### Cloud Deployment

Compatible with:
- **Google Cloud Run**
- **AWS App Runner** 
- **Azure Container Apps**
- **Kubernetes clusters**

### Environment Setup

1. Set up managed PostgreSQL service
2. Configure environment variables
3. Deploy container image
4. Initialize database with `scripts/init_db.py`

## Development

### Local Development
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run with auto-reload
RELOAD=true python scripts/run_server.py

# Format code
black .
isort .

# Type checking
mypy .
```

### Testing
```bash
pytest tests/
pytest --cov=. tests/
```

## Agent API Compliance

This implementation follows the [Agent API documentation](https://docs.agno.com/agent-api/introduction) standards:

✅ **FastAPI server architecture**  
✅ **PostgreSQL database for persistence**  
✅ **Agent/API/DB folder structure**  
✅ **Production deployment ready**  
✅ **Docker containerization**  
✅ **Environment configuration**  
✅ **Comprehensive logging**  
✅ **Health checks and monitoring**  

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions:
- Check the logs: `docker-compose logs agent-api`
- Database issues: `python scripts/init_db.py --reset`
- API documentation: `http://localhost:8000/docs`