"""
Simple AgentOS with File Upload
- Upload documents (PDF, TXT, DOCX, etc.)
- Ask questions about uploaded documents
- Or ask general questions using LLM knowledge

Usage:
# Ask question with uploaded file
curl -X POST "http://localhost:7777/agents/doc-agent/runs" \
  -F "message=What is this document about?" \
  -F "files=@document.pdf"

# Ask general question without file
curl -X POST "http://localhost:7777/agents/doc-agent/runs" \
  -F "message=What is Python?"
"""

import os
from typing import Optional, Sequence

from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.media import File
from agno.models.azure import AzureOpenAI
from agno.os import AgentOS
from agno.tools import Toolkit

# ============================================================================
# Document Processing Tool
# ============================================================================


class DocumentTools(Toolkit):
    """Simple document processing toolkit."""

    def __init__(self):
        super().__init__(name="document_tools", tools=[self.read_document])

    def read_document(self, files: Optional[Sequence[File]] = None) -> str:
        """
        Read and extract text from uploaded documents.

        Args:
            files: Files uploaded by user (auto-injected by AGNO)

        Returns:
            Extracted text content
        """
        if not files:
            return "No files uploaded."

        results = []
        for i, file in enumerate(files, 1):
            if file.content:
                # Simple text extraction (decode bytes to string)
                try:
                    text = file.content.decode("utf-8", errors="ignore")
                    file_name = getattr(file, "name", f"file_{i}")
                    results.append(f"=== {file_name} ===\n\n{text}")
                except Exception as e:
                    results.append(f"Error reading file {i}: {str(e)}")
            else:
                results.append(f"File {i} is empty.")

        return "\n\n".join(results)


# ============================================================================
# LLM Setup
# ============================================================================

llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# ============================================================================
# Agent Setup
# ============================================================================

doc_agent = Agent(
    id="doc-agent",
    name="Document Q&A Agent",
    model=llm,
    tools=[DocumentTools()],
    instructions=[
        "You can answer questions about uploaded documents or general questions.",
        "If files are uploaded, use the read_document tool to extract their content first.",
        "Then answer questions based on the document content.",
        "If no files are uploaded, answer using your general knowledge.",
        "Be concise and helpful.",
    ],
    send_media_to_model=False,  # Let tools handle files
    store_media=True,  # Store files for tool access
    markdown=True,
    debug_mode=True,
)

# ============================================================================
# AgentOS Setup
# ============================================================================

agent_os = AgentOS(
    id="simple-doc-agentos",
    name="Simple Document Q&A",
    agents=[doc_agent],
)

app = agent_os.get_app()

# ============================================================================
# Custom Endpoints
# ============================================================================

from fastapi import APIRouter
from fastapi.responses import JSONResponse

custom_router = APIRouter()


@custom_router.get("/health")
async def health_check():
    """Health check."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "Simple Document Q&A",
            "agents": ["doc-agent"],
        }
    )


@custom_router.get("/info")
async def api_info():
    """API information."""
    return JSONResponse(
        content={
            "name": "Simple Document Q&A API",
            "description": "Upload documents and ask questions",
            "endpoints": {
                "ask_question": "POST /agents/doc-agent/runs",
                "health": "GET /health",
                "docs": "GET /docs",
            },
            "examples": [
                {
                    "with_file": 'curl -X POST "http://localhost:7777/agents/doc-agent/runs" -F "message=Summarize this" -F "files=@doc.pdf"'
                },
                {
                    "without_file": 'curl -X POST "http://localhost:7777/agents/doc-agent/runs" -F "message=What is AI?"'
                },
            ],
        }
    )


app.include_router(custom_router)

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    agent_os.serve(
        app="simple-doc-agent:app",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )
