# ManageEngine IT Support Agent with AgentOS Integration

This unified agent system replaces the legacy agent architecture with AgentOS-based integration for improved session management, monitoring, and scalability.

## 📁 Directory Structure

```
managengine-agent/
├── agents/
│   └── unified_agents.py          # All agent definitions (creator, updater, viewer)
├── tools/
│   └── unified_tools.py           # Consolidated ManageEngine toolkit
├── team.py                      # Complete team with AgentOS integration
├── requirements.txt               # Dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your actual configuration values
```

### 3. Run Team (Simple)
```bash
# Start the team with AgentOS integration
python team.py
```

## 📡 API Endpoints

### AgentOS (port 7777)

- `GET /docs` - Interactive API documentation
- `GET /config` - AgentOS configuration
- `POST /agents/{agent_id}/runs` - Run specific agent
- `POST /teams/{team_id}/runs` - Run team

### Usage Examples

#### Running Team
```bash
python team.py
```

#### Team Functions
```python
from team import manageengine_team

# Run team with streaming
manageengine_team.print_response("I need help with my laptop", stream=True)

# Run team programmatically
response = manageengine_team.run("Help with password reset")
print(response.content)
```

## 🔧 Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/manageengine_db

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# ManageEngine
MANAGEENGINE_BASE_URL=https://your-domain.manageengine.com/api/v3
MANAGEENGINE_API_KEY=your_technician_key_here

# AgentOS
AGENTOS_SECURITY_KEY=your_security_key_here
```

### Optional Configuration

```bash
# Session Management
SESSION_TIMEOUT_SECONDS=86400  # 24 hours
MAX_CONCURRENT_SESSIONS=100

# Agent Behavior
DEFAULT_MODEL_TEMPERATURE=0.2
MAX_TOKENS=4000

# Performance
ENABLE_CACHING=True
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## 🤖 Agent Architecture

### Agent Types

1. **Ticket Creator Agent**
   - Creates new IT support tickets
   - Intelligent troubleshooting before ticket creation
   - Duplicate ticket detection
   - Automatic categorization and prioritization

2. **Ticket Updater Agent**
   - Updates existing ticket descriptions
   - Security validation (users can only update own tickets)
   - Status validation (only open tickets can be modified)

3. **Ticket Viewer Agent**
   - Displays user's own tickets
   - Status filtering (open/closed/all)
   - Formatted table output
   - Resolution details for closed tickets

### Team Coordinator

The **ManageEngine Helpdesk Team** coordinates all agents with:
- Intelligent request routing
- Security validation
- Session state management
- User authentication context
- Transparent decision-making with reasoning tools

## 🔄 Migration Benefits

### From Legacy System

| Feature | Legacy | AgentOS Integration |
|----------|----------|---------------------|
| Session Management | Custom database sessions | AgentOS built-in sessions |
| Agent Communication | WebSocket only | Multiple interfaces (REST, WebSocket, Streaming) |
| Monitoring | Limited logs | Comprehensive AgentOS monitoring |
| Scalability | Single process | Distributed AgentOS architecture |
| Error Handling | Basic | Advanced with retries and circuit breakers |
| Security | Custom validation | AgentOS RBAC and JWT tokens |

### Key Improvements

1. **Unified Architecture**: Single source of truth for agent configuration
2. **Better Monitoring**: AgentOS provides comprehensive metrics and tracing
3. **Improved Performance**: Async operations and connection pooling
4. **Enhanced Security**: Role-based access control and token-based authentication
5. **Scalability**: Designed for horizontal scaling and load balancing
6. **Developer Experience**: Rich documentation and interactive API explorer

## 🧪 Testing

### Health Checks
```bash
# Check API server
curl http://localhost:8000/health

# Check AgentOS server
curl http://localhost:7777/health
```

### Agent Communication Test
```bash
# Send message to agents
curl -X POST http://localhost:8000/agentos/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help with my laptop",
    "user_id": "123",
    "user_name": "John Doe"
  }'
```

### Session Management Test
```bash
# Create session
curl -X POST http://localhost:8000/agentos/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123",
    "user_name": "John Doe"
  }'
```

## 📊 Monitoring

### Available Metrics

- Agent execution time
- Token usage and costs
- Session duration and activity
- Error rates and types
- API request patterns
- Resource utilization

### Access Points

- **API Server**: `http://localhost:8000/docs`
- **AgentOS Interface**: `http://localhost:7777`
- **AgentOS API Docs**: `http://localhost:7777/docs`

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
2. **Database Connection**: Check `DATABASE_URL` format and database availability
3. **ManageEngine API**: Verify `MANAGEENGINE_API_KEY` and network connectivity
4. **AgentOS Connection**: Ensure AgentOS server is running on port 7777

### Debug Mode

Enable debug logging by setting:
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

## 🔄 Development Workflow

### Making Changes

1. Modify agent definitions in `agents/unified_agents.py`
2. Update tools in `tools/unified_tools.py`
3. Test changes with both servers running
4. Monitor AgentOS logs for performance impact

### Adding New Agents

1. Define agent function in `agents/unified_agents.py`
2. Add to `AGENT_REGISTRY`
3. Update team instructions in `agentos_integration.py`
4. Test with AgentOS API endpoints

## 📚 Additional Resources

- [AgentOS Documentation](https://docs.agno.com/agent-os/introduction)
- [Agno Framework Docs](https://docs.agno.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ManageEngine API Docs](https://www.manageengine.com/products/service-desk/sdpod-v3-api/)

## 🤝 Support

For issues with:
- **AgentOS Integration**: Check AgentOS logs at port 7777
- **API Routes**: Check FastAPI logs at port 8000
- **Agent Logic**: Review agent instructions and tool outputs
- **External APIs**: Verify ManageEngine and Azure OpenAI connectivity