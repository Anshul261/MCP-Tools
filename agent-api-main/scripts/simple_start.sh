#!/bin/bash
# scripts/simple_start.sh - Simplified startup script

set -e

echo "=== Custom Agent API Simple Startup ==="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cat > .env << 'EOF'
# Azure PostgreSQL Database Configuration
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your-server.postgres.database.azure.com
DB_PORT=5432
DB_NAME=your_database_name

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
OPENAI_API_VERSION=2024-02-15-preview

# HuggingFace Configuration
HUGGINGFACE_HUB_TOKEN=your_huggingface_token

# External APIs (Optional)
BRAVE_API_KEY=your_brave_search_api_key

# Vector Database Configuration
PGVECTOR_TABLE=rag_documents

# Document Processing Configuration
DOCUMENTS_DIR=documents
CONVERTED_DOCS_DIR=converted_docs

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
API_DOCS_ENABLED=true
EOF
    echo "❌ Please update .env file with your actual credentials and run again"
    exit 1
fi

# Simple environment loading (Python-based to handle special characters)
echo "📁 Loading environment variables..."
if command -v python3 >/dev/null 2>&1; then
    eval "$(python3 << 'EOF'
import os
import re

try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove surrounding quotes if present
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Escape for shell export
                value_escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
                print(f'export {key}="{value_escaped}"')
except Exception as e:
    print(f'echo "Error loading .env: {e}"')
    exit(1)
EOF
)"
else
    echo "❌ Python3 not found. Please install Python3 or manually set environment variables."
    exit 1
fi

# Validate required variables
echo "🔍 Validating configuration..."
required_vars="DB_USER DB_PASSWORD DB_HOST DB_NAME AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT AZURE_OPENAI_DEPLOYMENT_NAME HUGGINGFACE_HUB_TOKEN"
missing_vars=""

for var in $required_vars; do
    if [ -z "$(eval echo \$$var)" ]; then
        missing_vars="$missing_vars $var"
    fi
done

if [ -n "$missing_vars" ]; then
    echo "❌ Missing required environment variables:$missing_vars"
    echo "   Please update your .env file with the required values"
    exit 1
fi

echo "✅ Configuration validated"

# Create directories
echo "📂 Creating directories..."
mkdir -p documents converted_docs logs

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📦 Installing requirements..."

# Determine pip command
PIP_CMD=""
if command -v pip3 >/dev/null 2>&1; then
    PIP_CMD="pip3"
elif command -v pip >/dev/null 2>&1; then
    PIP_CMD="pip"
else
    PIP_CMD="python3 -m pip"
fi

echo "Using pip command: $PIP_CMD"

$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt

# Set Python path
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start the development server
echo ""
echo "🚀 Starting development server..."
echo "   - API will be available at: http://${API_HOST:-0.0.0.0}:${API_PORT:-8000}"
echo "   - Docs will be available at: http://${API_HOST:-localhost}:${API_PORT:-8000}/docs"
echo "   - Press Ctrl+C to stop"
echo ""

# Start with uvicorn
python -m uvicorn api.main:app \
    --host "${API_HOST:-0.0.0.0}" \
    --port "${API_PORT:-8000}" \
    --reload \
    --log-level debug