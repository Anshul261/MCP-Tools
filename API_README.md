# AGNO Multi-Agent API

A comprehensive REST API for the AGNO multi-agent system with real-time streaming support, document processing, and intelligent conversation management.

## 🚀 Features

- **Multi-Agent Chat**: Coordinate between document and web search agents
- **Streaming Responses**: Real-time Server-Sent Events (SSE) streaming  
- **Document Processing**: Upload, process, and index documents
- **Knowledge Base**: Search through processed documents
- **Session Management**: Persistent conversation sessions with memory
- **System Monitoring**: Health checks, metrics, and status endpoints

## 📋 Requirements

### Core Dependencies
```bash
pip install -r requirements-api.txt
```

### AGNO System Dependencies
The API integrates with the existing AGNO multi-agent system, which requires:
- Python 3.8+
- PostgreSQL with pgvector extension
- Azure OpenAI API access
- `agno` library and all its dependencies
- `docling` for document processing
- Environment variables configured (see `.env` setup)

### Required Environment Variables
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

# Additional models (optional)
AZURE_OPENAI_API_KEY_o4=your_api_key_o4
AZURE_OPENAI_ENDPOINT_o4=your_endpoint_o4
AZURE_OPENAI_DEPLOYMENT_NAME_o4=your_deployment_o4

AZURE_OPENAI_API_KEY_5=your_api_key_5
AZURE_OPENAI_ENDPOINT_5=your_endpoint_5
AZURE_OPENAI_DEPLOYMENT_NAME_5=your_deployment_5

# Database Configuration  
DB_URL=postgresql://user:pass@host:port/db
# OR individual components:
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name

# Other configurations
HUGGINGFACE_HUB_TOKEN=your_hf_token
PGVECTOR_TABLE=rag_documents
OPENAI_API_VERSION=2024-02-15-preview
```

## 🏗️ Architecture

```
app/
├── api/v1/               # API endpoints
│   ├── chat.py          # Chat and session management
│   ├── documents.py     # Document processing
│   └── system.py        # System monitoring
├── core/                # Core functionality
│   ├── agents.py        # AGNO agent integration
│   ├── database.py      # Database management
│   └── streaming.py     # Streaming infrastructure
├── models/              # Request/response models
│   ├── requests.py      # API request models
│   └── responses.py     # API response models  
└── main.py              # FastAPI application
```

## 🚦 Quick Start

### 1. Setup Environment
Ensure your AGNO environment is configured with all required variables:
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

# Database Configuration  
DB_URL=postgresql://user:pass@host:port/db
HUGGINGFACE_HUB_TOKEN=your_token
```

### 2. Install Dependencies
```bash
pip install -r requirements-api.txt
```

### 3. Start the API Server
```bash
python start_api.py
```

The server will start on `http://localhost:8000` with:
- 📖 API Documentation: http://localhost:8000/docs
- 📊 Health Check: http://localhost:8000/health
- 🔍 Interactive API Explorer: http://localhost:8000/docs

### 4. Test the API
```bash
python api_examples.py
```

## 📡 API Endpoints

### Chat Endpoints

#### POST /api/v1/chat/message
Send a message to the AI agent team with streaming support.

**Request:**
```json
{
  "message": "What is machine learning?",
  "user_id": "user123",
  "session_id": "optional_session_id",
  "stream": true,
  "show_reasoning": false,
  "stream_intermediate_steps": true
}
```

**Response:** Server-Sent Events stream with real-time content

#### GET /api/v1/chat/sessions/{user_id}
List chat sessions for a user.

#### POST /api/v1/chat/sessions  
Create a new chat session.

#### DELETE /api/v1/chat/sessions/{session_id}
Delete a chat session.

### Document Endpoints

#### POST /api/v1/documents/upload
Upload and process documents with streaming progress.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "description=Important document" \
  -F "tags=research,ai" \
  -F "auto_process=true"
