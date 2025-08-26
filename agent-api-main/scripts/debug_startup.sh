#!/bin/bash
# scripts/debug_startup.sh - Debug server startup issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"

print_header "Debug Server Startup"

# Load environment variables
if ! load_env_vars; then
    print_error "Failed to load environment variables"
    exit 1
fi

# Check error logs first
print_step "Checking error logs..."
if [ -f "logs/error.log" ]; then
    print_info "Last 20 lines of error log:"
    echo "----------------------------------------"
    tail -n 20 logs/error.log
    echo "----------------------------------------"
else
    print_info "No error log found"
fi

# Test basic Python imports
print_step "Testing Python imports..."
echo "Testing basic imports..."

python3 << 'EOF'
import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Test basic imports
try:
    import fastapi
    print("✓ FastAPI import successful")
except ImportError as e:
    print(f"✗ FastAPI import failed: {e}")

try:
    import uvicorn
    print("✓ Uvicorn import successful")
except ImportError as e:
    print(f"✗ Uvicorn import failed: {e}")

try:
    import agno
    print("✓ Agno import successful")
except ImportError as e:
    print(f"✗ Agno import failed: {e}")

try:
    import docling
    print("✓ Docling import successful")
except ImportError as e:
    print(f"✗ Docling import failed: {e}")

try:
    import transformers
    print("✓ Transformers import successful")
except ImportError as e:
    print(f"✗ Transformers import failed: {e}")
EOF

# Test application imports
print_step "Testing application imports..."
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from core.config import settings
    print("✓ Core config import successful")
except Exception as e:
    print(f"✗ Core config import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from core.database import db_manager
    print("✓ Database manager import successful")
except Exception as e:
    print(f"✗ Database manager import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from agents.selector import get_available_agents
    print("✓ Agents selector import successful")
    agents = get_available_agents()
    print(f"  Available agents: {agents}")
except Exception as e:
    print(f"✗ Agents selector import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from api.main import app
    print("✓ Main application import successful")
except Exception as e:
    print(f"✗ Main application import failed: {e}")
    import traceback
    traceback.print_exc()
EOF

# Test database connection
print_step "Testing database connection..."
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from core.database import db_manager
    health = db_manager.health_check()
    print(f"Database health: {health}")
except Exception as e:
    print(f"Database connection failed: {e}")
    import traceback
    traceback.print_exc()
EOF

# Try starting with uvicorn directly (no gunicorn)
print_step "Testing direct uvicorn startup..."
print_info "Attempting to start with uvicorn directly for better error messages..."

export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start uvicorn with verbose logging
python3 -m uvicorn api.main:app \
    --host "${API_HOST:-0.0.0.0}" \
    --port "${API_PORT:-8000}" \
    --log-level debug \
    --no-access-log \
    --timeout-keep-alive 5 &

SERVER_PID=$!

# Wait a bit and check if it started
sleep 5

if kill -0 $SERVER_PID 2>/dev/null; then
    print_success "Server started successfully with uvicorn!"
    print_info "Server PID: $SERVER_PID"
    print_info "Testing API response..."
    
    # Test the API
    if curl -s -f "http://localhost:${API_PORT:-8000}/v1/health" >/dev/null 2>&1; then
        print_success "API is responding!"
        print_info "API URL: http://localhost:${API_PORT:-8000}"
        print_info "API Docs: http://localhost:${API_PORT:-8000}/docs"
        
        print_header "Server is running successfully!"
        print_info "Press Ctrl+C to stop the server"
        
        # Wait for the server
        wait $SERVER_PID
    else
        print_warning "Server started but API is not responding"
        kill $SERVER_PID 2>/dev/null || true
    fi
else
    print_error "Server failed to start with uvicorn"
    print_info "Check the output above for error details"
fi