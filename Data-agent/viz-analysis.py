import asyncio
from textwrap import dedent
import os
from dotenv import load_dotenv

load_dotenv()
import pandas as pd

from agno.tools.python import PythonTools
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools
from agno.models.azure import AzureOpenAI

file_path = "jobs_in_data.csv"

duckdb_tools = DuckDbTools(
    create_tables=False, export_tables=False, summarize_tables=False
)

python_tools = PythonTools()

def preprocess_file(file_path):
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
        csv_path = file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
        df.to_csv(csv_path, index=False)
        return csv_path
    return file_path

# Load the data
if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
    csv_path = preprocess_file(file_path)
    duckdb_tools.create_table_from_path(path=csv_path, table="data")
else:
    duckdb_tools.create_table_from_path(path=file_path, table="data")

agent = Agent(
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    tools=[duckdb_tools, python_tools],
    markdown=True,
    show_tool_calls=True,
    additional_context=dedent("""\
    You have access to the following tables:
    - data: contains information about jobs in data.
    - Python tools for creating visualizations using plotly only to create dashboards.
    
    IMPORTANT: When creating visualizations
        1. First query the data using DuckDB
        2. Then use Python tools to create charts
        3. Save charts as files that can be viewed.
    
    You are not allowed to create visualizations that are not related to the data. 
    You have to always query the data first before creating visualizations.
    If errors occur, you have to fix them and try again.
    """),
)

async def conversational_data_analysis():
    print("Data Analysis Agent Ready!")
    print("You can now ask questions about your data or request visualizations.")
    print("Examples:")
    print("- 'Show me the data structure'")
    print("- 'Create a plotly dashboard with filters'")
    print("- 'What are the most common job categories?'")
    print("- 'Make a chart showing salary distribution by company size'")
    print("\nType 'quit', 'exit', or 'bye' to end the conversation.\n")
    
    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye', 'q']:
                print("Goodbye! Thanks for using the data analysis agent.")
                break
            
            if not question:
                print("Please enter a question or command.")
                continue
            
            print("\nAgent:")
            await agent.aprint_response(question, stream=True)
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Thanks for using the data analysis agent.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again with a different question.\n")

# Run the conversational interface
asyncio.run(conversational_data_analysis())