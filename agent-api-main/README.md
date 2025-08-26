# Custom Agent API - Complete Documentation

A production-ready FastAPI application providing intelligent agents for document search, web search, and coordinated reasoning. Built with the Agno framework and designed for Azure cloud services.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Agent Details](#agent-details)
7. [Document Processing](#document-processing)
8. [Development Guide](#development-guide)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What This API Does
- **Document Agent**: RAG-powered search through uploaded documents using HuggingFace embeddings
- **Web Agent**: Real-time web search using Brave Search API
- **Reasoning Team**: Coordinated multi-agent responses combining document and web sources
- **Document Processing**: Converts PDF, DOCX, PPTX, TXT files to searchable knowledge base
- **Memory System**: Remembers user conversations and preferences across sessions

### Key Technologies
- **Framework**: FastAPI (async Python web framework)
- **AI Framework**: Agno (agent orchestration)
- **Database**: Azure PostgreSQL with pgvector extension
- **LLM**: Azure OpenAI (GPT-4)
- **Embeddings**: HuggingFace transformers (BAAI/bge-small-en-v1.5)
- **Document Processing**: Docling (PDF/Office conversion)
- **Web Search**: Brave Search API

---

## Quick Start

### Prerequisites
- Python 3.11+ 
- Azure PostgreSQL database with pgvector extension
- Azure OpenAI deployment (GPT-4 recommended)
- HuggingFace account for embeddings

### 1. Clone and Setup
```bash
git clone <repository-url>
cd custom-agent-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary  # PostgreSQL driver
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials (see Configuration section)
nano .env
```

### 3. Start the Server
```bash
# Set Python path and start server
PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Verify Installation
```bash
# Test basic connectivity
curl http://localhost:8000/v1/health

# View interactive docs
open http://localhost:8000/docs
```

---

## Architecture

### Project Structure
```
custom-agent-api/
├── agents/              # Agent implementations
│   ├── base.py          # Abstract base classes
│   ├── document_agent.py # Document search agent
│   ├── web_agent.py     # Web search agent
│   ├── team_coordinator.py # Multi-agent coordination
│   └── selector.py      # Agent registry and selection
├── api/                 # FastAPI application
│   ├── main.py          # Application entry point
│   ├── settings.py      # API configuration
│   └── routes/          # API endpoints
│       ├── agents.py    # Agent interaction endpoints
│       ├── documents.py # Document management endpoints
│       ├── health.py    # Health check endpoints
│       └── v1_router.py # API version routing
├── core/                # Core business logic
│   ├── config.py        # Configuration management
│   ├── database.py      # Database connections
│   └── document_processor.py # Document processing
├── scripts/             # Utility scripts
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Container orchestration
└── .env.example         # Configuration template
```

### Data Flow
1. **Document Upload** → Temporary storage → Docling conversion → Markdown → Embeddings → PostgreSQL/pgvector
2. **User Query** → Agent selection → Knowledge/Web search → LLM processing → Response
3. **Memory** → Conversation context → PostgreSQL storage → Future personalization

---

## Configuration

### Environment Variables

#### Required - Azure PostgreSQL
```bash
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your-server.postgres.database.azure.com
DB_PORT=5432
DB_NAME=your_database_name
```

#### Required - Azure OpenAI
```bash
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
OPENAI_API_VERSION=2024-02-15-preview
```

#### Required - HuggingFace
```bash
HUGGINGFACE_HUB_TOKEN=your_huggingface_token
```

#### Optional - External APIs
```bash
BRAVE_API_KEY=your_brave_search_api_key  # For web search
ANTHROPIC_API_KEY=your_anthropic_key     # Future extensions
```

#### Optional - System Configuration
```bash
# Vector database
PGVECTOR_TABLE=rag_documents

# File storage
DOCUMENTS_DIR=documents
CONVERTED_DOCS_DIR=converted_docs

# API settings
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_DOCS_ENABLED=true
```

### Azure Services Setup

#### PostgreSQL Database
1. Create Azure Database for PostgreSQL
2. Enable pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Configure firewall rules for your IP
4. Note connection details for .env file

#### Azure OpenAI
1. Create Azure OpenAI resource
2. Deploy GPT-4 model
3. Note endpoint URL and API key
4. Set deployment name in configuration

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication required. Add authentication middleware in `api/main.py` for production.

### Core Endpoints

#### Health Check
```http
GET /v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "api": {
    "name": "Custom Agent API",
    "version": "1.0.0",
    "debug": false
  },
  "database": {
    "database": "healthy",
    "vector_db": "healthy",
    "embedder": "healthy",
    "knowledge_base": "healthy"
  },
  "documents": {
    "status": "healthy",
    "total_documents": 5,
    "converted_documents": 5,
    "knowledge_base_loaded": true
  },
  "configuration": {
    "status": "healthy"
  }
}
```

#### List Agents
```http
GET /v1/agents
```

**Response:**
```json
["doc_agent", "web_agent", "reasoning_team"]
```

#### Get Agent Information
```http
GET /v1/agents/info
```

**Response:**
```json
[
  {
    "id": "doc_agent",
    "name": "Document Agent",
    "description": "RAG Assistant with local document search capabilities",
    "type": "agent"
  },
  {
    "id": "web_agent", 
    "name": "Web Agent",
    "description": "Web search agent that helps users find the latest news and information",
    "type": "agent"
  },
  {
    "id": "reasoning_team",
    "name": "Reasoning Knowledge Team", 
    "description": "Team that coordinates between document search and web search to provide comprehensive answers",
    "type": "team"
  }
]
```

#### Chat with Agent
```http
POST /v1/agents/{agent_id}/chat
```

**Request Body:**
```json
{
  "message": "What is artificial intelligence?",
  "user_id": "user123",
  "session_id": "session_456", 
  "stream": true,
  "debug_mode": false,
  "detailed_breakdown": true
}
```

**Response (Non-streaming):**
```json
{
  "response": "Artificial intelligence (AI) refers to...",
  "session_id": "session_456",
  "user_id": "user123", 
  "agent_id": "doc_agent"
}
```

**Response (Streaming with Detailed Breakdown):**
```
data: RunResponseStartedEvent(created_at=1755518780, event='RunStarted', agent_id='doc_agent', agent_name='Document Agent', run_id='b12388dc-666b-424a-95d4-03f654d37e68', session_id='test_1755518780', team_session_id=None, tools=None, content=None, model='gpt-4.1-mini', model_provider='Azure')
data: ToolCallStartedEvent(created_at=1755518783, event='ToolCallStarted', agent_id='doc_agent', agent_name='Document Agent', run_id='b12388dc-666b-424a-95d4-03f654d37e68', session_id='test_1755518780', team_session_id=None, tools=None, content=None, tool=ToolExecution(tool_call_id='call_HjYQgJO0KYVVi1ZXOwIXa9sr', tool_name='search_knowledge_base', tool_args={'query': 'artificial intelligence'}, tool_call_error=None, result=None))
data: search_knowledge_base(query=artificial intelligence) completed in 2.5s.
data: RunResponseContentEvent(...) 
data: Artificial intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence...
data: MemoryUpdateStartedEvent(...)
data: MemoryUpdateCompletedEvent(...)
data: [DONE]
```

**Response (Simple Streaming):**
```
data: Artificial intelligence
data: (AI) refers to
data: [DONE]
```

### Document Management

#### Get Document Statistics
```http
GET /v1/documents/stats
```

**Response:**
```json
{
  "total_documents": 10,
  "converted_documents": 8,
  "total_size_bytes": 5242880,
  "knowledge_base_loaded": true,
  "source_directory": "/app/documents",
  "converted_directory": "/app/converted_docs"
}
```

#### List Documents
```http
GET /v1/documents
```

**Response:**
```json
[
  {
    "filename": "report.pdf",
    "size": 1024000,
    "converted": true,
    "converted_path": "/app/converted_docs/report.md",
    "extension": ".pdf",
    "valid": true
  }
]
```

#### Upload Documents
```http
POST /v1/documents/upload
Content-Type: multipart/form-data
```

**Form Data:**
- `files`: File(s) to upload (PDF, DOCX, PPTX, TXT)

**Response:**
```json
{
  "message": "Upload completed. 2 files uploaded successfully, 0 failed.",
  "uploaded_files": [
    {
      "filename": "document1.pdf",
      "size": 1024000,
      "success": true
    }
  ],
  "failed_files": [],
  "total_uploaded": 2,
  "total_failed": 0
}
```

#### Process Documents
```http
POST /v1/documents/process
```

Converts all uploaded documents and reloads knowledge base.

**Response:**
```json
{
  "message": "Processing completed. 3 documents converted and knowledge base reloaded.",
  "total_files": 3,
  "converted": 3,
  "failed": 0,
  "knowledge_base_reloaded": true
}
```

#### Delete Document
```http
DELETE /v1/documents/{filename}
```

**Response:**
```json
{
  "message": "Document 'report.pdf' deleted successfully"
}
```

---

## Agent Details

### Document Agent (`doc_agent`)

**Purpose:** Search and analyze uploaded documents using RAG (Retrieval Augmented Generation)

**Capabilities:**
- Semantic search through document knowledge base
- Multi-document synthesis and analysis
- Citation of specific documents and sections
- Context-aware responses based on document content

**Best For:**
- Technical documentation queries
- Policy and procedure questions  
- Historical data analysis
- Internal knowledge base searches

**Example Usage:**
```bash
curl -X POST http://localhost:8000/v1/agents/doc_agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the key findings in the quarterly report?",
    "user_id": "analyst1"
  }'
```

### Web Agent (`web_agent`)

**Purpose:** Search current web information using Brave Search API

**Capabilities:**
- Real-time web search
- Current events and news retrieval
- Fact verification against web sources
- Citation of web sources with URLs

**Best For:**
- Breaking news and current events
- Market data and trends
- General factual queries
- Real-time information needs

**Example Usage:**
```bash
curl -X POST http://localhost:8000/v1/agents/web_agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the latest developments in AI technology?",
    "user_id": "researcher1"
  }'