```

#### GET /api/v1/documents/
List processed documents with filtering.

#### DELETE /api/v1/documents/{document_id}
Delete a document and remove from knowledge base.

#### POST /api/v1/documents/reindex
Rebuild the knowledge base index.

### System Endpoints

#### GET /api/v1/system/health
Comprehensive system health check.

#### GET /api/v1/system/memory-status
Memory database statistics.

#### GET /api/v1/system/agents/status
Agent availability and configuration.

## 🌊 Streaming Support

All chat endpoints support Server-Sent Events (SSE) for real-time streaming:

### Client Implementation Example

```javascript
const eventSource = new EventSource('/api/v1/chat/message/stream');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.event) {
        case 'content':
            // Display streaming content
            document.getElementById('response').innerHTML += data.data.content;
            break;
            
        case 'status':
            // Show status updates
            console.log('Status:', data.data.status);
            break;
            
        case 'complete':
            // Handle completion
            eventSource.close();
            break;
            
        case 'error':
            // Handle errors
            console.error('Error:', data.data.error);
            eventSource.close();
            break;
    }
};
```

### Python Client Example

```python
import httpx
import json

async def stream_chat_response(message, user_id):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/api/v1/chat/message",
            json={"message": message, "user_id": user_id, "stream": True}
        ) as response:
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    
                    if data["event"] == "content":
                        print(data["data"]["content"], end="", flush=True)
                    elif data["event"] == "complete":
                        break
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `ENVIRONMENT` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `info` |

### Development vs Production

**Development:**
```bash
export ENVIRONMENT=development
python start_api.py  # Auto-reload enabled
```

**Production:**
```bash
export ENVIRONMENT=production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🧪 Testing

### Run Basic Tests
```bash
python simple_test.py
```

### Run Comprehensive API Tests  
```bash
python api_examples.py
```

### Manual Testing with curl

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Send Chat Message:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, world!", 
    "user_id": "test_user",
    "stream": false
  }'
```

**Upload Document:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@sample.txt" \
  -F "description=Test document"
```

## 🎯 Usage Examples

### Basic Chat Interaction

```python
import httpx
import asyncio

async def chat_example():
    async with httpx.AsyncClient() as client:
        # Create session
        session_response = await client.post(
            "http://localhost:8000/api/v1/chat/sessions",
            json={"user_id": "user123", "title": "My Chat"}
        )
        session_id = session_response.json()["session"]["session_id"]
        
        # Send message
        chat_response = await client.post(
            "http://localhost:8000/api/v1/chat/message", 
            json={
                "message": "Explain quantum computing",
                "user_id": "user123",
                "session_id": session_id,
                "stream": False
            }
        )
        
        print(chat_response.json()["response"])

asyncio.run(chat_example())
```

### Document Processing with Progress

```python
import httpx
import asyncio
import json

async def upload_with_streaming():
    async with httpx.AsyncClient() as client:
        with open("document.pdf", "rb") as f:
            files = {"file": ("document.pdf", f, "application/pdf")}
            
            async with client.stream(
                "POST",
                "http://localhost:8000/api/v1/documents/upload/stream",
                files=files
            ) as response:
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        print(f"Progress: {data['data']['status']}")

