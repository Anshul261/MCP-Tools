import os
import base64
import json
import glob
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agno.tools.python import PythonTools
from agno.agent import Agent
from agno.os import AgentOS
from agno.team import Team
from agno.tools.duckdb import DuckDbTools
from agno.models.azure import AzureOpenAI
from agno.tools.reasoning import ReasoningTools
from agno.db.postgres import PostgresDb


load_dotenv()
console = Console()

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db = PostgresDb(db_url=db_url)

u_id="anshulraj@gmail.com"

# API Models
class ChatMessage(BaseModel):
    message: str
    chat_id: Optional[str] = "main"

class ChatResponse(BaseModel):
    response: str
    visualizations: list = []
    timestamp: str

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
        for col in track(df.columns, description="Inferring data types..."):
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

def display_data_info(column_types):
    """Display data information in a rich table"""
    table = Table(title="Dataset Information")
    table.add_column("Column", style="cyan")
    table.add_column("Data Type", style="magenta")
    
    for col, dtype in column_types.items():
        table.add_row(col, str(dtype))
    
    console.print(table)

# Initialize data processor
processor = DataProcessor()
file_path = "Alpha-NOC-Reports-Jan-to-Apr-2025.xlsx"

console.print(Panel.fit("Data Analysis System Initializing", style="bold blue"))

csv_path, column_types = processor.clean_and_infer_types(file_path)
display_data_info(column_types)

# Initialize tools
# duckdb_tools = DuckDbTools(create_tables=False, export_tables=False, summarize_tables=False)
duckdb_tools = DuckDbTools()
python_tools = PythonTools()
reasoning_tools = ReasoningTools()

# Load processed data
duckdb_tools.create_table_from_path(path=csv_path, table="data")

# Data Analysis Agent - specialized for querying and basic analysis
data_analyst = Agent(
    name="Data Analyst",
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    tools=[duckdb_tools],
    instructions=[
        "You are a data analyst with access to a 'data' table containing ticket/support request data.",
        "The data table has 4469 rows and columns including: Request ID, Category, Subcategory, SLA Name, Created Time, etc.",
        "Always use SQL queries to analyze the actual data in the 'data' table.",
        "Provide detailed analysis with specific numbers and insights from the data.",
        "When analyzing trends, use date functions on the 'Created Time' column.",
        "Focus on real patterns in the actual data, not hypothetical scenarios.",
    ],
)

# Visualization Agent - specialized for creating charts
viz_specialist = Agent(
    name="Visualization Specialist",
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    tools=[python_tools, duckdb_tools],
    instructions=[
        "You are a visualization specialist. You MUST create actual files when users request visualizations.",
        "WORKFLOW: 1) Query data with DuckDB, 2) Create visualization with Python, 3) Save to output/ folder",
        "MANDATORY: Use Python tools to execute code that saves files - never just talk about creating them.",
        "For pie charts: Use matplotlib with plt.pie(), save as PNG to output/ folder",
        "For line/bar charts: Use matplotlib, save as PNG to output/ folder", 
        "For dashboards: Create HTML with embedded Chart.js, save to output/ folder",
        "EXACT WORKING EXAMPLE for pie chart:",
        "1. DuckDB: SELECT Category, COUNT(*) as count FROM data GROUP BY Category", 
        "2. Python code to execute:",
        "   import matplotlib.pyplot as plt",
        "   plt.figure(figsize=(10, 8))",  
        "   plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)",
        "   plt.title('Category Distribution')",
        "   plt.axis('equal')",
        "   plt.savefig('output/category_pie_chart.png', dpi=300, bbox_inches='tight')",
        "   plt.close()",
        "3. Confirm file was saved to output/ folder",
        "CRITICAL: You must actually execute the Python code to create and save files.",
        "Never respond without creating the requested visualization file first.",
        "Always use descriptive filenames like 'category_pie_chart.png' or 'monthly_trends.png'",
    ],
)

analysis_team = Team(
    name="Data Analysis Team",
    db=db,
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    members=[data_analyst, viz_specialist],
    tools=[reasoning_tools],
    instructions=[
        f"You have access to a 'data' table with {len(column_types)} columns and 4469 rows of ticket/support data.",
        f"Column types: {column_types}",
        "CRITICAL WORKFLOW: When ANY user asks for charts/visualizations:",
        "1. Data Analyst: Query the data with SQL",
        "2. Visualization Specialist: IMMEDIATELY execute Python code to create and save the file",
        "3. Never just describe - always create actual files",
        "VISUALIZATION REQUESTS = MANDATORY FILE CREATION",
        "Examples of requests that REQUIRE file creation:",
        "- 'Create a chart' → MUST save a file",
        "- 'Show me a pie chart' → MUST save a file", 
        "- 'Make a visualization' → MUST save a file",
        "The Visualization Specialist must use Python tools to execute actual code.",
        "ALWAYS query the actual data table using SQL before providing any analysis.",
        "Provide concrete insights based on actual data, not hypothetical scenarios.",
        "Focus on time-based trends using the Created Time column for monthly/daily analysis.",
        "The UI will automatically display created visualizations to users.",
    ],
    enable_user_memories=True,
    enable_session_summaries=True,
    markdown=True,
    stream_member_events=True,
    enable_agentic_memory=True,
)



agent_os = AgentOS(
    os_id="my-first-os",
    description="My first AgentOS",
    agents=[viz_specialist, data_analyst,],
    teams=[analysis_team]
)

app = agent_os.get_app()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving visualizations
app.mount("/static", StaticFiles(directory="output"), name="static")

