from agno.agent import Agent
from agno.tools.gmail import GmailTools
from agno.models.azure import AzureOpenAI

import os
from dotenv import load_dotenv
load_dotenv()
llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5", "gpt-4.1-mini"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY_5"),
    api_version=os.getenv("2025-04-01-preview", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_5"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5"),
)

client_secret_path="/home/anshul/Projects/AI-Search-MCP/Agents/mail-agent/client_secret_398183445172-l83cj61nme1l06ml8oitlv2vvcb93lqd.apps.googleusercontent.com.json"
agent = Agent(model=llm, tools=[GmailTools(        
                                credentials_path=client_secret_path,
                                token_path="/home/anshul/Projects/AI-Search-MCP/Agents/mail-agent/token.json",
                                port=8080,
                                )], debug_mode=True)
agent.print_response("List the contents of emails from anshulraj@gmail.com in the last 72 hours with the contetnts of the emails as a table", markdown=True)