#!/bin/bash
# scripts/utils.sh - Utility functions for scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${PURPLE}=== $1 ===${NC}\n"
}

print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓ ${NC}$1"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${NC}$1"
}

print_error() {
    echo -e "${RED}✗ ${NC}$1"
}

print_step() {
    echo -e "\n${CYAN}→ $1${NC}"
}

# Function to create default .env file
create_env_file() {
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
API_DEBUG=false
API_DOCS_ENABLED=true
EOF
}

# Function to safely load environment variables using Python
load_env_vars() {
    if [ ! -f ".env" ]; then
        print_error ".env file not found"
        return 1
    fi
    
    print_info "Loading environment variables from .env..."
    
    # Check if python3 is available
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python3 is required but not found"
        return 1
    fi
    
    # Use Python to safely parse and export environment variables
    local temp_script=$(mktemp)
    cat > "$temp_script" << 'EOF'
import os
import sys

def safe_export(key, value):
    # Escape special characters for shell
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    value = value.replace('$', '\\$')
    value = value.replace('`', '\\`')
    print(f'export {key}="{value}"')

try:
    with open('.env', 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check for key=value format
            if '=' not in line:
                continue
                
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Remove surrounding quotes if present
            if len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
            
            # Export the variable
            safe_export(key, value)
            
except Exception as e:
    print(f'echo "Error parsing .env file on line {line_num}: {e}"', file=sys.stderr)
    sys.exit(1)
EOF
    
    # Execute the Python script and eval the output
    local env_exports
    env_exports=$(python3 "$temp_script")
    local exit_code=$?
    
    # Clean up temp script
    rm -f "$temp_script"
    
    if [ $exit_code -ne 0 ]; then
        print_error "Failed to parse .env file"
        return 1
    fi
    
    # Apply the exports
    eval "$env_exports"
    
    print_success "Environment variables loaded successfully"
    return 0
}

# Function to validate required environment variables
validate_env_vars() {
    local missing_vars=""
    
    # Required variables
    local required_vars="DB_USER DB_PASSWORD DB_HOST DB_NAME AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT AZURE_OPENAI_DEPLOYMENT_NAME HUGGINGFACE_HUB_TOKEN"
    
    for var in $required_vars; do
        local value
        value=$(eval echo "\$$var")
        if [ -z "$value" ]; then
            missing_vars="$missing_vars $var"
        fi
    done
    
    if [ -n "$missing_vars" ]; then
        print_error "Missing required environment variables:"
        for var in $missing_vars; do
            print_error "  - $var"
        done
        print_info "Please update your .env file with the required values"
        print_info "Make sure there are no special characters that need escaping"
        return 1
    fi
    
    print_success "All required environment variables are set"
    return 0
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_system_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version
    python_version=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $python_version"
    
    # Check pip (try multiple variants)
    local pip_cmd=""
    if command_exists pip3; then
        pip_cmd="pip3"
    elif command_exists pip; then
        pip_cmd="pip"
    elif python3 -m pip --version >/dev/null 2>&1; then
        pip_cmd="python3 -m pip"
    else
        print_error "pip is required but not found. Please install pip."
        print_info "Try: sudo apt install python3-pip (Ubuntu/Debian) or equivalent for your system"
        exit 1
    fi
    
    print_info "Using pip command: $pip_cmd"
    
    # Check Docker (optional)
    if command_exists docker; then
        print_info "Docker is available"
        if command_exists docker-compose; then
            print_info "Docker Compose is available"
        elif docker compose version >/dev/null 2>&1; then
            print_info "Docker Compose (v2) is available"
        fi
    else
        print_warning "Docker is not available (required for Docker deployment)"
    fi
    
    print_success "System requirements check completed"
}

# Function to install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    # Determine pip command
    local pip_cmd=""
    if command_exists pip3; then
        pip_cmd="pip3"
    elif command_exists pip; then
        pip_cmd="pip"
    else
        pip_cmd="python3 -m pip"
    fi
    
    if [ -f "requirements.txt" ]; then
        $pip_cmd install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Function to create virtual environment
create_venv() {
    print_step "Creating Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_info "Virtual environment already exists"
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip in virtual environment
    python -m pip install --upgrade pip
    
    print_success "Virtual environment activated"
}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-30}
    
    print_info "Waiting for $service_name to be ready..."
    
    local i=1
    while [ $i -le $timeout ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            print_success "$service_name is ready"
            return 0
        fi
        sleep 1
        i=$((i + 1))
    done
    
    print_error "$service_name is not ready after ${timeout}s"
    return 1
}

# Function to check API health
check_api_health() {
    local host=${1:-localhost}
    local port=${2:-8000}
    local timeout=${3:-30}
    
    print_info "Checking API health..."
    
    local i=1
    while [ $i -le $timeout ]; do
        if curl -s -f "http://$host:$port/v1/health" >/dev/null 2>&1; then
            print_success "API is healthy and responding"
            return 0
        fi
        sleep 2
        i=$((i + 1))
    done
    
    print_error "API health check failed after ${timeout}s"
    return 1
}

# Function to display startup information
show_startup_info() {
    local host=${1:-localhost}
    local port=${2:-8000}
    
    print_header "🚀 Custom Agent API Started Successfully!"
    
    echo -e "${GREEN}API Endpoints:${NC}"
    echo -e "  • API Base:        http://$host:$port"
    echo -e "  • Health Check:    http://$host:$port/v1/health"
    echo -e "  • API Docs:        http://$host:$port/docs"
    echo -e "  • Agents:          http://$host:$port/v1/agents"
    echo -e "  • Documents:       http://$host:$port/v1/documents"
    
    echo -e "\n${BLUE}Available Agents:${NC}"
    echo -e "  • doc_agent:       Document search and analysis"
    echo -e "  • web_agent:       Web search and current information"
    echo -e "  • reasoning_team:  Coordinated document + web search"
    
    echo -e "\n${YELLOW}Quick Commands:${NC}"
    echo -e "  • Test API:        curl http://$host:$port/v1/health"
    echo -e "  • List agents:     curl http://$host:$port/v1/agents"
    echo -e "  • Upload docs:     Use POST http://$host:$port/v1/documents/upload"
    echo -e "  • Process docs:    curl -X POST http://$host:$port/v1/documents/process"
    
    echo -e "\n${PURPLE}Logs and Monitoring:${NC}"
    echo -e "  • View logs:       tail -f logs/api.log (if logging to file)"
    echo -e "  • Stop service:    Ctrl+C (development) or docker-compose down (Docker)"
    
    echo -e "\n${CYAN}Documentation:${NC}"
    echo -e "  • Interactive API docs available at http://$host:$port/docs"
    echo -e "  • ReDoc available at http://$host:$port/redoc"
    echo
}

# Function to cleanup on exit
cleanup() {
    print_info "Cleaning up..."
    
    # Kill background processes if any
    jobs -p | xargs -r kill 2>/dev/null || true
    
    print_info "Cleanup completed"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM