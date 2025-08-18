# api/routes/documents.py
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel
import tempfile
from pathlib import Path
import logging

from core.document_processor import doc_processor
from core.database import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


class DocumentInfo(BaseModel):
    """Document information model"""
    filename: str
    size: int
    converted: bool
    converted_path: str = None
    extension: str
    valid: bool


class DocumentStats(BaseModel):
    """Document statistics model"""
    total_documents: int
    converted_documents: int
    total_size_bytes: int
    knowledge_base_loaded: bool
    source_directory: str
    converted_directory: str


class UploadResult(BaseModel):
    """Upload result model"""
    filename: str
    size: int = None
    success: bool
    error: str = None


class ProcessResult(BaseModel):
    """Processing result model"""
    message: str
    total_files: int
    converted: int
    failed: int
    knowledge_base_reloaded: bool


@router.get("/stats", response_model=DocumentStats)
async def get_document_stats():
    """Get statistics about the document collection."""
    try:
        stats = doc_processor.get_document_stats()
        return DocumentStats(**stats)
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document statistics: {str(e)}"
        )


@router.get("", response_model=List[DocumentInfo])
async def list_documents():
    """List all documents in the collection."""
    try:
        documents = doc_processor.list_documents()
        return [DocumentInfo(**doc) for doc in documents]
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.post("/upload", response_model=Dict[str, Any])
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload one or more documents to the collection."""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        temp_file_path = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
            
            # Add document to collection
            result = doc_processor.add_document(temp_file_path, file.filename)
            
            if result["success"]:
                uploaded_files.append(UploadResult(
                    filename=result["filename"],
                    size=result["size"],
                    success=True
                ))
            else:
                failed_files.append(UploadResult(
                    filename=file.filename,
                    success=False,
                    error=result["error"]
                ))
                
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            failed_files.append(UploadResult(
                filename=file.filename,
                success=False,
                error=str(e)
            ))
        finally:
            # Always clean up temp file and close uploaded file
            if temp_file_path and temp_file_path.exists():
                temp_file_path.unlink(missing_ok=True)
            await file.close()
    
    return {
        "message": f"Upload completed. {len(uploaded_files)} files uploaded successfully, {len(failed_files)} failed.",
        "uploaded_files": uploaded_files,
        "failed_files": failed_files,
        "total_uploaded": len(uploaded_files),
        "total_failed": len(failed_files)
    }


@router.post("/convert", response_model=Dict[str, Any])
async def convert_documents():
    """Convert uploaded documents to markdown format."""
    try:
        result = doc_processor.convert_all_documents()
        return result
    except Exception as e:
        logger.error(f"Error during document conversion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document conversion failed: {str(e)}"
        )


@router.post("/knowledge/reload", response_model=Dict[str, str])
async def reload_knowledge_base():
    """Reload the knowledge base with converted documents."""
    try:
        stats = doc_processor.get_document_stats()
        if stats["converted_documents"] == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No converted documents found. Please convert documents first."
            )
        
        await db_manager.initialize_knowledge_base(recreate=True)
        return {"message": "Knowledge base reloaded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reloading knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload knowledge base: {str(e)}"
        )


@router.post("/process", response_model=ProcessResult)
async def process_all_documents():
    """Process all documents: convert to markdown and reload knowledge base."""
    try:
        convert_result = doc_processor.convert_all_documents()
        
        if convert_result["converted"] == 0:
            return ProcessResult(
                message="No documents to process.",
                total_files=convert_result["total_files"],
                converted=0,
                failed=convert_result["failed"],
                knowledge_base_reloaded=False
            )
        
        await db_manager.initialize_knowledge_base(recreate=True)
        
        return ProcessResult(
            message=f"Processing completed. {convert_result['converted']} documents converted and knowledge base reloaded.",
            total_files=convert_result["total_files"],
            converted=convert_result["converted"],
            failed=convert_result["failed"],
            knowledge_base_reloaded=True
        )
        
    except Exception as e:
        logger.error(f"Error during document processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )


@router.delete("/{filename}", response_model=Dict[str, str])
async def delete_document(filename: str):
    """Delete a document from the collection."""
    try:
        result = doc_processor.delete_document(filename)
        
        if not result["success"]:
            if "not found" in result["error"].lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["error"]
                )
        
        return {"message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, Any])
async def get_documents_health():
    """Get health status of document processing system."""
    try:
        stats = doc_processor.get_document_stats()
        
        return {
            "status": "healthy",
            "directories_exist": True,
            "source_directory": stats["source_directory"],
            "converted_directory": stats["converted_directory"],
            "total_documents": stats["total_documents"],
            "converted_documents": stats["converted_documents"],
            "knowledge_base_status": "loaded" if stats["knowledge_base_loaded"] else "empty"
        }
        
    except Exception as e:
        logger.error(f"Document health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "directories_exist": False
        }