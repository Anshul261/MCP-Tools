from agno.agent import Agent
from agno.media import Image
import os
from dotenv import load_dotenv
from agno.models.azure import AzureOpenAI
from pathlib import Path

load_dotenv()

# Verify image exists first
image_path = "/home/anshul/Projects/AI-Search-MCP/Agents/invoice-processing/batch2-0501.jpg"
if not Path(image_path).exists():
    print(f"Error: Image not found at {image_path}")
    exit(1)

# Fixed Azure OpenAI configuration
agent = Agent(
    model=AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-06-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    ),
    markdown=True,
)

# FIXED: Use 'filepath' instead of 'path'
try:
    agent.print_response(
        "Transcribe this document.",
        images=[Image(filepath=image_path)]  # Changed from 'path' to 'filepath'
    )
except Exception as e:
    print(f"Error: {e}")
    print("Check your Azure OpenAI deployment supports vision models")
