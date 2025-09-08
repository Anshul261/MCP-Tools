import os
import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

from agno.tools.python import PythonTools
from agno.agent import Agent
from agno.tools.duckdb import DuckDbTools
from agno.models.azure import AzureOpenAI

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

console.print(Panel.fit("HTML Dashboard Analysis System", style="bold blue"))

csv_path, column_types = processor.clean_and_infer_types(file_path)
display_data_info(column_types)

# Initialize tools
duckdb_tools = DuckDbTools(create_tables=False, export_tables=False, summarize_tables=False)
python_tools = PythonTools()

# Load processed data
duckdb_tools.create_table_from_path(path=csv_path, table="data")

# Single powerful agent focused on HTML dashboard generation
dashboard_agent = Agent(
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    tools=[duckdb_tools, python_tools],
    enable_user_memories=True,
    enable_session_summaries=True,
    markdown=True,
    show_tool_calls=True,
    instructions=[
        "You are a data analysis and dashboard creation specialist.",
        f"You have access to a 'data' table with {len(column_types)} columns and ticket/support data.",
        f"Key columns: {', '.join(list(column_types.keys())[:10])}...",
        "IMPORTANT: Create HTML dashboards instead of Python plots.",
        "CRITICAL SOLUTION: Use the dashboard_templates.py file to avoid f-string conflicts:",
        "1. Import and use get_html_template() for the base HTML structure",
        "2. Use get_stat_card_template() for KPI cards", 
        "3. Use get_chart_card_template() for chart containers",
        "4. Use get_chart_js_template() for Chart.js initialization",
        "5. Use simple string replacement with .replace() method instead of f-strings",
        "6. Build dashboard content in sections, then combine using template placeholders",
        "Steps for dashboard creation:",
        "1. Query the 'data' table using DuckDB to get actual insights",
        "2. Create stat cards content using templates",
        "3. Create chart cards content using templates", 
        "4. Generate Chart.js code using safe templates",
        "5. Combine all sections using string replacement",
        "6. Save the final HTML file",
        "Always include actual data insights as text elements.",
        "Use professional color schemes and responsive design.",
        "For complex dashboards, build each section separately to avoid syntax errors.",
    ],
)

def main():
    console.print(Panel.fit("HTML Dashboard Agent Ready", style="bold green"))
    console.print("[yellow]Data loaded and preprocessed successfully[/yellow]")
    console.print(f"[cyan]Ready to create HTML/CSS/JavaScript dashboards[/cyan]")
    
    console.print("\n[bold]Dashboard Types Available:[/bold]")
    console.print("- 'create dashboard' - Generate comprehensive HTML dashboard")
    console.print("- 'monthly trends' - Monthly ticket volume analysis")
    console.print("- 'category analysis' - Category and subcategory breakdown")
    console.print("- 'sla performance' - SLA compliance dashboard")
    console.print("- Ask any specific analysis questions")
    console.print("- 'quit' to exit\n")
    
    # Start interactive session
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                console.print("[green]Dashboard session ended![/green]")
                break
                
            if not question:
                continue
                
            console.print("[blue]Creating HTML dashboard...[/blue]")
            dashboard_agent.print_response(question)
            
        except KeyboardInterrupt:
            console.print("\n[green]Dashboard session ended![/green]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("Please try a different question.")

if __name__ == "__main__":
    main()