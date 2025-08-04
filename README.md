# AI-Search Multi-Agent System

A Level 4 AGNO architecture multi-agent system combining vector-based document search with real-time web research capabilities.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Document Agent │    │   Web Agent     │    │    Coordinator  │
│  (Vector Search)│    │  (Web Search)   │    │       Agent     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Enhanced Multi  │
                    │ Agent Interface │
                    └─────────────────┘
```

## File Structure & Functionality

### Core System Files

- **`enhanced_multi_agent.py`** - Main entry point with Rich interactive console
  - Professional UI with colored panels and markdown support
  - Demo capabilities and metrics tracking
  - Commands: `demo`, `status`, `metrics`, `help`, `doc:`, `web:`, `quit`

- **`multi_agent_system.py`** - System orchestration and initialization
  - Manages agent lifecycle and communication
  - Environment validation and error handling
  - Factory pattern for system creation

### Agent Classes (`agents/` directory)

- **`base_agent.py`** - Base class for all agents
  - Common AGNO agent initialization
  - Azure OpenAI model configuration
  - Memory management with SQLite storage
  - Async query processing methods

- **`coordinator_agent.py`** - Team orchestration and query routing
  - Intelligent query classification with URL detection
  - Response synthesis and validation
  - Multi-agent coordination strategies
  - Routing logic: company queries → docs, general queries → web, URLs → web

- **`document_agent.py`** - Vector search specialist
  - PgVector database integration with HuggingFace embeddings
  - Document conversion using Docling
  - Local knowledge base management
  - Hybrid search capabilities

- **`web_agent.py`** - Web research specialist  
  - MCP (Model Context Protocol) integration with Brave Search
  - Real-time web search capabilities
  - Async MCP tools handling
  - Multiple search strategies (web, news, smart, research)

- **`__init__.py`** - Package initialization and exports

### Data Directories

- **`data/`** - Agent memory databases (SQLite)
- **`documents/`** - Raw documents for processing
- **`converted_docs/`** - Processed documents in markdown format

## Quick Start

### Prerequisites

1. **Environment Variables** - Create `.env` file:
```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
OPENAI_API_VERSION=2024-02-15-preview

# PostgreSQL Database
DB_HOST=your_db_host
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
PGVECTOR_TABLE=your_table_name

# Optional: Web Search
BRAVE_API_KEY=your_brave_api_key
```

2. **Dependencies**: Ensure you have the working `Web-Search/` and `Vector-Search/` directories

### Run the System

```bash
# Activate your conda environment
conda activate env_12

# Start the interactive multi-agent system
python enhanced_multi_agent.py
```

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