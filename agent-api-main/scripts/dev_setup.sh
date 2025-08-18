#!/bin/bash
# scripts/dev_setup.sh - Development environment setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"

print_header "Development Environment Setup"

# Check system requirements
check_system_requirements

# Create virtual environment
create_venv

# Install dependencies
print_step "Installing development dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Requirements installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Install development dependencies if available
if grep -q "dev" pyproject.toml 2>/dev/null; then
    print_info "Installing development dependencies..."
    pip install -e ".[dev]"
    print_success "Development dependencies installed"
fi

# Create development directories
print_step "Creating development directories..."
mkdir -p logs
mkdir -p documents
mkdir -p converted_docs
mkdir -p tests/data
print_success "Development directories created"

# Set up pre-commit hooks (if available)
if command_exists pre-commit && [ -f ".pre-commit-config.yaml" ]; then
    print_info "Setting up pre-commit hooks..."
    pre-commit install
    print_success "Pre-commit hooks installed"
fi

print_header "Starting Development Server"

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

# Start the development server
print_info "Starting development server with auto-reload..."
print_info "Server will restart automatically when code changes are detected"

export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start the server with development settings
python -m uvicorn api.main:app \
    --host "${API_HOST:-0.0.0.0}" \
    --port "${API_PORT:-8000}" \
    --reload \
    --reload-dir . \
    --log-level debug \
    --access-log \
    --use-colors &

SERVER_PID=$!

# Wait for the server to start
sleep 5

# Check if server started successfully
if check_api_health "${API_HOST:-localhost}" "${API_PORT:-8000}" 10; then
    show_startup_info "${API_HOST:-localhost}" "${API_PORT:-8000}"
    
    print_header "Development Server Running"
    print_info "Press Ctrl+C to stop the server"
    
    # Wait for the server process
    wait $SERVER_PID
else
    print_error "Failed to start development server"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi