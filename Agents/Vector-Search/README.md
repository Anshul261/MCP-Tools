# RAG Agent with Agno Framework

A Retrieval-Augmented Generation (RAG) application using the Agno framework with Azure OpenAI, Docling document processing, and Brave Search integration.

## Features

- **Agno Framework**: Built with the modern Agno agent framework
- **Document Processing**: Uses Docling for PDF, DOCX, PPTX conversion
- **Vector Database**: PostgreSQL with pgvector extension
- **Local Embeddings**: HuggingFace with BAAI/bge-small-en-v1.5 model (runs locally)
- **Azure OpenAI**: Chat model for responses
- **Web Search**: Brave Search API integration
- **Interactive CLI**: Command-line interface for Q&A

## Quick Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup PostgreSQL with pgvector**:
   ```bash
   # Create database
   createdb rag_database
   
   # Initialize schema
   psql -d rag_database -f database/init_db.sql
   ```

3. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

4. **Run setup**:
   ```bash
   python setup.py
   ```

5. **Start the agent**:
   ```bash
   python agno_rag_agent.py
   ```

## Configuration

Edit your `.env` file with:

```env
# Azure OpenAI (Chat model only)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_chat_deployment

# Database
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=rag_database
DB_PORT=5432

# Optional: Web Search
BRAVE_API_KEY=your_brave_api_key
```

**Note**: Embeddings now run locally using HuggingFace with the BAAI/bge-small-en-v1.5 model - no additional API keys needed!

## Usage

### Interactive Mode
```bash
python agno_rag_agent.py
```

Commands:
- Ask any question
- `add <path>` - Add documents from file or directory
- `quit` - Exit

### Adding Documents
Place documents in the `documents/` folder or use the `add` command:
```
add /path/to/your/documents
```

Supported formats: PDF, DOCX, PPTX, TXT

## Architecture

```
Documents → Docling → Markdown → Knowledge Base → Vector DB
                                      ↓
User Query → Agent → Local Search + Web Search → Response
```

## Files

- `agno_rag_agent.py` - Main RAG agent
- `setup.py` - Automated setup script
- `database/init_db.sql` - Database schema
- `.env.example` - Configuration template
- `requirements.txt` - Dependencies

## Troubleshooting

1. **Database connection issues**: 
   ```bash
   # Test your connection first
   python test_db_connection.py
   ```
   See `README_SETUP.md` for detailed database setup instructions.

2. **Import errors**: Run `python setup.py` to check all dependencies

3. **Azure OpenAI errors**: Verify API keys and deployment names in `.env`

4. **No documents**: Add documents to `documents/` folder or use `add` command

5. **PostgreSQL authentication errors**: Check `README_SETUP.md` for authentication fixes