asyncio.run(upload_with_streaming())
```

## 🔍 Monitoring

### Health Monitoring
- **Basic Health**: `/health`
- **Detailed Health**: `/api/v1/system/health?detailed=true`
- **Agent Status**: `/api/v1/system/agents/status`
- **Memory Status**: `/api/v1/system/memory-status`
- **System Metrics**: `/api/v1/system/metrics`

### Logging
The API provides comprehensive logging:
- Request/response logging
- Performance metrics  
- Error tracking
- Agent activity monitoring

## 🚨 Error Handling

The API provides consistent error responses:

```json
{
  "success": false,
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "optional_request_id"
}
```

### Common Error Codes
- `400` - Bad Request (validation errors)
- `404` - Not Found (session/document not found)
- `500` - Internal Server Error
- `503` - Service Unavailable (agent system not ready)

## 🔒 Security Considerations

**Current Status:** No authentication implemented

**For Production:**
- Implement API key authentication
- Add rate limiting
- Enable HTTPS
- Validate file uploads
- Sanitize user inputs

## 🔧 Implementation Details

### Core Architecture Components

#### 1. **Agent System Integration** (`app/core/agents.py`)
- **AgentSystemManager**: Main class that initializes and manages AGNO agents
- **Key Methods**:
  - `get_agent_response()`: Async generator for streaming/non-streaming responses
  - `get_agent_status()`: Returns status of all agents
  - `get_knowledge_base_info()`: KB information and document counts
- **Dependencies**: 
  - `get_agent_system()`: Returns the global agent system instance
  - `get_knowledge_base()`: Returns the knowledge base
  - `get_document_processor()`: Returns document processing handler

#### 2. **Database Management** (`app/core/database.py`)
- **DatabaseManager**: Handles SQLite databases for API-specific data
- **SessionManager**: Manages chat sessions and conversation history
- **DocumentManager**: Tracks document processing and metadata
- **MemoryManager**: Interfaces with AGNO memory system
- **Async Wrappers**: All managers have async wrapper classes for FastAPI compatibility

#### 3. **Streaming Infrastructure** (`app/core/streaming.py`)
- **StreamingManager**: Manages active streams and event history
- **WebStreamingResponseHandler**: Optimized for web interface streaming
- **SSEFormatter**: Converts events to Server-Sent Events format
- **Event Types**: `status`, `content`, `tool_call`, `tool_result`, `agent_thinking`, `error`, `complete`

#### 4. **Request/Response Models** (`app/models/`)
- **Comprehensive Pydantic models** for all endpoints
- **Streaming support** with specialized web streaming models
- **Error handling** with structured error responses
- **Validation** with field descriptions and constraints

### Database Schema

The API creates three main SQLite databases:

#### 1. **agent_memory.db** (AGNO Memory)
- Used by AGNO memory system
- Stores conversation history and user memories

#### 2. **agent_sessions.db** (AGNO Storage)
- Used by AGNO storage system
- Stores session data and agent context

#### 3. **api_data.db** (API Specific)
```sql
-- Documents tracking
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    content_type TEXT,
    size_bytes INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    description TEXT,
    tags TEXT,  -- JSON array
    metadata TEXT,  -- JSON object
    processing_error TEXT
);

-- API sessions (extended)
CREATE TABLE api_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    metadata TEXT,  -- JSON object
    is_active BOOLEAN DEFAULT 1
);

-- Request logging
CREATE TABLE api_requests (
    request_id TEXT PRIMARY KEY,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    user_id TEXT,
    session_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time REAL,
    status_code INTEGER,
    error_message TEXT,
    metadata TEXT
);

-- Streaming sessions
CREATE TABLE streaming_sessions (
    stream_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT,
    stream_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    events_sent INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    metadata TEXT
);
```

## 🚨 Troubleshooting

### Common Import Errors

#### 1. **"No module named 'docling'"**
```bash
# Install docling
pip install docling
```

#### 2. **"No module named 'agno'"**
```bash
# Make sure you're in the correct directory with multi-agent-system.py
# Check if AGNO is properly installed
python -c "import agno; print('AGNO available')"
```

#### 3. **"'AgentSystemManager' object has no attribute 'get_response'"**
**Solution**: The correct method is `get_agent_response()`, not `get_response()`
- Fixed in commit: Updated chat API to use correct method name

#### 4. **"cannot import name 'SessionCreateResponse'"**
**Solution**: Missing response classes in models/responses.py
- Fixed in commit: Added all missing response classes

### Server Startup Issues

#### 1. **"You must pass the application as an import string"**
**Solution**: Use import string instead of app object for reload mode
```python
# Wrong
uvicorn.run(app, reload=True)

# Correct  
uvicorn.run("app.main:app", reload=True)
```

#### 2. **Unicode/Encoding Errors in main.py**
**Solution**: Remove emoji characters from log messages
```python
# Wrong
logger.info("✅ Agent system initialized")

