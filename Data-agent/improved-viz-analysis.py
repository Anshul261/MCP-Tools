import os
import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

from agno.tools.python import PythonTools
from agno.agent import Agent
from agno.team import Team
from agno.tools.duckdb import DuckDbTools
from agno.models.azure import AzureOpenAI
from agno.tools.reasoning import ReasoningTools

load_dotenv()
console = Console()

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
duckdb_tools = DuckDbTools(create_tables=False, export_tables=False, summarize_tables=False)
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

# Collaborative Team
analysis_team = Team(
    name="Data Analysis Team",
    mode="coordinate",
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
        "ALWAYS query the actual data table using SQL before providing any analysis.",
        "Data Analyst: Run SQL queries on the 'data' table to find real patterns and trends.",
        "Visualization Specialist: Use query results to create meaningful charts and save them to output folder.",
        "Provide concrete insights based on actual data, not hypothetical scenarios.",
        "Focus on time-based trends using the Created Time column for monthly/daily analysis.",
    ],
    enable_user_memories=True,
    enable_session_summaries=True,
    markdown=True,
    show_tool_calls=True,
)

def main():
    console.print(Panel.fit("Data Analysis Team Ready", style="bold green"))
    console.print("[yellow]Data loaded and preprocessed successfully[/yellow]")
    console.print(f"[cyan]Detected {len(column_types)} columns with proper types[/cyan]")
    
    console.print("\n[bold]Available commands:[/bold]")
    console.print("- 'describe data' - Get data overview")
    console.print("- 'create dashboard' - Generate multiple visualizations")
    console.print("- Ask specific questions about your data")
    console.print("- 'quit' to exit\n")
    
    # Start interactive session
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                console.print("[green]Analysis session ended![/green]")
                break
                
            if not question:
                continue
                
            console.print("[blue]Team analyzing...[/blue]")
            analysis_team.print_response(question)
            
        except KeyboardInterrupt:
            console.print("\n[green]Analysis session ended![/green]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("Please try a different question.")

if __name__ == "__main__":
    main()