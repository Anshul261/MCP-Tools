#!/bin/bash

echo "🚀 Starting Agent API Test Environment"
echo "======================================"

# Check if we're in the right directory
if [ ! -d "agent-api-main" ]; then
    echo "❌ agent-api-main directory not found!"
    echo "Please run this script from the AI-Search-MCP directory"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if API server is already running
if check_port 8000; then
    echo "✅ API server is already running on port 8000"
    echo "Proceeding with tests..."
else
    echo "🔄 Starting API server..."
    cd agent-api-main
    
    # Start the server in background
    nohup python -m uvicorn api.main:app --reload --port 8000 --host 0.0.0.0 > ../api_server.log 2>&1 &
    API_PID=$!
    echo "Server PID: $API_PID"
    
    cd ..
    
    # Wait for server to start
    echo "⏳ Waiting for server to start..."
    sleep 5
    
    # Check if server started successfully
    max_attempts=10
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ API server started successfully!"
            break
        else
            echo "Attempt $attempt/$max_attempts - Server not ready yet..."
            sleep 2
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Failed to start API server after $max_attempts attempts"
        echo "Check the log file: api_server.log"
        exit 1
    fi
fi

echo ""
echo "🧪 Available Test Commands:"
echo "=========================="
echo "1. Test all agents:       python test_detailed_breakdown.py"
echo "2. Quick test:           python test_detailed_breakdown.py quick"
echo "3. Compare responses:    python test_detailed_breakdown.py compare"
echo "4. List agents:          python test_detailed_breakdown.py agents"
echo "5. Show help:           python test_detailed_breakdown.py help"
echo ""

# Offer to run a quick test
read -p "🚀 Run a quick test now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running quick test..."
    python test_detailed_breakdown.py quick
fi

echo ""
echo "📋 Server Information:"
echo "====================="
echo "API URL: http://localhost:8000"
echo "Health Check: http://localhost:8000/health"
echo "API Docs: http://localhost:8000/docs"
echo "Server Log: api_server.log"
echo ""
echo "To stop the server:"
echo "pkill -f 'uvicorn api.main:app'"