def find_latest_visualizations():
    """Find the latest visualization files in the output directory"""
    viz_files = []
    output_dir = Path("output")
    
    if not output_dir.exists():
        return viz_files
    
    # Look for HTML and PNG files
    for pattern in ["*.html", "*.png"]:
        files = list(output_dir.glob(pattern))
        for file_path in files:
            try:
                stat = file_path.stat()
                viz_files.append({
                    "filename": file_path.name,
                    "url": f"/static/{file_path.name}",
                    "type": "html" if file_path.suffix == ".html" else "image",
                    "created": stat.st_mtime,
                    "size": stat.st_size
                })
            except (OSError, IOError):
                continue  # Skip files that can't be accessed
    
    # Sort by creation time, newest first
    viz_files.sort(key=lambda x: x['created'], reverse=True)
    return viz_files

def find_new_visualizations(before_count):
    """Find visualizations created after a certain point"""
    current_viz = find_latest_visualizations()
    if len(current_viz) > before_count:
        return current_viz[:len(current_viz) - before_count]
    return []

def find_visualizations_since(start_time):
    """Find visualizations created or modified since a specific timestamp"""
    viz_files = []
    output_dir = Path("output")
    
    if not output_dir.exists():
        return viz_files
    
    # Look for HTML and PNG files
    for pattern in ["*.html", "*.png"]:
        files = list(output_dir.glob(pattern))
        for file_path in files:
            try:
                stat = file_path.stat()
                # Check if file was modified after start_time (with 1 second buffer)
                if stat.st_mtime >= (start_time - 1):
                    viz_files.append({
                        "filename": file_path.name,
                        "url": f"/static/{file_path.name}",
                        "type": "html" if file_path.suffix == ".html" else "image",
                        "created": stat.st_mtime,
                        "size": stat.st_size
                    })
            except (OSError, IOError):
                continue  # Skip files that can't be accessed
    
    # Sort by creation time, newest first
    viz_files.sort(key=lambda x: x['created'], reverse=True)
    return viz_files

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(message: ChatMessage):
    """Chat with the data analysis team and get visualizations"""
    try:
        import time
        from datetime import datetime
        
        # Record start time for detecting new files
        start_time = time.time()
        console.print(f"[blue]Processing message: {message.message}[/blue]")
        
        # Send message to the analysis team
        response = analysis_team.run(message.message, stream=False)
        
        # Wait a moment for file system to sync
        time.sleep(0.5)
        
        # Find files created/modified after start time
        new_visualizations = find_visualizations_since(start_time)
        
        # Fallback: if no new files detected but response mentions creating visualizations,
        # include the most recent files (in case timing was off)
        if len(new_visualizations) == 0 and any(keyword in response.content.lower() for keyword in ['created', 'chart', 'visualization', 'graph', 'dashboard', 'saved']):
            console.print("[yellow]No new files detected but response mentions visualizations, checking recent files...[/yellow]")
            all_viz = find_latest_visualizations()
            # Include files from the last 5 minutes as a fallback
            recent_time = start_time - 300  # 5 minutes ago
            new_visualizations = [v for v in all_viz[:3] if v['created'] >= recent_time]  # Max 3 most recent
            console.print(f"[yellow]Fallback: Including {len(new_visualizations)} recent files[/yellow]")
        
        console.print(f"[green]Found {len(new_visualizations)} visualizations to display[/green]")
        for viz in new_visualizations:
            console.print(f"  - {viz['filename']} ({viz['type']})")
        
        return ChatResponse(
            response=response.content,
            visualizations=new_visualizations,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        console.print(f"[red]API Error: {str(e)}[/red]")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visualizations")
async def get_visualizations():
    """Get all available visualizations"""
    try:
        visualizations = find_latest_visualizations()
        return JSONResponse(content={"visualizations": visualizations})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/force-visualization")  
async def force_create_visualization(request_data: dict):
    """Force create a visualization when agents fail"""
    try:
        viz_type = request_data.get("type", "pie")
        query = request_data.get("query", "SELECT Category, COUNT(*) as count FROM data GROUP BY Category")
        
        # Execute query directly
        result = duckdb_tools.execute_sql(query)
        console.print(f"[blue]Query result: {result}[/blue]")
        
        # Create visualization using Python tools directly
        if viz_type == "pie":
            python_code = f"""
import matplotlib.pyplot as plt
import time

# Data from query
data = {result}
if isinstance(data, str):
    # Handle string result, try to parse
    print("Result is string:", data)
else:
    print("Processing data:", data)

# Create a simple pie chart with dummy data for now
categories = ['Network', 'Security', 'Software', 'Hardware', 'Other']
counts = [25, 30, 20, 15, 10]

plt.figure(figsize=(10, 8))
plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
plt.title('Category Distribution - Forced Creation')
plt.axis('equal')

# Save with timestamp to avoid conflicts
filename = f'output/forced_pie_chart_{{int(time.time())}}.png'
plt.savefig(filename, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved chart to: {{filename}}")
"""
            
            result = python_tools.execute_python_code(python_code)
            console.print(f"[green]Python execution result: {result}[/green]")
            
        return {"status": "success", "message": "Forced visualization created"}
        
    except Exception as e:
        console.print(f"[red]Force visualization error: {str(e)}[/red]")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents": len(agent_os.agents), "teams": len(agent_os.teams)}

if __name__ == "__main__":
    # Default port is 7777; change with port=...
    agent_os.serve(app="agent:app", reload=True)