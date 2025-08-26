#!/bin/bash
# scripts/start.sh - Main startup script

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/utils.sh"

print_header "Custom Agent API Startup"

# Change to project directory
cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_info "Creating .env file from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        create_env_file
    fi
    print_warning "Please update .env file with your credentials and run again"
    exit 1
fi

# Load environment variables
print_info "Loading environment variables..."
if ! load_env_vars; then
    print_error "Failed to load environment variables from .env file"
    print_info "Please check your .env file for syntax errors"
    print_info "Common issues:"
    print_info "  - Special characters in passwords (use quotes)"
    print_info "  - Unescaped semicolons, quotes, or backticks"
    print_info "  - Missing equals signs"
    exit 1
fi

# Validate required environment variables
print_info "Validating configuration..."
validate_env_vars

# Create necessary directories
print_info "Creating directories..."
mkdir -p documents converted_docs logs

# Choose startup method
if [ "${1:-}" = "--dev" ]; then
    print_info "Starting in development mode..."
    exec "$SCRIPT_DIR/dev_setup.sh"
elif [ "${1:-}" = "--docker" ]; then
    print_info "Starting with Docker..."
    exec "$SCRIPT_DIR/docker_start.sh"
else
    print_info "Starting in production mode..."
    exec "$SCRIPT_DIR/prod_start.sh"
fi