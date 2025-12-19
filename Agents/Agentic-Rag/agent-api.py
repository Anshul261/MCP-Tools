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
from io import BytesIO
from typing import Optional, Sequence

import PyPDF2
from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
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
        Supports PDF, TXT, and other text-based files.

        Args:
            files: Files uploaded by user (auto-injected by AGNO)

        Returns:
            Extracted text content that will persist in conversation history
        """
        if not files:
            return "No files uploaded."

        results = []
        for i, file in enumerate(files, 1):
            # Debug: show all available attributes
            print(f"[DEBUG] File {i} attributes: {dir(file)}")

            if not file.content:
                results.append(f"File {i} is empty.")
                continue

            # Get file attributes safely with defaults
            file_name = (
                getattr(file, "name", None)
                or getattr(file, "filename", None)
                or f"file_{i}"
            )
            file_type = (
                getattr(file, "type", None)
                or getattr(file, "content_type", None)
                or "unknown"
            )

            print(
                f"[DEBUG] File {i}: name={file_name}, type={file_type}, size={len(file.content)}"
            )

            try:
                # Check if it's a PDF file
                is_pdf = (
                    isinstance(file_name, str) and file_name.lower().endswith(".pdf")
                ) or (isinstance(file_type, str) and "pdf" in file_type.lower())

                if is_pdf:
                    print(f"[PDF] Processing {file_name} ({len(file.content)} bytes)")

                    # Extract text from PDF using PyPDF2
                    pdf_reader = PyPDF2.PdfReader(BytesIO(file.content))
                    num_pages = len(pdf_reader.pages)
                    print(f"[PDF] Found {num_pages} pages in {file_name}")

                    text_parts = []
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        try:
                            page_text = page.extract_text()
                            if page_text and page_text.strip():
                                text_parts.append(f"[Page {page_num}]\n{page_text}")
                                print(
                                    f"[PDF] Extracted {len(page_text)} characters from page {page_num}"
                                )
                            else:
                                print(
                                    f"[PDF] Warning: Page {page_num} has no extractable text"
                                )
                        except Exception as page_error:
                            print(f"[PDF] Error on page {page_num}: {page_error}")
                            text_parts.append(
                                f"[Page {page_num}]\n(Error extracting this page: {page_error})"
                            )

                    if text_parts:
                        extracted_text = "\n\n".join(text_parts)
                        print(
                            f"[PDF] Successfully extracted text from {len(text_parts)} pages"
                        )
                        results.append(
                            f"=== Document: {file_name} ===\n"
                            f"Type: PDF\n"
                            f"Pages: {num_pages}\n"
                            f"Extracted: {len(text_parts)} pages with text\n\n"
                            f"{extracted_text}\n"
                            f"=== End of {file_name} ==="
                        )
                    else:
                        print(f"[PDF] Warning: No readable text found in {file_name}")
                        results.append(
                            f"=== Document: {file_name} ===\n"
                            f"Type: PDF\n"
                            f"Pages: {num_pages}\n"
                            f"Warning: This PDF has {num_pages} pages but no extractable text. "
                            f"It may contain only images or scanned content.\n"
                            f"=== End of {file_name} ==="
                        )
                else:
                    # Try to decode as plain text
                    print(f"[TEXT] Processing {file_name} as text file")
                    text = file.content.decode("utf-8", errors="ignore")
                    print(f"[TEXT] Extracted {len(text)} characters")
                    results.append(
                        f"=== Document: {file_name} ===\n"
                        f"Type: Text\n"
                        f"Size: {len(file.content)} bytes\n\n"
                        f"{text}\n"
                        f"=== End of {file_name} ==="
                    )
            except Exception as e:
                import traceback

                error_details = traceback.format_exc()
                print(f"[ERROR] Failed to process {file_name}:")
                print(error_details)
                results.append(
                    f"=== Document: {file_name} ===\n"
                    f"Error: Failed to extract text\n"
                    f"Details: {str(e)}\n"
                    f"Type: {file_type}\n"
                    f"Size: {len(file.content)} bytes\n"
                    f"=== End of {file_name} ==="
                )

        # Return a comprehensive result that will be stored in session history
        full_result = "\n\n".join(results)
        return (
            "I have successfully extracted and stored the document content in this conversation.\n"
            f"You can now ask me questions about the following document(s):\n\n"
            f"{full_result}\n\n"
            f"The document content is now available in our conversation context. "
            f"Ask me anything about it!"
        )


# ============================================================================
# Database Setup
# ============================================================================

# SQLite database for session storage
db = SqliteDb(
    db_file="agent_sessions.db",  # Database file in current directory
    id="doc-agent-db",
)

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
        "IMPORTANT: When files are uploaded, use the read_document tool IMMEDIATELY to extract their content.",
        "The extracted document content will be stored in the conversation history automatically.",
        "After extraction, the document stays in context for all future questions in this session.",
        "Users do NOT need to re-upload the document for follow-up questions.",
        "If asked about a document that was already processed, refer to the document content from the conversation history.",
        "If no files are uploaded, answer using your general knowledge.",
        "Be concise, helpful, and reference specific parts of the document when answering.",
    ],
    db=db,  # Enable session storage
    enable_user_memories=True,  # Store user preferences and context
    add_history_to_context=True,  # Add conversation history to context
    num_history_runs=10,  # Keep last 10 messages in context
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
            "database": "SQLite (agent_sessions.db)",
            "session_storage": "enabled",
        }
    )


@custom_router.get("/info")
async def api_info():
    """API information."""
    return JSONResponse(
        content={
            "name": "Simple Document Q&A API",
            "description": "Upload documents and ask questions with session storage",
            "database": {
                "type": "SQLite",
                "file": "agent_sessions.db",
                "features": [
                    "Session persistence",
                    "Conversation history",
                    "User memories",
                    "Context retention (10 messages)",
                ],
            },
            "endpoints": {
                "agent_runs": "POST /agents/doc-agent/runs",
                "sessions_list": "GET /sessions",
                "session_detail": "GET /sessions/{session_id}",
                "session_runs": "GET /sessions/{session_id}/runs",
                "health": "GET /health",
                "info": "GET /info",
                "docs": "GET /docs",
            },
            "examples": [
                {
                    "with_file": 'curl -X POST "http://localhost:7777/agents/doc-agent/runs" -F "message=Summarize this" -F "files=@doc.pdf" -F "session_id=user123"'
                },
                {
                    "without_file": 'curl -X POST "http://localhost:7777/agents/doc-agent/runs" -F "message=What is AI?" -F "session_id=user123"'
                },
                {"list_sessions": 'curl -X GET "http://localhost:7777/sessions"'},
                {"get_session": 'curl -X GET "http://localhost:7777/sessions/user123"'},
            ],
        }
    )


app.include_router(custom_router)

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    agent_os.serve(
        app="agent-api:app",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )
