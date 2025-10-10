# AI-Search Multi-Agent System

A comprehensive multi-agent ecosystem built on AGNO framework, featuring specialized agents for document search, web research, data analysis, stock market insights, and invoice processing. The system includes both interactive CLI interfaces and REST API access.

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    AI-Search Multi-Agent System                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  Document Agent │    │   Web Agent     │    │ Coordinator │ │
│  │ (Vector Search) │    │  (Web Search)   │    │    Agent    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                      │                      │        │
│           └──────────────────────┼──────────────────────┘        │
│                                  │                               │
│                     ┌────────────▼───────────┐                   │
│                     │ Enhanced Multi-Agent   │                   │
│                     │      Interface         │                   │
│                     └────────────────────────┘                   │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                     Specialized Agents                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ Data-Agent   │  │ Stock-Agent  │  │ Invoice Processing  │   │
│  │  (DuckDB +   │  │  (YFinance + │  │    (OCR + DuckDB)   │   │
│  │  HTML/Chart) │  │  Next.js UI) │  │                     │   │
│  └──────────────┘  └──────────────┘  └─────────────────────┘   │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                         API Layer                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│                    ┌────────────────────┐                        │
│                    │   FastAPI Server   │                        │
│                    │  (REST + SSE)      │                        │
│                    └────────────────────┘                        │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
AI-Search-MCP/
├── Agents/                          # All specialized agent implementations
│   ├── Vector-Search/               # Core document search agent
│   ├── Web-Search/                  # Core web research agent
│   ├── Data-agent/                  # Data analysis and visualization
│   ├── Stock-Agent/                 # Stock market analysis
│   ├── invoice-processing/          # Invoice OCR and processing
│   ├── Agentic-Rag/                # RAG implementations
│   └── research-agent/              # Research-focused agent
│
├── app/                             # FastAPI application
│   ├── api/v1/                      # API endpoints
│   │   ├── chat.py                 # Chat and sessions
│   │   ├── documents.py            # Document processing
│   │   └── system.py               # System monitoring
│   ├── core/                        # Core functionality
│   │   ├── agents.py               # AGNO integration
│   │   ├── database.py             # Database management
│   │   └── streaming.py            # SSE streaming
│   └── models/                      # Request/response models
│
├── API_README.md                    # Comprehensive API documentation
├── README.md                        # This file
├── requirements-api.txt             # API dependencies
├── start_api.py                     # API server launcher
└── docker-compose.yml               # PostgreSQL + pgvector setup
```

## Important Note: Independent Agent Architecture

**Each agent is completely independent and self-contained.** They are NOT interconnected - each agent:
- Has its own environment configuration
- Runs in isolation with dedicated Docker containers (where applicable)
- Maintains separate databases and dependencies
- Can be deployed and scaled independently

This modular design allows you to run only the agents you need without requiring the entire system.

### Quick Reference: Agent Overview

| Agent | Purpose | Database | Deployment | Ports |
|-------|---------|----------|------------|-------|
| **Vector + Web Search** | Document search + web research | PostgreSQL (pgvector) | CLI | N/A |
| **Data Analysis** | Excel/CSV → HTML dashboards | DuckDB | Docker or CLI | 7778, 3001, 80 |
| **Stock Analysis** | Real-time stock market insights | SQLite | Docker or CLI | 7777, 3000, 8080 |
| **Invoice Processing** | OCR invoice extraction | DuckDB | CLI only | N/A |
| **REST API** | API access to agents | PostgreSQL | Python script | 8000 |

---

## Components Overview

### 1. Core Multi-Agent System (Vector + Web Search)

The foundational system combining document search with web research capabilities.

**Location:** `Agents/Vector-Search/` and `Agents/Web-Search/`

**Agents:**
- **Document Agent** - PgVector + HuggingFace embeddings
- **Web Agent** - Brave Search via MCP
- **Coordinator Agent** - Intelligent query routing and synthesis

**Features:**
- Intelligent query routing (company docs vs general knowledge)
- Response validation and synthesis
- Memory persistence across sessions
- Rich terminal interface with markdown rendering

**Deployment:** CLI-based, uses shared PostgreSQL database from root docker-compose.yml

### 2. Data Analysis Agent

AI-powered data visualization system with HTML dashboard generation.

**Location:** `Agents/Data-agent/`

**Key Capabilities:**
- Excel/CSV ingestion with automatic type inference
- DuckDB integration for high-performance analytics
- HTML dashboard generation (replaces traditional plotting)
- Interactive Chart.js visualizations
- Multi-agent collaboration for analysis

**Files:**
- `html-dashboard-analysis.py` - Main entry (single agent, HTML output)
- `improved-viz-analysis.py` - Multi-agent version
- `dashboard_templates.py` - Template system for HTML generation

**Output:** Professional HTML dashboards with responsive design

**Docker Deployment:**
```bash
cd Agents/Data-agent
docker-compose up -d
```
- Backend API: http://localhost:7778
- Next.js UI: http://localhost:3001
- Nginx reverse proxy: http://localhost:80
- Uses external PostgreSQL network: `ai-search-mcp_default`

### 3. Stock Analysis Agent

Real-time stock market analysis with modern web interface.

**Location:** `Agents/Stock-Agent/`

**Architecture:**
- **Backend:** AgentOS with 3 specialized agents
  - Intelligence Analyst (market data)
  - Bull/Bear Analyst (sentiment analysis)
  - Trading Manager (recommendations)
- **Frontend:** Next.js chat interface
- **Data:** YFinance integration
- **Storage:** SQLite database for agent memory

**Key Features:**
- Team memory and collaboration
- Real-time chat interface
- Comprehensive stock analysis
- Investment recommendations

**Docker Deployment:**
```bash
cd Agents/Stock-Agent
docker-compose up -d
```
- Agent API (AgentOS): http://localhost:7777
- Next.js UI: http://localhost:3000
- Nginx reverse proxy: http://localhost:8080
- Uses SQLite for persistence (no external database needed)

### 4. Invoice Processing System

Automated invoice extraction with human-in-the-loop validation.

**Location:** `Agents/invoice-processing/`

**Workflow:**
```
Invoice Image → OCR Extraction → Analysis → Validation → Human Review? → DuckDB
```

**Features:**
- Azure OpenAI vision models for OCR
- Intelligent field extraction and parsing
- Confidence scoring with configurable thresholds
- Optional human review for low-confidence extractions
- DuckDB persistence for invoices and line items
- Handles multiple invoice formats gracefully

**Configuration:**
- Auto-approval threshold for high-confidence invoices
- Configurable human review workflow
- Flexible field extraction for non-standard formats

**Deployment:** CLI-based Python script, uses DuckDB (embedded database, no external DB needed)

### 5. REST API Layer

Production-ready FastAPI server with streaming support.

**Location:** `app/`

**Capabilities:**
- Multi-agent chat with SSE streaming
- Document upload and processing
- Session management with memory
- System health monitoring
- Real-time progress updates

**Endpoints:**
- `POST /api/v1/chat/message` - Chat with agents (streaming)
- `POST /api/v1/documents/upload` - Document processing
- `GET /api/v1/system/health` - System status
- `GET /api/v1/chat/sessions/{user_id}` - Session management

**See [API_README.md](API_README.md) for complete documentation.**

## Quick Start

### Prerequisites

1. **Python Environment**
```bash
conda activate env_12
# OR
python -m venv .venv && source .venv/bin/activate
```

2. **Environment Variables** - Create `.env` file in project root:
```env
# Azure OpenAI (Required for all agents)
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
OPENAI_API_VERSION=2024-02-15-preview

