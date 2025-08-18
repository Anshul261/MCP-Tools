#!/bin/bash
# scripts/docker_start.sh - Docker deployment script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"

print_header "Docker Deployment"

# Check if Docker is available
if ! command_exists docker; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check for Docker Compose
COMPOSE_CMD=""
if command_exists docker-compose; then
    COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available"
    exit 1
fi

print_info "Using Docker Compose command: $COMPOSE_CMD"

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

# Create necessary directories for volume mounts
print_step "Creating directories for Docker volumes..."
mkdir -p documents
mkdir -p converted_docs
mkdir -p logs
print_success "Directories created"

# Build and start services
print_step "Building and starting Docker services..."

if [ "${1:-}" = "--build" ]; then
    print_info "Building Docker images..."
    $COMPOSE_CMD build --no-cache
fi

print_info "Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
print_step "Waiting for services to be ready..."

# Wait for API service
if wait_for_service "${API_HOST:-localhost}" "${API_PORT:-8000}" "API" 60; then
    # Additional health check
    if check_api_health "${API_HOST:-localhost}" "${API_PORT:-8000}" 30; then
        show_startup_info "${API_HOST:-localhost}" "${API_PORT:-8000}"
        
        print_header "Docker Services Status"
        $COMPOSE_CMD ps
        
        print_header "Service Logs"
        print_info "To view real-time logs:"
        echo "  $COMPOSE_CMD logs -f"
        echo "  $COMPOSE_CMD logs -f api"
        
        print_info "To stop services:"
        echo "  $COMPOSE_CMD down"
        
        print_info "To rebuild and restart:"
        echo "  $0 --build"
        
    else
        print_error "API health check failed"
        print_info "Checking service logs..."
        $COMPOSE_CMD logs api
        exit 1
    fi
else
    print_error "Services failed to start"
    print_info "Checking service status..."
    $COMPOSE_CMD ps
    print_info "Checking service logs..."
    $COMPOSE_CMD logs
    exit 1
fi