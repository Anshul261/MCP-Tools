#!/bin/bash
# scripts/prod_start.sh - Production startup script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"

print_header "Production Server Startup"

# Check system requirements
check_system_requirements

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    create_venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
install_python_deps

# Load environment variables
if [ -f ".env" ]; then
    if ! load_env_vars; then
        print_error "Failed to load environment variables. Please check your .env file."
        exit 1
    fi
else
    print_error ".env file not found. Please run ./scripts/start.sh first to create it."
    exit 1
fi

# Create necessary directories
print_step "Creating production directories..."
mkdir -p logs
mkdir -p documents
mkdir -p converted_docs
print_success "Production directories created"

# Set production environment variables
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export API_DEBUG=false

print_header "Starting Production Server"

# Start the production server
print_info "Starting production server..."

# Use gunicorn for production if available, otherwise uvicorn
if command_exists gunicorn; then
    print_info "Using Gunicorn WSGI server"
    
    # Calculate number of workers (2 * CPU cores + 1)
    WORKERS=${WORKERS:-$(($(nproc) * 2 + 1))}
    
    exec gunicorn api.main:app \
        -w $WORKERS \
        -k uvicorn.workers.UvicornWorker \
        --bind "${API_HOST:-0.0.0.0}:${API_PORT:-8000}" \
        --timeout 120 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info \
        --capture-output \
        --enable-stdio-inheritance
else
    print_info "Using Uvicorn ASGI server"
    
    exec python -m uvicorn api.main:app \
        --host "${API_HOST:-0.0.0.0}" \
        --port "${API_PORT:-8000}" \
        --workers "${WORKERS:-1}" \
        --log-level info \
        --access-log \
        --no-use-colors \
        --loop uvloop \
        --http httptools
fi