# Optional: Additional Azure models (for specialized agents)
AZURE_OPENAI_API_KEY_o4=your_key
AZURE_OPENAI_ENDPOINT_o4=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME_o4=your_deployment

AZURE_OPENAI_API_KEY_5=your_key
AZURE_OPENAI_ENDPOINT_5=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME_5=your_deployment

# PostgreSQL Database (Required for Vector Search)
DB_HOST=your_db_host
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
PGVECTOR_TABLE=rag_documents

# OR use DB_URL
DB_URL=postgresql://user:pass@host:port/db

# HuggingFace (Required for Vector Search embeddings)
HUGGINGFACE_HUB_TOKEN=your_token

# Optional: Web Search
BRAVE_API_KEY=your_brave_api_key
```

3. **Database Setup** (for Vector Search)
```bash
# Start PostgreSQL with pgvector using Docker
docker-compose up -d

# OR install pgvector extension on existing PostgreSQL
CREATE EXTENSION vector;
```

### Running Different Components

Each agent can be run independently. Choose the deployment method based on your needs:

#### 1. Core Multi-Agent System (CLI)
```bash
# Start shared PostgreSQL database first (if not already running)
docker-compose up -d  # from project root

# Then run the multi-agent CLI
cd Agents/Vector-Search  # or Web-Search
python enhanced_multi_agent.py
```

**Available Commands:**
- `demo` - Run capability demonstrations
- `status` - Show system status
- `metrics` - Display usage analytics
- `doc: [query]` - Direct document search
- `web: [query]` - Direct web search
- `[query]` - Auto-routed intelligent query
- `quit` - Exit system

#### 2. REST API Server
```bash
# From project root
python start_api.py
```

**Access Points:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

#### 3. Data Analysis Agent

**Option A: Docker (Recommended)**
```bash
cd Agents/Data-agent
docker-compose up -d
```
- Backend: http://localhost:7778
- UI: http://localhost:3001
- Nginx: http://localhost:80

**Option B: Local Python**
```bash
cd Agents/Data-agent
python html-dashboard-analysis.py
```

#### 4. Stock Analysis Agent

**Option A: Docker (Recommended)**
```bash
cd Agents/Stock-Agent
docker-compose up -d
```
- Agent API: http://localhost:7777
- UI: http://localhost:3000
- Nginx: http://localhost:8080

**Option B: Local Development**
```bash
# Backend (terminal 1)
cd Agents/Stock-Agent
python agent-api.py

# Frontend (terminal 2)
cd Agents/Stock-Agent/ui
npm run dev
```

#### 5. Invoice Processing Agent
```bash
cd Agents/invoice-processing
python main.py
```
*Note: CLI-based only, processes images in current directory*

## Usage Examples

### Interactive Commands

```bash
# General queries (auto-routed)
What is machine learning?
Tell me about the company leave policy

# URL queries (auto-routed to web)
What is this about https://github.com/openai/gpt-4?

# Direct agent access
doc: Find information about employee benefits
web: Latest AI developments in 2025

# System commands
demo        # Run capability demonstrations
status      # Show system status and agent capabilities  
metrics     # Display usage analytics
help        # Show all available commands
quit        # Exit the system
```

### Query Routing Logic

- **Company-specific** (leave policy, benefits, procedures) → **Document Agent**
- **URLs** (GitHub, websites) → **Web Agent**
- **General knowledge** (definitions, current events) → **Web Agent**
- **Creative tasks** (how to implement, create) → **Both agents + synthesis**

## Key Features

- **Intelligent Routing**: Automatically determines which agent(s) to use
- **Response Validation**: Ensures answers are relevant to queries
- **Rich Interface**: Professional console with markdown rendering
- **Memory Persistence**: Agents remember conversation history
- **Demo Mode**: Built-in capability demonstrations
- **Error Handling**: Graceful fallbacks when services are unavailable
- **Metrics Tracking**: Usage analytics and performance monitoring

## Technical Details

- **Framework**: AGNO Level 4 architecture
- **Vector DB**: PgVector with HuggingFace embeddings
- **Web Search**: Brave Search API via MCP
- **Memory**: SQLite storage for agent sessions
- **UI**: Rich library for enhanced console experience
- **Async**: Full async/await support for MCP tools

## Agent Collaboration

The system implements true multi-agent collaboration where:

1. **Coordinator** analyzes queries and routes intelligently
2. **Document Agent** searches local knowledge base
3. **Web Agent** performs real-time web research
4. **Responses** are validated, synthesized, and presented as unified answers

No more duplicate responses or irrelevant information - just intelligent, coordinated assistance!