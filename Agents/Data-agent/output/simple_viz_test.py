#!/usr/bin/env python3
"""
Simple test with a dedicated visualization agent
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv

from agno.tools.python import PythonTools  
from agno.tools.duckdb import DuckDbTools
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.db.postgres import PostgresDb

load_dotenv()

# Setup
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db = PostgresDb(db_url=db_url)

# Load data (same as main agent)
csv_path = "Alpha-NOC-Reports-Jan-to-Apr-2025.csv"
duckdb_tools = DuckDbTools()
python_tools = PythonTools()

# Create the data table
if Path(csv_path).exists():
    duckdb_tools.create_table_from_path(path=csv_path, table="data")
    print("✅ Data loaded")
else:
    print("❌ CSV file not found")

# Create a simple, direct agent
simple_viz_agent = Agent(
    name="Simple Viz Agent",
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    tools=[python_tools, duckdb_tools],
    db=db,
    instructions=[
        "You are a simple visualization creator.",
        "When asked to create a chart, follow these EXACT steps:",
        "1. Use DuckDB to query the data",
        "2. Use Python tools to create and save a PNG file", 
        "3. ALWAYS execute actual Python code - never just describe it",
        "4. Save files to output/ folder",
        "NEVER just talk about creating files - ALWAYS execute the code.",
    ],
)

def test_simple_agent():
    """Test the simple agent"""
    print("\n🧪 Testing Simple Visualization Agent")
    print("=" * 50)
    
    # Check files before
    output_dir = Path("output")
    files_before = set()
    if output_dir.exists():
        files_before = {f.name for f in output_dir.glob("*") if f.is_file()}
    
    print(f"Files before: {len(files_before)}")
    
    # Direct request
    response = simple_viz_agent.run(
        "Query the 'data' table to get Category counts, then create a pie chart and save it as 'test_simple_pie.png' in the output folder. Execute the actual Python code.",
        stream=False
    )
    
    print(f"Response: {response.content}")
    
    # Check files after
    time.sleep(1)
    files_after = set()
    if output_dir.exists():
        files_after = {f.name for f in output_dir.glob("*") if f.is_file()}
    
    new_files = files_after - files_before
    print(f"New files: {new_files}")
    
    return len(new_files) > 0

if __name__ == "__main__":
    success = test_simple_agent()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")