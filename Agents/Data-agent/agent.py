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

# Build database URL from environment variables
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5533")
db_user = os.getenv("DB_USER", "ai")
db_password = os.getenv("DB_PASSWORD", "ai")
db_name = os.getenv("DB_NAME", "ai")

db_url = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
console.print(f"[blue]Connecting to database: {db_user}@{db_host}:{db_port}/{db_name}[/blue]")
db = PostgresDb(db_url=db_url)
llm=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )
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
file_path = "realistic_ticket_data.xlsx"

# Initialize data only once using file-based flag to survive reloads
data_flag_file = ".data_initialized"
csv_path = file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')

if not os.path.exists(data_flag_file) or not os.path.exists(csv_path):
    console.print(Panel.fit("Data Analysis System Initializing", style="bold blue"))
    csv_path, column_types = processor.clean_and_infer_types(file_path)
    display_data_info(column_types)
    # Create flag file to prevent reprocessing
    with open(data_flag_file, 'w') as f:
        f.write("initialized")
else:
    # Reuse already processed data - load column types from CSV with proper inference
    if os.path.exists(csv_path):
        # Read a small sample to get proper column types
        df_sample = pd.read_csv(csv_path, nrows=1000)
        # Apply the same type inference as the original processing
        for col in df_sample.columns:
            if any(word in col.lower() for word in ['date', 'time', 'created', 'updated', 'resolved']):
                try:
                    df_sample[col] = pd.to_datetime(df_sample[col])
                except (ValueError, TypeError):
                    pass
            elif df_sample[col].dtype == 'object':
                try:
                    df_sample[col] = pd.to_numeric(df_sample[col])
                except (ValueError, TypeError):
                    pass
        column_types = df_sample.dtypes.to_dict()
        console.print(f"[green]Reusing processed data: {csv_path}[/green]")
    else:
        # Fallback if CSV doesn't exist
        csv_path, column_types = processor.clean_and_infer_types(file_path)

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
    model=llm,
    tools=[duckdb_tools],
    instructions=[
        "You are a data analyst with access to a 'data' table containing ticket/support request data.",
        "You have access to ONLY the 'data' table - do not query any other tables as they don't exist.",
        "IMPORTANT: Always start by running 'DESCRIBE data' to understand the current schema before running analysis queries.",
        "Use exact column names from the schema - column names may contain spaces and need to be quoted with double quotes.",
        "For date operations, use STRFTIME('%Y-%m', \"Created Time\") for monthly grouping - do NOT use DATE_TRUNC.",
        "Always use SQL queries to analyze the actual data in the 'data' table.",
        "Provide detailed analysis with specific numbers and insights from the data.",
        "Focus on real patterns in the actual data, not hypothetical scenarios.",
        "",
        "For insight requests, provide a comprehensive text summary with key findings:",
        "- FIRST: Run DESCRIBE data to get current schema",
        "- Execute 3-5 relevant SQL queries to gather key metrics from the 'data' table ONLY",
        "- Use proper DuckDB syntax: STRFTIME for dates, proper column quoting",
        "- Summarize findings in clear, actionable insights",
        "- Include specific numbers and percentages",
        "- Stop after providing insights - do not create visualizations unless specifically requested",
        "",
        "CRITICAL: Only query the 'data' table. If a query fails, check the schema and use correct DuckDB syntax.",
    ],
)

