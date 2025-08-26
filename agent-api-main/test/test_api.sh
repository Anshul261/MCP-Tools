#!/bin/bash
# scripts/test_api.sh - Test if the API is working

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Testing Custom Agent API ===${NC}\n"

# Get API configuration
API_HOST=${API_HOST:-localhost}
API_PORT=${API_PORT:-8000}
BASE_URL="http://$API_HOST:$API_PORT"

echo -e "${BLUE}Testing API at: $BASE_URL${NC}\n"

# Test 1: Basic connectivity
echo -e "${YELLOW}1. Testing basic connectivity...${NC}"
if curl -s -f "$BASE_URL" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${RED}✗ API is not responding${NC}"
    echo "   Make sure the server is running on port $API_PORT"
    exit 1
fi

# Test 2: Health check
echo -e "\n${YELLOW}2. Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/v1/health" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Health endpoint working${NC}"
    echo "   Response: $(echo $HEALTH_RESPONSE | head -c 100)..."
else
    echo -e "${RED}✗ Health endpoint failed${NC}"
fi

# Test 3: List agents
echo -e "\n${YELLOW}3. Testing agents endpoint...${NC}"
AGENTS_RESPONSE=$(curl -s "$BASE_URL/v1/agents" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Agents endpoint working${NC}"
    echo "   Available agents: $AGENTS_RESPONSE"
else
    echo -e "${RED}✗ Agents endpoint failed${NC}"
fi

# Test 4: Document stats
echo -e "\n${YELLOW}4. Testing documents endpoint...${NC}"
DOCS_RESPONSE=$(curl -s "$BASE_URL/v1/documents/stats" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Documents endpoint working${NC}"
    echo "   Document stats: $(echo $DOCS_RESPONSE | head -c 100)..."
else
    echo -e "${RED}✗ Documents endpoint failed${NC}"
fi

# Test 5: API Documentation
echo -e "\n${YELLOW}5. Testing API documentation...${NC}"
if curl -s -f "$BASE_URL/docs" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ API docs available${NC}"
    echo -e "   View at: ${BLUE}$BASE_URL/docs${NC}"
else
    echo -e "${RED}✗ API docs not available${NC}"
fi

# Summary
echo -e "\n${BLUE}=== API Status Summary ===${NC}"
echo -e "${GREEN}API Base URL:${NC}      $BASE_URL"
echo -e "${GREEN}Health Check:${NC}      $BASE_URL/v1/health"
echo -e "${GREEN}API Documentation:${NC} $BASE_URL/docs"
echo -e "${GREEN}Available Endpoints:${NC}"
echo "  • GET  /v1/agents           - List available agents"
echo "  • POST /v1/agents/{id}/chat - Chat with an agent"
echo "  • GET  /v1/documents/stats  - Document statistics"
echo "  • POST /v1/documents/upload - Upload documents"
echo "  • POST /v1/documents/process - Process documents"

echo -e "\n${YELLOW}Quick test commands:${NC}"
echo "curl $BASE_URL/v1/health"
echo "curl $BASE_URL/v1/agents"
echo "curl $BASE_URL/v1/documents/stats"

echo -e "\n${BLUE}To test agent chat:${NC}"
cat << EOF
curl -X POST $BASE_URL/v1/agents/web_agent/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Hello, can you help me?",
    "user_id": "test_user",
    "stream": false
  }'
EOF

echo -e "\n${GREEN}API is ready for use!${NC}"