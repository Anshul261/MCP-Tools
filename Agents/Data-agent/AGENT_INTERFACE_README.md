# Data Agent Interface

A custom FastAPI application that provides a web-based interface for the Data Agent system, integrating seamlessly with the existing AgentOS setup.

## Features

### 🎯 Core Functionality
- **Interactive Dashboard**: Web-based interface for data analysis and visualization
- **Multi-Agent Integration**: Seamless integration with existing agents (data_analyst, viz_specialist, analysis_team)
- **Real-time Query Execution**: Execute custom data analysis queries through the agents
- **Dynamic Visualizations**: Generate new charts and dashboards on demand
- **File Management**: Upload and process new data files
- **Export Capabilities**: Export data and visualizations in multiple formats

### 🛠️ Technical Features
- **FastAPI Framework**: High-performance API with automatic documentation
- **AgentOS Integration**: Preserves all existing agent functionality
- **Database Integration**: Uses existing PostgreSQL database setup
- **Static File Serving**: Serves generated visualizations and assets
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Error Handling**: Comprehensive error handling and response models

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database running on localhost:5532
- All dependencies from the existing agent.py setup
- Azure OpenAI API credentials in `.env` file

### Quick Start

1. **Start the Interface**:
   ```bash
   python start_interface.py
   ```

2. **Access the Dashboard**:
   - Main Dashboard: http://localhost:7778/dashboard
   - API Documentation: http://localhost:7778/docs
   - AgentOS Interface: http://localhost:7778/

## API Endpoints

### 📊 Dashboard Endpoints

#### `GET /dashboard`
Main dashboard interface with interactive web UI.

#### `GET /health`
Health check endpoint for system monitoring.
```json
{
  "status": "healthy",
  "agents_status": {
    "data_analyst": "active",
    "viz_specialist": "active",
    "analysis_team": "active"
  },
  "database_status": "connected",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 🔍 Data Analysis Endpoints

#### `POST /query`
Execute custom data queries via the agents.
```json
{
  "query": "Show me ticket trends by month",
  "agent_type": "data_analyst"
}
```

Response:
```json
{
  "success": true,
  "result": "Analysis results...",
  "agent_used": "data_analyst",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### `POST /visualize`
Generate new visualizations.
```json
{
  "chart_type": "bar",
  "data_query": "tickets by category",
  "title": "Ticket Distribution",
  "description": "Analysis of ticket categories"
}
```

### 📁 File Management Endpoints

#### `POST /upload`
Upload new data files (CSV, XLSX, XLS).
- Supports multipart/form-data
- Automatically processes data files
- Updates DuckDB tables

#### `GET /export/{format}`
Export data/visualizations in specified format.
- Supported formats: `csv`, `json`, `html`
- Downloads generated files

### 🔧 Utility Endpoints

#### `GET /api/data/summary`
Get summary information about loaded data.

#### `GET /api/visualizations/list`
List all available visualizations with metadata.

## Agent Integration

### Existing Agents
The interface integrates with your existing agents:

1. **Data Analyst**: Specialized for SQL queries and data analysis
2. **Visualization Specialist**: Creates HTML dashboards with Chart.js/D3.js
3. **Analysis Team**: Combined team for complex multi-step analysis

### Agent Selection
- Queries containing visualization keywords automatically use the viz specialist
- Complex analysis can be routed to the analysis team
- Default routing goes to the data analyst

## Usage Examples

### 1. Basic Data Query
```javascript
// Execute a data analysis query
fetch('/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: "What are the top 5 ticket categories by volume?",
    agent_type: "data_analyst"
  })
})
```

### 2. Create Visualization
```javascript
// Generate a new chart
fetch('/visualize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    chart_type: "pie",
    data_query: "ticket status distribution",
    title: "Ticket Status Overview"
  })
})
```

### 3. Upload Data File
```javascript
// Upload a new data file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/upload', {
  method: 'POST',
  body: formData
})
```

## Configuration

### Environment Variables
The interface uses the same environment variables as your existing setup:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `OPENAI_API_VERSION`

### Database Configuration
- Uses the existing PostgreSQL setup: `postgresql+psycopg://ai:ai@localhost:5532/ai`
- Integrates with existing DuckDB tools for data processing

### File Structure
```
Data-agent/
├── agent_interface.py          # Main FastAPI application
├── start_interface.py          # Startup script
├── agent.py                    # Original AgentOS setup
├── output/                     # Generated visualizations
├── static/                     # Static assets (CSS, JS, images)
├── uploads/                    # Uploaded data files
└── .env                       # Environment variables
```

## Development

### Running in Development Mode
```bash
python start_interface.py
```

### Running in Production Mode
```bash
uvicorn agent_interface:app --host 0.0.0.0 --port 7778
```

### API Documentation
Once running, visit http://localhost:7778/docs for interactive API documentation.

## Integration with Existing Setup

The interface is designed to work alongside your existing `agent.py`:

1. **Preserves Existing Functionality**: All original agents and teams remain unchanged
2. **Database Integration**: Uses the same PostgreSQL database and DuckDB tools
3. **No Conflicts**: Runs on port 7778 while original setup can run on 7777
4. **Shared Resources**: Uses the same output folder and data files

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Kill process using port 7778
   lsof -ti:7778 | xargs kill -9
   ```

2. **Database Connection Issues**:
   - Ensure PostgreSQL is running on localhost:5532
   - Check database credentials in `.env` file

3. **Missing Dependencies**:
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

4. **File Upload Issues**:
   - Ensure `uploads/` directory exists and is writable
   - Check file format (only CSV, XLSX, XLS supported)

### Logging
The application provides detailed logging. Check console output for debugging information.

## Contributing

The interface is designed to be extensible. You can:
- Add new endpoints in `agent_interface.py`
- Modify the dashboard HTML in the `/dashboard` endpoint
- Add new response models using Pydantic
- Extend agent integration patterns

## License

Same license as the parent Data Agent project.