# Correct
logger.info("[OK] Agent system initialized")
```

#### 3. **Database Connection Errors**
**Solution**: Check PostgreSQL connection and environment variables
```bash
# Test database connection
python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DB_URL'))
print('Database connection successful')
"
```

### Method Signature Mismatches

#### 1. **Async/Sync Method Conflicts**
**Solution**: Use async wrapper classes instead of modifying original classes
```python
# Wrong - modifying original class
class SessionManager:
    async def create_session(self): pass  # Conflicts with sync version

# Correct - wrapper pattern
def get_session_storage():
    class AsyncSessionManager:
        def __init__(self, manager): self._manager = manager
        async def create_session(self, data): 
            return self._manager.create_session(...)
    return AsyncSessionManager(session_manager)
```

#### 2. **Missing Dependencies in FastAPI**
**Solution**: Create dependency functions in core modules
```python
# In app/core/database.py
def get_session_storage(): return session_manager
def get_memory_system(): return memory_manager 
def get_document_storage(): return document_manager

# In app/core/agents.py  
def get_agent_system(): return agent_system
def get_knowledge_base(): return agent_system.knowledge_base
def get_document_processor(): return DocumentProcessor()
```

### Streaming Response Issues

#### 1. **Generator Not Converting to SSE**
**Solution**: Wrap async generator with proper SSE formatting
```python
# Wrong - direct generator return
return agents.get_agent_response(...)

# Correct - wrap with SSE formatting
async def stream_generator():
    agent_generator = agents.get_agent_response(...)
    async for chunk in agent_generator:
        yield f"data: {json.dumps(chunk)}\n\n"
return create_sse_response(stream_generator())
```

### Response Model Issues

#### 1. **Missing Response Classes**
**Solution**: Add all required response classes to models/responses.py
```python
class SessionCreateResponse(BaseResponse):
    session: ChatSession = Field(..., description="Created session")

class SessionDeleteResponse(BaseResponse):
    session_id: str = Field(..., description="Deleted session ID")
    message: str = Field("Session deleted successfully")

class DocumentDeleteResponse(BaseResponse):
    document_id: str = Field(..., description="Deleted document ID")
    removed_from_knowledge_base: bool = Field(..., description="KB removal status")
    message: str = Field("Document deleted successfully")
```

## 🧪 Testing Commands

### 1. **Basic Health Check**
```bash
curl http://localhost:8000/health
```

### 2. **Test Non-Streaming Chat**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What documents do you have access to?", 
    "user_id": "test_user", 
    "stream": false
  }'
```

### 3. **Test Streaming Chat**
```bash
curl -N -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about AI", 
    "user_id": "test_user", 
    "stream": true
  }'
```

### 4. **Test System Status**
```bash
curl http://localhost:8000/api/v1/system/agents/status
curl http://localhost:8000/api/v1/system/memory-status
curl http://localhost:8000/api/v1/system/health?detailed=true
```

### 5. **Test Document Upload**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@sample.txt" \
  -F "description=Test document" \
  -F "tags=test,sample"
```

## 🤝 Contributing & Maintenance

### Adding New Endpoints
1. **Create endpoint** in appropriate `app/api/v1/` file
2. **Add request/response models** to `app/models/`
3. **Add dependencies** to `app/core/` modules  
4. **Update this documentation**
5. **Add test commands** to verify functionality

### Updating AGNO Integration
1. **Check method signatures** in AGNO library
2. **Update wrapper classes** in `app/core/agents.py` and `app/core/database.py`
3. **Test with both streaming and non-streaming** responses
4. **Update environment variable** requirements if needed

### Debugging Tips
1. **Check server logs** for detailed error messages
2. **Use curl with `-v`** flag for verbose output
3. **Test individual components** before full integration
4. **Verify database connections** and environment variables
5. **Check FastAPI docs** at `/docs` for request/response formats

## 📝 License

MIT License - See LICENSE file for details.

---

## 🎉 Quick Success Check

After starting the server, visit:
- http://localhost:8000 - API info
- http://localhost:8000/docs - Interactive documentation  
- http://localhost:8000/health - Health status

**Test the chat endpoint:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test", "stream": false}'
```

Your API is ready when all endpoints return successful responses! 🚀