# Visualization Agent - specialized for creating charts
viz_specialist = Agent(
    name="Visualization Specialist",
    model=llm,
    tools=[python_tools, duckdb_tools],
    instructions=[
        "You are a visualization specialist. You MUST create actual files when users request visualizations.",

        "MODE DETECTION - Choose visualization approach based on user request:",
        "DASHBOARD MODE: If user asks for 'dashboard', 'comprehensive analysis', 'overview', 'complete view', 'full analysis', 'multiple charts', or asks complex multi-faceted questions",
        "SINGLE CHART MODE: If user asks for specific 'chart', 'graph', 'plot', 'show me [specific metric]', or requests one specific visualization",

        "DASHBOARD MODE WORKFLOW:",
        "1) Query data with DuckDB for multiple related metrics",
        "2) Create comprehensive HTML dashboard with 3-4 related charts using Chart.js",
        "3) Include KPI summary cards, insights section, and professional styling",
        "4) Use dashboard_templates.py functions for consistent layout",
        "5) Save as HTML to output/ folder with descriptive name like 'comprehensive_dashboard.html'",

        "SINGLE CHART MODE WORKFLOW:",
        "1) Query data with DuckDB for specific metric",
        "2) Create focused visualization with matplotlib",
        "3) Save as PNG to output/ folder with descriptive name",

        "DASHBOARD CREATION TEMPLATE:",
        "```python",
        "from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template",
        "# Query data first to get actual values",
        "# Create HTML template - get_html_template() takes NO parameters",
        "html_template = get_html_template()",
        "# Create stat cards using template replacement",
        "stat_card_template = get_stat_card_template()",
        "stats_html = stat_card_template.replace('{{NUMBER}}', '1000').replace('{{LABEL}}', 'Total Tickets')",
        "# Create chart JS using get_chart_js_template(chart_id, chart_type, data_labels, data_values, title)",
        "chart_js = get_chart_js_template('chart1', 'pie', ['A', 'B'], [10, 20], 'My Chart')",
        "# Create chart containers using get_chart_card_template()",
        "chart_card_template = get_chart_card_template()",
        "charts_html = chart_card_template.replace('{{CHART_TITLE}}', 'My Chart').replace('{{CHART_ID}}', 'chart1')",
        "# Replace placeholders: {{STATS_CONTENT}}, {{CHARTS_CONTENT}}, {{INSIGHTS_CONTENT}}, {{JAVASCRIPT_CONTENT}}",
        "final_html = html_template.replace('{{STATS_CONTENT}}', stats_html).replace('{{CHARTS_CONTENT}}', charts_html)",
        "# Save to output/ folder - avoid filename conflicts with template",
        "```",

        "SINGLE CHART EXAMPLE:",
        "1. DuckDB: SELECT Category, COUNT(*) as count FROM data GROUP BY Category",
        "2. Python: matplotlib visualization, save PNG to output/",

        "CRITICAL REQUIREMENTS:",
        "- ALWAYS query actual data first with DuckDB from the 'data' table only",
        "- MUST execute Python code to create and save files",
        "- Dashboard mode: Create 3-4 related visualizations in one HTML file",
        "- Single mode: Create focused analysis with one PNG chart",
        "- Include data-driven insights and specific numbers in all outputs",
        "- Never respond without creating the requested file(s)",
        "",
        "IMPORTANT FUNCTION SIGNATURES:",
        "- get_html_template() - takes NO parameters, returns template string",
        "- get_chart_js_template(chart_id, chart_type, data_labels, data_values, title) - requires all 5 parameters",
        "- get_stat_card_template() - takes NO parameters, returns template string",
        "- get_chart_card_template() - takes NO parameters, returns chart container template",
        "- Use template.replace('{{PLACEHOLDER}}', 'value') to fill templates",
        "",
        "CRITICAL: Always use specific filenames like 'ticket_dashboard.html' or 'category_analysis.html'",
        "NEVER use generic names like 'comprehensive_dashboard.html' that might conflict with templates",
    ],
)

analysis_team = Team(
    name="Data Analysis Team",
    db=db,
    model=llm,
    members=[data_analyst, viz_specialist],
    tools=[reasoning_tools],
    instructions=[
        "You have access to a 'data' table containing ticket/support request data.",
        "IMPORTANT: Agents should run 'DESCRIBE data' first to get current schema and row count before analysis.",

        "REQUEST TYPE DETECTION:",
        "INSIGHTS/ANALYSIS REQUESTS: 'insights', 'analysis', 'what can you tell me', 'patterns', 'trends', 'summary' → Data Analyst provides text-based insights",
        "DASHBOARD REQUESTS: 'dashboard', 'comprehensive dashboard', 'overview dashboard', 'create dashboard' → Create HTML dashboard",
        "SINGLE CHART REQUESTS: 'chart', 'graph', 'plot', 'show me [specific metric] chart' → Create single visualization",

        "WORKFLOW FOR INSIGHTS/ANALYSIS MODE:",
        "1. Data Analyst: Query relevant datasets and provide comprehensive text-based insights",
        "2. Include specific numbers, percentages, and key findings",
        "3. NO visualization creation required - just provide insights in text format",

        "WORKFLOW FOR DASHBOARD MODE:",
        "1. Data Analyst: Query multiple related datasets (category breakdown, trends, status, etc.)",
        "2. Visualization Specialist: Create comprehensive HTML dashboard with 3-4 charts using dashboard_templates.py",
        "3. Include KPI cards, insights, and professional multi-chart layout",
        "4. Save as HTML file with descriptive name like 'comprehensive_dashboard.html'",

        "WORKFLOW FOR SINGLE CHART MODE:",
        "1. Data Analyst: Query specific dataset for the requested metric",
        "2. Visualization Specialist: Create focused matplotlib visualization",
        "3. Include analysis insights with specific data points",
        "4. Save as PNG file with descriptive name",

        "IMPORTANT RULES:",
        "- For insight/analysis questions: ONLY Data Analyst responds with text insights, NO files created",
        "- For dashboard requests: Create HTML dashboards with multiple charts",
        "- For chart requests: Create single PNG visualizations",
        "- Always query actual data first before providing insights or creating visualizations",
        "- Provide concrete insights with specific numbers and percentages",

        "EXAMPLES:",
        "Insights: 'What insights can you provide?' → Data Analyst text response only",
        "Dashboard: 'Create a dashboard' → HTML with 3-4 charts",
        "Single: 'Show me a pie chart of categories' → PNG pie chart",

        "Focus on time-based trends using the Created Time column for monthly/daily analysis.",
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","http://localhost:3001", "http://127.0.0.1:3001"],
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