```

**Note:** Requires `BRAVE_API_KEY` in environment variables. Without it, web search functionality is disabled.

### Reasoning Team (`reasoning_team`)

**Purpose:** Coordinate between document and web agents for comprehensive analysis

**Capabilities:**
- Multi-source information synthesis
- Document vs. web information comparison
- Comprehensive research combining internal and external data
- Intelligent source prioritization

**Decision Logic:**
- **Documents First:** Technical specs, internal policies, historical records
- **Web First:** Current events, breaking news, recent developments  
- **Both Sources:** Research topics, comprehensive analysis, fact-checking

**Best For:**
- Complex research questions
- Comparative analysis
- Comprehensive reports
- Multi-source fact verification

**Example Usage:**
```bash
curl -X POST http://localhost:8000/v1/agents/reasoning_team/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare our internal AI strategy with current market trends",
    "user_id": "executive1"
  }'
```

### Memory and Personalization

All agents include:
- **Conversation Memory:** Remembers chat history within sessions
- **User Memories:** Learns user preferences and context across sessions
- **Session Summaries:** Maintains conversation continuity
- **Contextual Awareness:** Builds upon previous interactions

---

## Document Processing

### Supported Formats
- **PDF**: Research papers, reports, manuals
- **Microsoft Word (.docx)**: Documents, proposals  
- **PowerPoint (.pptx)**: Presentations, slide decks
- **Plain Text (.txt)**: Notes, logs, simple documents

### Processing Pipeline

1. **Upload** → Files stored in `documents/` directory
2. **Validation** → Check file type, size limits (50MB default)
3. **Conversion** → Docling converts to Markdown format
4. **Embedding** → HuggingFace creates vector embeddings
5. **Storage** → Embeddings stored in PostgreSQL with pgvector
6. **Indexing** → Available for semantic search by document agent

### File Size Limits
- Default: 50MB per file
- Configurable in `core/config.py`
- Large files automatically chunked during processing

### Processing Workflow

#### Upload Documents
```bash
# Single file
curl -X POST http://localhost:8000/v1/documents/upload \
  -F "files=@report.pdf"

