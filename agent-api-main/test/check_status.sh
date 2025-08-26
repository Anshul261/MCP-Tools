#!/bin/bash
# scripts/check_status.sh - Check API server status

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Custom Agent API Status Check ===${NC}\n"

# Check if server process is running
API_PORT=${API_PORT:-8000}
echo -e "${YELLOW}Checking server process...${NC}"

# Check for running processes on the API port
PROCESS_CHECK=$(lsof -i :$API_PORT 2>/dev/null)
if [ -n "$PROCESS_CHECK" ]; then
    echo -e "${GREEN}✓ Server process found on port $API_PORT${NC}"
    echo "$PROCESS_CHECK"
else
    echo -e "${RED}✗ No server process found on port $API_PORT${NC}"
    echo "The server may not be running or using a different port"
fi

echo ""

# Check API responsiveness
API_HOST=${API_HOST:-localhost}
BASE_URL="http://$API_HOST:$API_PORT"

echo -e "${YELLOW}Checking API responsiveness...${NC}"
if timeout 5 curl -s -f "$BASE_URL/v1/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding at $BASE_URL${NC}"
    
    # Get detailed health info
    echo -e "\n${YELLOW}Health Status:${NC}"
    curl -s "$BASE_URL/v1/health" | python3 -m json.tool 2>/dev/null || echo "Health check returned non-JSON response"
    
else
    echo -e "${RED}✗ API is not responding at $BASE_URL${NC}"
    echo "Possible issues:"
    echo "  - Server not started"
    echo "  - Wrong host/port configuration"
    echo "  - Firewall blocking connections"
    echo "  - Server crashed or failed to start"
fi

echo -e "\n${YELLOW}Log files (if they exist):${NC}"
if [ -d "logs" ]; then
    ls -la logs/ 2>/dev/null || echo "No log files found"
    
    if [ -f "logs/error.log" ]; then
        echo -e "\n${YELLOW}Recent error log entries:${NC}"
        tail -n 5 logs/error.log
    fi
    
    if [ -f "logs/access.log" ]; then
        echo -e "\n${YELLOW}Recent access log entries:${NC}"
        tail -n 5 logs/access.log
    fi
else
    echo "No logs directory found"
fi

echo -e "\n${YELLOW}Environment check:${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
else
    echo -e "${RED}✗ .env file missing${NC}"
fi

if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠ No virtual environment found${NC}"
fi

echo -e "\n${BLUE}=== Quick Actions ===${NC}"
echo "To view server logs in real-time:"
echo "  tail -f logs/error.log"
echo ""
echo "To restart the server:"
echo "  pkill -f 'gunicorn.*api.main:app'"
echo "  ./scripts/start.sh"
echo ""
echo "To test the API:"
echo "  ./scripts/test_api.sh"
echo ""
echo "To stop the server:"
echo "  pkill -f 'gunicorn.*api.main:app'"