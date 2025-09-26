import asyncio
from textwrap import dedent
import os
from dotenv import load_dotenv

load_dotenv()
import pandas as pd


from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools
from agno.models.azure import AzureOpenAI

file_path = "/home/anshul/Projects/AI-Search-MCP/Data-agent/jobs_in_data.csv"

duckdb_tools = DuckDbTools(
    create_tables=False, export_tables=False, summarize_tables=False
)

def preprocess_file(file_path):
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        # Convert Excel to CSV temporarily
        df = pd.read_excel(file_path)
        csv_path = file_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
        df.to_csv(csv_path, index=False)
        return csv_path
    return file_path

if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
    csv_path = preprocess_file(file_path)
    duckdb_tools.create_table_from_path(
        path=csv_path,
        table="data",
    )
else:   
    duckdb_tools.create_table_from_path(
        path=file_path,
        table="data",
    )


# duckdb_tools.create_table_from_path(
#     path="https://agno-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
#     table="movies",
# )

agent = Agent(
    model=AzureOpenAI(
            id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        ),
    tools=[duckdb_tools],
    markdown=True,
    show_tool_calls=True,
    additional_context=dedent("""\
    You have access to the following tables:
    - data: contains information about jobs in data.
    """),
)
asyncio.run(
    agent.aprint_response("What is the average salary of jobs in data?", stream=False)
)