# Multiple files  
curl -X POST http://localhost:8000/v1/documents/upload \
  -F "files=@report1.pdf" \
  -F "files=@presentation.pptx"
```

#### Convert and Index
```bash
# Process all uploaded documents
curl -X POST http://localhost:8000/v1/documents/process

# Or step by step:
# 1. Convert to markdown
curl -X POST http://localhost:8000/v1/documents/convert

# 2. Reload knowledge base
curl -X POST http://localhost:8000/v1/documents/knowledge/reload
```

#### Monitor Processing
```bash
# Check conversion status
curl http://localhost:8000/v1/documents/stats

# List all documents
curl http://localhost:8000/v1/documents
```

### Troubleshooting Document Processing

**Common Issues:**
- **Conversion fails:** Check file format and corruption
- **Large files timeout:** Increase file size limits or split files
- **Embeddings fail:** Verify HuggingFace token and network access
- **Knowledge base empty:** Ensure documents are converted before querying

---

## Development Guide

### Adding New Agents

1. **Create Agent Factory:**
```python
# agents/my_new_agent.py
from agents.base import BaseAgentFactory
from agno.agent import Agent

class MyNewAgentFactory(BaseAgentFactory):
    @property
    def agent_id(self) -> str:
        return "my_new_agent"
    
    @property 
    def agent_name(self) -> str:
        return "My New Agent"
        
    @property
    def agent_description(self) -> str:
        return "Description of what this agent does"
    
    def create_agent(self, user_id=None, session_id=None, debug_mode=False):
        config = self.get_base_agent_config(user_id, session_id, debug_mode)
        config.update({
            "name": self.agent_name,
            "agent_id": self.agent_id,
            "tools": [],  # Add tools here
            "instructions": "Agent behavior instructions here"
        })
        return Agent(**config)

