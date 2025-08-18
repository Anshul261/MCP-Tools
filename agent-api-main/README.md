# Custom Agent API

A production-ready FastAPI application that provides intelligent agents for document search, web search, and coordinated reasoning. Built with the Agno framework and designed for enterprise deployment with Azure services.

## 🚀 Features

- **Document Agent**: RAG-powered document search and analysis
- **Web Agent**: Real-time web search and information retrieval  
- **Reasoning Team**: Coordinated multi-agent responses combining document and web sources
- **Azure Integration**: Full support for Azure PostgreSQL and Azure OpenAI
- **Production Ready**: Docker support, health checks, and comprehensive logging
- **Modern API**: FastAPI with automatic documentation and validation

## 🏗️ Architecture

```
custom-agent-api/
├── agents/           # Agent implementations and factories
├── api/             # FastAPI routes and application
├── core/            # Core configuration and database management
├── scripts/         # Deployment and utility scripts
├── tests/           # Test suite
└── docs/            # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure PostgreSQL database with pgvector extension
- Azure OpenAI deployment
- HuggingFace account (for embeddings)

### One-Command Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd custom-agent-api

# Make scripts executable
chmod +x scripts/*.sh

# Start the application (will guide you through setup)
./scripts/start.sh
```

The startup script will:
1. Create a `.env` file from template
2. Prompt you to configure your credentials
3. Set up the environment
4. Start the API server

### Manual Setup

1. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

2. **Development Mode**
   ```bash
   ./scripts/start.sh --dev
   ```

3. **Production Mode**
   ```bash
   ./scripts/start.sh
   ```

4. **Docker Deployment**
   ```bash
   ./scripts/start.sh --docker
   ```

## 🔧 Configuration

### Required Environment Variables

```bash
# Azure PostgreSQL
DB_USER=your_db_user
DB_PASSWORD=your_db_password  
DB_HOST=your-server.postgres.database.azure.com
DB_NAME=your_database_name

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# HuggingFace
HUGGINGFACE_HUB_TOKEN=your_token
```

### Optional Configuration

```bash
# Web search (enhances web agent capabilities)
BRAVE_API_KEY=your_brave_api_key

# API customization
API_PORT=8000
API_DEBUG=false
API_DOCS_ENABLED=true
```

## 📚 API Usage

### Available Endpoints

- `GET /v1/health` - System health check
- `GET /v1/agents` - List available agents
- `POST /v1/agents/{agent_id}/chat` - Chat with an agent
- `POST /v1/documents/upload` - Upload documents
- `POST /v1/documents/process` - Convert and index documents
- `GET /docs` - Interactive API documentation

### Available Agents

1. **doc_agent** - Document search and analysis
2. **web_agent** - Web search and current information
3. **reasoning_team** - Coordinated document + web search

### Example Usage

```bash
# Check API health
curl http://localhost:8000/v1/health

# List available agents
curl http://localhost:8000/v1/agents

# Chat with document agent
curl -X POST http://localhost:8000/v1/agents/doc_agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What information is available about AI?",
    "user_id": "user123", 
    "stream": false
  }'

# Upload documents
curl -X POST http://localhost:8000/v1/documents/upload \
  -F "files=@document.pdf"

# Process uploaded documents
curl -X POST http://localhost:8000/v1/documents/process
```

### Python Client Example

```python
import requests

# Initialize client
base_url = "http://localhost:8000"

# Chat with reasoning team
response = requests.post(f"{base_url}/v1/agents/reasoning_team/chat", json={
    "message": "Compare document information with current web trends",
    "user_id": "user123",
    "stream": False
})

print(response.json()["response"])
```

## 🐳 Docker Deployment

### Development with Docker

```bash
# Build and start with Docker Compose
./scripts/start.sh --docker

# View logs
docker-compose logs -f

# Stop services  
docker-compose down
```

### Production Deployment

```bash
# Build production image
docker build -t custom-agent-api:latest .

# Run with environment file
docker run -d \
  --name custom-agent-api \
  --env-file .env \
  -p 8000:8000 \
  -v ./documents:/app/documents \
  -v ./converted_docs:/app/converted_docs \
  custom-agent-api:latest
```

## 🔍 Document Processing

### Supported Formats

- PDF documents
- Microsoft Word (.docx)
- PowerPoint (.pptx)  
- Plain text (.txt)

### Processing Workflow

1. **Upload**: Documents uploaded via API
2. **Convert**: Docling converts to markdown
3. **Embed**: HuggingFace creates embeddings
4. **Index**: Stored in PostgreSQL with pgvector
5. **Search**: Available to document agent

### Usage

```bash
# Upload multiple documents
curl -X POST http://localhost:8000/v1/documents/upload \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx"

# Process all documents  
curl -X POST http://localhost:8000/v1/documents/process

# Check processing status
curl http://localhost:8000/v1/documents/stats
```

## 🚀 Production Deployment

### Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image custom-agent-api:latest .

# Deploy to Container Instances
az container create \
  --resource-group mygroup \
  --name custom-agent-api \
  --image myregistry.azurecr.io/custom-agent-api:latest \
  --environment-variables @env-vars.yaml \
  --ports 8000
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-agent-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: custom-agent-api
  template:
    metadata:
      labels:
        app: custom-agent-api
    spec:
      containers:
      - name: api
        image: custom-agent-api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: api-secrets
```

## 🔧 Development

### Setup Development Environment

```bash
# Development mode with auto-reload
./scripts/start.sh --dev

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black .
ruff check .
```

### Project Structure

- **agents/**: Agent implementations using factory pattern
- **api/**: FastAPI routes and application configuration  
- **core/**: Shared configuration, database, and utilities
- **scripts/**: Deployment and utility scripts
- **tests/**: Comprehensive test suite

### Adding New Agents

1. Create agent factory in `agents/`
2. Register in `agents/selector.py`
3. Add tests in `tests/`

```python
# agents/my_agent.py
from agents.base import BaseAgentFactory

class MyAgentFactory(BaseAgentFactory):
    @property  
    def agent_id(self) -> str:
        return "my_agent"
    
    def create_agent(self, user_id, session_id, debug_mode):
        # Implementation
        pass
```

## 📊 Monitoring and Logging

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/v1/health

# Database health  
curl http://localhost:8000/v1/health/database

# Document system health
curl http://localhost:8000/v1/documents/health
```

### Logging

- **Development**: Console output with debug information
- **Production**: Structured JSON logs to files
- **Docker**: Container logs via Docker logging drivers

### Metrics

The API provides built-in metrics for:
- Request/response times
- Error rates  
- Agent usage statistics
- Document processing metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards

- Python 3.11+ type hints
- Black code formatting
- Ruff linting
- Comprehensive test coverage
- Clear documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Database Connection Issues**
- Verify Azure PostgreSQL credentials
- Check network connectivity and firewall rules
- Ensure pgvector extension is installed

**Document Processing Fails**  
- Check HuggingFace token validity
- Verify supported document formats
- Monitor disk space for converted documents

**Agent Responses Empty**
- Confirm Azure OpenAI deployment is active
- Check API key permissions
- Verify model deployment name matches configuration

### Getting Help

- Check the [API documentation](http://localhost:8000/docs)
- Review logs in development mode
- Open an issue on GitHub