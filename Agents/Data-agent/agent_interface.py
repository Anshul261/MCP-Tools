import os
import json
import asyncio
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rich.console import Console

# Import AgentOS components
from agno.tools.python import PythonTools
from agno.agent import Agent
from agno.os import AgentOS
from agno.team import Team
from agno.tools.duckdb import DuckDbTools
from agno.models.azure import AzureOpenAI
from agno.tools.reasoning import ReasoningTools
from agno.db.postgres import PostgresDb

# Load environment variables
load_dotenv()
console = Console()

# Database configuration
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db = PostgresDb(db_url=db_url)
u_id = "anshulraj@gmail.com"

# Data processor class
class DataProcessor:
    """Simple data preprocessing for Excel/CSV files"""
    
    @staticmethod
    def clean_and_infer_types(file_path):
        """Load file and infer proper data types"""
        console.print(f"[blue]Processing file: {file_path}[/blue]")
        
        if file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        
        # Basic data cleaning
        original_rows = len(df)
        df = df.dropna(how='all')
        console.print(f"[green]Cleaned data: {len(df)}/{original_rows} rows retained[/green]")
        
        # Infer and convert data types with proper error handling
        for col in df.columns:
            # Try to convert to datetime if column name suggests it's a date
            if any(word in col.lower() for word in ['date', 'time', 'created', 'updated', 'resolved']):
                try:
                    df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    pass  # Keep as original type if conversion fails
            
            # Try to convert to numeric if possible
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass  # Keep as string if conversion fails
        
        # Save as CSV for DuckDB
        csv_path = file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
        df.to_csv(csv_path, index=False)
        
        return csv_path, df.dtypes.to_dict()

# Pydantic models for API requests and responses
class QueryRequest(BaseModel):
    query: str
    agent_type: Optional[str] = "data_analyst"

class QueryResponse(BaseModel):
    success: bool
    result: Any
    agent_used: str
    timestamp: datetime

class VisualizationRequest(BaseModel):
    chart_type: str
    data_query: str
    title: Optional[str] = None
    description: Optional[str] = None

class VisualizationResponse(BaseModel):
    success: bool
    file_path: str
    file_name: str
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    agents_status: Dict[str, str]
    database_status: str
    timestamp: datetime

class DashboardData(BaseModel):
    total_records: int
    recent_uploads: List[str]
    available_visualizations: List[str]
    agent_status: Dict[str, str]

# Initialize data processor and load default data
processor = DataProcessor()
default_file_path = "Alpha-NOC-Reports-Jan-to-Apr-2025.xlsx"

# Check if default file exists, if not skip initialization
csv_path = None
column_types = {}
if os.path.exists(default_file_path):
    csv_path, column_types = processor.clean_and_infer_types(default_file_path)

# Initialize tools
duckdb_tools = DuckDbTools()
python_tools = PythonTools()
reasoning_tools = ReasoningTools()

# Load processed data if available
if csv_path and os.path.exists(csv_path):
    duckdb_tools.create_table_from_path(path=csv_path, table="data")

# Initialize Azure OpenAI model
azure_model = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# Data Analysis Agent - specialized for querying and basic analysis
data_analyst = Agent(
    name="Data Analyst",
    model=azure_model,
    tools=[duckdb_tools],
    instructions=[
        "You are a data analyst with access to a 'data' table containing ticket/support request data.",
        f"The data table has columns: {list(column_types.keys()) if column_types else 'No data loaded yet'}",
        "Always use SQL queries to analyze the actual data in the 'data' table.",
        "Provide detailed analysis with specific numbers and insights from the data.",
        "When analyzing trends, use date functions on the 'Created Time' column if available.",
        "Focus on real patterns in the actual data, not hypothetical scenarios.",
    ],
)

# Visualization Agent - specialized for creating charts
viz_specialist = Agent(
    name="Visualization Specialist",
    model=azure_model,
    tools=[python_tools, duckdb_tools],
    instructions=[
        "You are a visualization specialist with access to the 'data' table and Python tools.",
        "Use DuckDB to query data and Python to generate clean HTML/CSS/JavaScript dashboards.",
        "Create professional web-based dashboards using Chart.js or D3.js instead of Plotly.",
        "Generate clean HTML files with embedded CSS and JavaScript for beautiful layouts.",
        "Focus on card-based layouts, proper spacing, and responsive design.",
        "Always save dashboards as HTML files in the output folder.",
        "Include data insights as text elements within the dashboard.",
        "Use modern web design principles with clean typography and colors.",
    ],
)