# Register the agent
from agents.base import agent_registry
my_agent_factory = MyNewAgentFactory()
agent_registry.register_agent_factory(my_agent_factory)
```

2. **Update Agent Selector:**
```python
# agents/selector.py
from agents.my_new_agent import my_agent_factory  # Import to trigger registration
```

### Adding New Tools

Tools must follow the Agno tool interface:

```python
from agno.tools.base import BaseTools

class MyCustomTool(BaseTools):
    def __init__(self):
        super().__init__(name="my_custom_tool")
    
    def my_function(self, query: str) -> str:
        """Custom tool function"""
        # Tool implementation
        return "Tool result"
```

### Environment Configuration

#### Development vs Production
```python
# core/config.py
class APISettings(BaseSettings):
    debug: bool = Field(default=False)  # Set True for development
    docs_enabled: bool = Field(default=True)  # Set False for production
```

#### Logging Configuration
```python
# api/main.py
logging.basicConfig(
    level=logging.INFO if not DEBUG_MODE else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Testing

#### Manual API Testing
```bash
# Health check
curl http://localhost:8000/v1/health

# Agent functionality
curl -X POST http://localhost:8000/v1/agents/doc_agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_id": "test"}'
```

#### Integration Testing
```python
import requests

def test_agent_chat():
    response = requests.post(
        "http://localhost:8000/v1/agents/doc_agent/chat",
        json={"message": "test query", "user_id": "test_user"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
```

---

## Deployment

### Local Development
```bash
# Start development server with auto-reload
PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Deployment

#### Build and Run
```bash
# Build image
docker build -t custom-agent-api .

# Run container
docker run -d \
  --name custom-agent-api \
  --env-file .env \
  -p 8000:8000 \
  -v ./documents:/app/documents \
  -v ./converted_docs:/app/converted_docs \
  custom-agent-api
```

#### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Cloud Deployment

#### Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image custom-agent-api:latest .

# Deploy container
az container create \
  --resource-group mygroup \
  --name custom-agent-api \
  --image myregistry.azurecr.io/custom-agent-api:latest \
  --environment-variables \
    DB_HOST=mydb.postgres.database.azure.com \
    AZURE_OPENAI_ENDPOINT=https://myopenai.openai.azure.com/ \
  --ports 8000
```

#### Production Considerations
- **Environment Variables:** Use Azure Key Vault for secrets
- **SSL/TLS:** Add HTTPS termination with Azure Application Gateway
- **Scaling:** Use Azure Container Apps for auto-scaling
- **Monitoring:** Add Application Insights for telemetry
- **Backup:** Regular database backups and document storage backup

---

## Troubleshooting

### Common Startup Issues

#### "ModuleNotFoundError: No module named 'api'"
**Cause:** Not running from project root or PYTHONPATH not set
**Solution:**
```bash
cd /path/to/custom-agent-api  # Go to project root
PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### "No module named 'psycopg2'"
**Cause:** Missing PostgreSQL driver
**Solution:**
```bash
pip install psycopg2-binary
# Or: pip install psycopg[binary]
```

#### "SyntaxError: expected 'except' or 'finally' block"
**Cause:** Python syntax error in code files
**Solution:** Check Python file syntax:
```bash
python -m py_compile api/routes/documents.py
```

#### "Database connection failed"
**Cause:** Invalid PostgreSQL credentials or network issues
**Solution:**
1. Verify credentials in `.env` file
2. Test connection manually:
   ```bash
   psql "postgresql://user:password@host:port/database"
   ```
3. Check Azure PostgreSQL firewall rules

### Runtime Issues

#### "Agent not found"
**Cause:** Agent not properly registered or invalid agent_id
**Solution:**
```bash
# Check available agents
curl http://localhost:8000/v1/agents
```

#### "Knowledge base empty"
**Cause:** No documents processed or conversion failed
**Solution:**
```bash
# Check document status
curl http://localhost:8000/v1/documents/stats

# Process documents
curl -X POST http://localhost:8000/v1/documents/process
```

#### "Web search not working"
**Cause:** Missing BRAVE_API_KEY or invalid API key
**Solution:**
1. Get API key from https://brave.com/search/api/
2. Add to `.env` file: `BRAVE_API_KEY=your_key_here`
3. Restart server

### Performance Issues

#### Slow response times
**Causes & Solutions:**
- **Large documents:** Implement document chunking
- **Database queries:** Add database connection pooling
- **LLM calls:** Implement response caching
- **Memory usage:** Monitor and optimize embeddings storage

#### High memory usage
**Solutions:**
- Limit concurrent requests with rate limiting
- Implement document pagination
- Use smaller embedding models
- Add memory monitoring and alerts

### Debugging

#### Enable Debug Mode
```bash
# Set in .env file
API_DEBUG=true

# Or environment variable
export API_DEBUG=true
PYTHONPATH=. python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

#### View Detailed Logs
```bash
# Application logs (if logging to file)
tail -f logs/api.log

# Container logs (Docker)
docker logs custom-agent-api -f

# Health check with details
curl http://localhost:8000/v1/health | jq
```

#### Test Individual Components
```bash
# Test database connection
curl http://localhost:8000/v1/health/database

# Test document system
curl http://localhost:8000/v1/documents/health

# Test specific agent
curl http://localhost:8000/v1/agents/doc_agent/validate
```

---

## Support and Maintenance

### Regular Maintenance
- **Update dependencies:** `pip install -r requirements.txt --upgrade`
- **Database cleanup:** Remove old conversation logs and temporary files
- **Document management:** Archive or remove outdated documents
- **Monitor disk space:** Document storage and database growth

### Backup Strategy
- **Database:** Regular PostgreSQL backups
- **Documents:** Backup `documents/` and `converted_docs/` directories
- **Configuration:** Version control `.env` template and code changes

### Monitoring
- **Health endpoints:** Regular automated health checks
- **Performance metrics:** Response times, memory usage, database performance
- **Error tracking:** Monitor application logs for errors and exceptions
- **Usage analytics:** Track agent usage patterns and popular queries

---

This documentation provides complete setup, configuration, and usage instructions for the Custom Agent API. For additional support or feature requests, refer to the project repository or contact the development team.