# Analysis team combining both agents
analysis_team = Team(
    name="Data Analysis Team",
    db=db,
    model=azure_model,
    members=[data_analyst, viz_specialist],
    tools=[reasoning_tools],
    instructions=[
        f"You have access to a 'data' table with {len(column_types)} columns of ticket/support data.",
        f"Column types: {column_types}",
        "ALWAYS query the actual data table using SQL before providing any analysis.",
        "Data Analyst: Run SQL queries on the 'data' table to find real patterns and trends.",
        "Visualization Specialist: Use query results to create meaningful charts and save them to output folder.",
        "Provide concrete insights based on actual data, not hypothetical scenarios.",
        "Focus on time-based trends using timestamp columns for temporal analysis.",
    ],
    enable_user_memories=True,
    enable_session_summaries=True,
    markdown=True,
    stream_member_events=True,
    enable_agentic_memory=True,
)

# Initialize AgentOS
agent_os = AgentOS(
    os_id="data-agent-interface",
    description="Data Analysis Agent OS with Custom FastAPI Interface",
    agents=[viz_specialist, data_analyst],
    teams=[analysis_team]
)

# Get the FastAPI app from AgentOS
app = agent_os.get_app()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("output", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

# Custom endpoints

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard interface"""
    try:
        # Get statistics about available data
        total_records = 0
        if csv_path and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            total_records = len(df)
        
        # Get available visualizations
        output_files = []
        if os.path.exists("output"):
            output_files = [f for f in os.listdir("output") if f.endswith('.html')]
        
        # Get recent uploads
        upload_files = []
        if os.path.exists("uploads"):
            upload_files = [f for f in os.listdir("uploads")]
        
        dashboard_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Agent Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    color: #333;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                    text-align: center;
                    transition: transform 0.2s;
                }}
                .stat-card:hover {{
                    transform: translateY(-5px);
                }}
                .stat-number {{
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 10px;
                }}
                .stat-label {{
                    color: #666;
                    font-size: 1.1em;
                }}
                .action-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .action-card {{
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                }}
                .action-title {{
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: #333;
                }}
                .btn {{
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 1em;
                    margin: 5px;
                    transition: all 0.2s;
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .file-list {{
                    max-height: 200px;
                    overflow-y: auto;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                }}
                .file-item {{
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                    cursor: pointer;
                }}
                .file-item:hover {{
                    background: #f5f5f5;
                }}
                textarea, input {{
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    font-size: 1em;
                    margin: 10px 0;
                }}
                .query-section {{
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Data Agent Dashboard</h1>
                    <p>Intelligent Data Analysis & Visualization Platform</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{total_records:,}</div>
                        <div class="stat-label">Total Records</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(output_files)}</div>
                        <div class="stat-label">Visualizations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(upload_files)}</div>
                        <div class="stat-label">Uploaded Files</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">3</div>
                        <div class="stat-label">Active Agents</div>
                    </div>
                </div>
                
                <div class="query-section">
                    <h2>🔍 Quick Data Query</h2>
                    <textarea id="queryText" rows="3" placeholder="Enter your data analysis question (e.g., 'Show me ticket trends by month')"></textarea>
                    <button class="btn" onclick="executeQuery()">Execute Query</button>
                    <div id="queryResult" style="margin-top: 15px; padding: 15px; background: #f9f9f9; border-radius: 8px; display: none;"></div>
                </div>
                
                <div class="action-grid">
                    <div class="action-card">
                        <div class="action-title">📊 Available Visualizations</div>
                        <div class="file-list">
                            {''.join([f'<div class="file-item" onclick="openVisualization(\'{f}\')">{f}</div>' for f in output_files]) if output_files else '<p>No visualizations available yet</p>'}
                        </div>
                        <button class="btn" onclick="createVisualization()">Create New Visualization</button>
                    </div>
                    
                    <div class="action-card">
                        <div class="action-title">📁 Data Management</div>
                        <input type="file" id="fileInput" accept=".csv,.xlsx,.xls" style="margin-bottom: 10px;">
                        <button class="btn" onclick="uploadFile()">Upload Data File</button>
                        <div class="file-list">
                            {''.join([f'<div class="file-item">{f}</div>' for f in upload_files]) if upload_files else '<p>No uploaded files</p>'}
                        </div>
                    </div>
                    
                    <div class="action-card">
                        <div class="action-title">⚡ Quick Actions</div>
                        <button class="btn" onclick="exportData('csv')">Export as CSV</button>
                        <button class="btn" onclick="exportData('json')">Export as JSON</button>
                        <button class="btn" onclick="checkHealth()">Health Check</button>
                        <button class="btn" onclick="refreshDashboard()">Refresh Dashboard</button>
                    </div>
                </div>
            </div>
            
            <script>
                async function executeQuery() {{
                    const query = document.getElementById('queryText').value;
                    if (!query) return;
                    
                    const resultDiv = document.getElementById('queryResult');
                    resultDiv.innerHTML = '<p>Executing query...</p>';
                    resultDiv.style.display = 'block';
                    
                    try {{
                        const response = await fetch('/query', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{query: query}})
                        }});
                        const data = await response.json();
                        
                        if (data.success) {{
                            resultDiv.innerHTML = `<pre>${{JSON.stringify(data.result, null, 2)}}</pre>`;
                        }} else {{
                            resultDiv.innerHTML = `<p style="color: red;">Error: ${{data.error || 'Unknown error'}}</p>`;
                        }}
                    }} catch (error) {{
                        resultDiv.innerHTML = `<p style="color: red;">Error: ${{error.message}}</p>`;
                    }}
                }}
                
                function openVisualization(filename) {{
                    window.open(`/output/${{filename}}`, '_blank');
                }}
                
                function createVisualization() {{
                    const chartType = prompt('Enter chart type (bar, line, pie, etc.):');
                    const dataQuery = prompt('Enter data query for visualization:');
                    if (chartType && dataQuery) {{
                        fetch('/visualize', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{
                                chart_type: chartType,
                                data_query: dataQuery,
                                title: `${{chartType}} Chart`
                            }})
                        }}).then(response => response.json())
                          .then(data => {{
                              if (data.success) {{
                                  alert(`Visualization created: ${{data.file_name}}`);
                                  location.reload();
                              }} else {{
                                  alert('Error creating visualization');
                              }}
                          }});
                    }}
                }}
                
                async function uploadFile() {{
                    const fileInput = document.getElementById('fileInput');
                    const file = fileInput.files[0];
                    if (!file) return;
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    try {{
                        const response = await fetch('/upload', {{
                            method: 'POST',
                            body: formData
                        }});
                        const data = await response.json();
                        
                        if (data.success) {{
                            alert(`File uploaded successfully: ${{data.filename}}`);
                            location.reload();
                        }} else {{
                            alert(`Error uploading file: ${{data.error}}`);
                        }}
                    }} catch (error) {{
                        alert(`Error: ${{error.message}}`);
                    }}
                }}
                
                function exportData(format) {{
                    window.open(`/export/${{format}}`, '_blank');
                }}
                
                async function checkHealth() {{
                    try {{
                        const response = await fetch('/health');
                        const data = await response.json();
                        alert(`System Status: ${{data.status}}\\nDatabase: ${{data.database_status}}`);
                    }} catch (error) {{
                        alert(`Health check failed: ${{error.message}}`);
                    }}
                }}
                
                function refreshDashboard() {{
                    location.reload();
                }}
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=dashboard_html)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute custom data queries via the agents"""
    try:
        # Select appropriate agent
        if request.agent_type == "visualization" or "chart" in request.query.lower() or "plot" in request.query.lower():
            agent = viz_specialist
            agent_used = "visualization_specialist"
        elif request.agent_type == "team":
            # Use the analysis team for complex queries
            response = analysis_team.run(request.query, user_id=u_id)
            return QueryResponse(
                success=True,
                result=response.content,
                agent_used="analysis_team",
                timestamp=datetime.now()
            )
        else:
            agent = data_analyst
            agent_used = "data_analyst"
        
        # Execute query
        response = agent.run(request.query, user_id=u_id)
        
        return QueryResponse(
            success=True,
            result=response.content,
            agent_used=agent_used,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        return QueryResponse(
            success=False,
            result=f"Query execution failed: {str(e)}",
            agent_used=request.agent_type,
            timestamp=datetime.now()
        )

@app.post("/visualize", response_model=VisualizationResponse)
async def create_visualization(request: VisualizationRequest):
    """Generate new visualizations"""
    try:
        # Create visualization prompt
        viz_prompt = f"""
        Create a {request.chart_type} visualization based on this data query: {request.data_query}
        Title: {request.title or f"{request.chart_type.title()} Chart"}
        Description: {request.description or f"Visualization of {request.data_query}"}
        
        Use the visualization specialist tools to:
        1. Query the data using SQL
        2. Create a professional HTML dashboard with the chart
        3. Save it to the output folder with a meaningful filename
        4. Use modern web design with Chart.js or D3.js
        """
        
        # Execute visualization request
        response = viz_specialist.run(viz_prompt, user_id=u_id)
        
        # Find the most recent HTML file in output folder
        output_dir = Path("output")
        html_files = list(output_dir.glob("*.html"))
        if html_files:
            latest_file = max(html_files, key=lambda f: f.stat().st_mtime)
            
            return VisualizationResponse(
                success=True,
                file_path=str(latest_file),
                file_name=latest_file.name,
                timestamp=datetime.now()
            )
        else:
            return VisualizationResponse(
                success=False,
                file_path="",
                file_name="",
                timestamp=datetime.now()
            )
    
    except Exception as e:
        return VisualizationResponse(
            success=False,
            file_path="",
            file_name="",
            timestamp=datetime.now()
        )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload new data files"""
    try:
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the file if it's a data file
        if file.filename.endswith(('.csv', '.xlsx', '.xls')):
            try:
                csv_path, new_column_types = processor.clean_and_infer_types(str(file_path))
                
                # Update the data table in DuckDB
                duckdb_tools.create_table_from_path(path=csv_path, table="uploaded_data")
                
                return JSONResponse({
                    "success": True,
                    "filename": file.filename,
                    "processed": True,
                    "columns": list(new_column_types.keys()),
                    "rows": len(pd.read_csv(csv_path))
                })
            except Exception as proc_error:
                return JSONResponse({
                    "success": True,
                    "filename": file.filename,
                    "processed": False,
                    "error": f"Processing failed: {str(proc_error)}"
                })
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "processed": False,
            "message": "File uploaded but not processed (not a data file)"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/export/{format}")
async def export_data(format: str):
    """Export data/visualizations in specified format"""
    try:
        if format.lower() == "csv":
            # Export current data as CSV
            if csv_path and os.path.exists(csv_path):
                return FileResponse(
                    csv_path,
                    media_type='application/octet-stream',
                    filename=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
            else:
                raise HTTPException(status_code=404, detail="No data available for export")
        
        elif format.lower() == "json":
            # Export current data as JSON
            if csv_path and os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                json_data = df.to_json(orient='records', date_format='iso')
                
                return JSONResponse(
                    content=json.loads(json_data),
                    headers={
                        "Content-Disposition": f"attachment; filename=data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    }
                )
            else:
                raise HTTPException(status_code=404, detail="No data available for export")
        
        elif format.lower() == "html":
            # Create a summary HTML of all visualizations
            output_dir = Path("output")
            html_files = list(output_dir.glob("*.html"))
            
            if html_files:
                summary_html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Visualization Summary</title></head>
                <body>
                    <h1>Available Visualizations</h1>
                    <ul>
                        {''.join([f'<li><a href="/output/{f.name}" target="_blank">{f.name}</a></li>' for f in html_files])}
                    </ul>
                </body>
                </html>
                """
                return HTMLResponse(content=summary_html)
            else:
                raise HTTPException(status_code=404, detail="No visualizations available for export")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = "connected"
        try:
            # Try to execute a simple query to check DB connection
            # This is a basic check - you might want to add more sophisticated checks
            db_status = "connected"
        except:
            db_status = "disconnected"
        
        # Check agent status
        agents_status = {
            "data_analyst": "active",
            "viz_specialist": "active", 
            "analysis_team": "active"
        }
        
        # Overall system status
        overall_status = "healthy" if db_status == "connected" else "degraded"
        
        return HealthResponse(
            status=overall_status,
            agents_status=agents_status,
            database_status=db_status,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        return HealthResponse(
            status="error",
            agents_status={},
            database_status="error",
            timestamp=datetime.now()
        )

# Additional utility endpoints

@app.get("/api/data/summary")
async def get_data_summary():
    """Get summary information about loaded data"""
    try:
        if not csv_path or not os.path.exists(csv_path):
            return JSONResponse({
                "success": False,
                "message": "No data loaded"
            })
        
        df = pd.read_csv(csv_path)
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "column_types": column_types,
            "memory_usage": df.memory_usage(deep=True).sum(),
            "null_counts": df.isnull().sum().to_dict()
        }
        
        return JSONResponse({
            "success": True,
            "summary": summary
        })
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@app.get("/api/visualizations/list")
async def list_visualizations():
    """List available visualizations"""
    try:
        output_dir = Path("output")
        if not output_dir.exists():
            return JSONResponse({"visualizations": []})
        
        html_files = list(output_dir.glob("*.html"))
        visualizations = []
        
        for file in html_files:
            stat = file.stat()
            visualizations.append({
                "name": file.name,
                "path": f"/output/{file.name}",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return JSONResponse({
            "success": True,
            "visualizations": sorted(visualizations, key=lambda x: x["modified"], reverse=True)
        })
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    # Run the custom FastAPI app
    uvicorn.run("agent_interface:app", host="0.0.0.0", port=7778, reload=True)