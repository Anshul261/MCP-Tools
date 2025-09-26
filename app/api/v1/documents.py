from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
import uuid
import os
import shutil
from datetime import datetime
from pathlib import Path

from ...core.streaming import DocumentProcessingStreamer, streaming_manager, create_sse_response
from ...models.requests import DocumentQuery, ReindexRequest, DocumentProcessingStatus
from ...models.responses import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    ReindexResponse,
    DocumentInfo
)
from ...core.agents import get_knowledge_base, get_document_processor
from ...core.database import get_document_storage

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

# Configuration
UPLOAD_DIR = Path("documents")
CONVERTED_DIR = Path("converted_docs")

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
CONVERTED_DIR.mkdir(exist_ok=True)

# Dependencies
async def get_knowledge_base_system():
    return get_knowledge_base()

async def get_processor():
    return get_document_processor()

async def get_doc_storage():
    return get_document_storage()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    auto_process: bool = Form(True),
    kb = Depends(get_knowledge_base_system),
    processor = Depends(get_processor),
    storage = Depends(get_doc_storage)
):
    """
    Upload and process a document
    
    Supports various document formats and triggers automatic knowledge base updates.
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.md'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate document ID and save file
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        file_path = UPLOAD_DIR / f"{document_id}_{file.filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create document record
        document_info = DocumentInfo(
            document_id=document_id,
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=file_path.stat().st_size,
            status=DocumentProcessingStatus.PENDING,
            created_at=datetime.utcnow(),
            description=description,
            tags=tag_list,
            metadata={
                "file_path": str(file_path),
                "original_filename": file.filename,
                "upload_source": "api"
            }
        )
        
        # Store document metadata
        await storage.create_document(document_info.dict())
        
        if auto_process:
            # Start processing in background
            try:
                await processor.process_document_async(document_id, str(file_path), kb)
                document_info.status = DocumentProcessingStatus.PROCESSING
                await storage.update_document_status(document_id, DocumentProcessingStatus.PROCESSING)
                
            except Exception as e:
                document_info.status = DocumentProcessingStatus.FAILED
                document_info.error_message = str(e)
                await storage.update_document_status(document_id, DocumentProcessingStatus.FAILED, str(e))
        
        return DocumentUploadResponse(
            success=True,
            document=document_info,
            processing_started=auto_process,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if it was created
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.post("/upload/stream")
async def upload_document_stream(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    kb = Depends(get_knowledge_base_system),
    processor = Depends(get_processor)
):
    """
    Upload document with streaming progress updates
    
    Returns Server-Sent Events showing upload and processing progress.
    """
    try:
        # Validate file
        allowed_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.md'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Create streaming handler
        streamer = DocumentProcessingStreamer(streaming_manager)
        
        # Generate document ID
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        # Create async generator for streaming
        async def process_with_stream():
            async for event in streamer.stream_document_processing(
                document_id=document_id,
                user_id="system",
                processing_func=processor.process_document,
                file=file,
                kb=kb,
                description=description,
                tags=tags
            ):
                yield event
        
        return create_sse_response(process_with_stream())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    status: Optional[DocumentProcessingStatus] = Query(None),
    sort_by: str = Query("created_at"),
    sort_desc: bool = Query(True),
    storage = Depends(get_doc_storage)
):
    """
    List processed documents with filtering and pagination
    
    Supports filtering by tags, status, and text search.
    """
    try:
        # Build query parameters
        query_params = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "sort_desc": sort_desc
        }
        
        if tags:
            query_params["tags"] = tags
        if search:
            query_params["search"] = search
        if status:
            query_params["status"] = status.value
        
        # Get documents from storage
        documents_data = await storage.list_documents(**query_params)
        
        # Convert to DocumentInfo objects
        documents = []
        for doc_data in documents_data.get('documents', []):
            documents.append(DocumentInfo(**doc_data))
        
        return DocumentListResponse(
            success=True,
            documents=documents,
            total_count=documents_data.get('total_count', len(documents)),
            page_info={
                "current_page": offset // limit + 1,
                "per_page": limit,
                "has_next": documents_data.get('has_more', False),
                "total_count": documents_data.get('total_count', len(documents))
            },
            filter_info={
                "tags": tags,
                "search": search,
                "status": status.value if status else None
            } if any([tags, search, status]) else None,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    storage = Depends(get_doc_storage)
):
    """
    Get details for a specific document
    
    Returns document metadata and processing status.
    """
    try:
        doc_data = await storage.get_document(document_id)
        
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentInfo(**doc_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    remove_from_kb: bool = Query(True, description="Remove from knowledge base"),
    kb = Depends(get_knowledge_base_system),
    storage = Depends(get_doc_storage)
):
    """
    Delete a document and optionally remove from knowledge base
    
    Removes document files and metadata from the system.
    """
    try:
        # Get document info
        doc_data = await storage.get_document(document_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove files if they exist
        file_path = Path(doc_data.get('metadata', {}).get('file_path', ''))
        if file_path.exists():
            file_path.unlink()
        
        # Remove converted file if it exists
        converted_path = CONVERTED_DIR / f"{file_path.stem}.md"
        if converted_path.exists():
            converted_path.unlink()
        
        removed_from_kb = False
        if remove_from_kb and kb:
            try:
                # Remove from knowledge base (this needs to be implemented based on AGNO KB API)
                await kb.remove_document(document_id)
                removed_from_kb = True
            except Exception as e:
                print(f"Warning: Could not remove from knowledge base: {e}")
        
        # Remove from storage
        await storage.delete_document(document_id)
        
        return DocumentDeleteResponse(
            success=True,
            document_id=document_id,
            removed_from_knowledge_base=removed_from_kb,
            message="Document deleted successfully",
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.post("/reindex", response_model=ReindexResponse)
async def reindex_knowledge_base(
    request: ReindexRequest,
    kb = Depends(get_knowledge_base_system),
    processor = Depends(get_processor),
    storage = Depends(get_doc_storage)
):
    """
    Rebuild knowledge base index
    
    Reprocesses documents and updates the knowledge base index.
    """
    try:
        start_time = datetime.utcnow()
        
        if request.document_ids:
            # Reindex specific documents
            documents_processed = 0
            documents_indexed = 0
            documents_failed = 0
            errors = []
            
            for doc_id in request.document_ids:
                try:
                    doc_data = await storage.get_document(doc_id)
                    if doc_data:
                        file_path = doc_data.get('metadata', {}).get('file_path')
                        if file_path and Path(file_path).exists():
                            await processor.reprocess_document(doc_id, file_path, kb)
                            documents_indexed += 1
                        documents_processed += 1
                except Exception as e:
                    documents_failed += 1
                    errors.append(f"Document {doc_id}: {str(e)}")
        else:
            # Full reindex
            if request.clear_existing:
                await kb.clear()
            
            # Get all documents
            all_docs = await storage.list_documents(limit=1000)  # Adjust as needed
            documents_processed = len(all_docs.get('documents', []))
            documents_indexed = 0
            documents_failed = 0
            errors = []
            
            for doc_data in all_docs.get('documents', []):
                try:
                    file_path = doc_data.get('metadata', {}).get('file_path')
                    if file_path and Path(file_path).exists():
                        await processor.reprocess_document(
                            doc_data['document_id'], 
                            file_path, 
                            kb
                        )
                        documents_indexed += 1
                    else:
                        documents_failed += 1
                        errors.append(f"File not found for document {doc_data['document_id']}")
                except Exception as e:
                    documents_failed += 1
                    errors.append(f"Document {doc_data['document_id']}: {str(e)}")
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ReindexResponse(
            success=True,
            documents_reindexed=documents_processed,
            processing_time=processing_time,
            knowledge_base_size=await kb.get_document_count() if hasattr(kb, 'get_document_count') else 0,
            index_updated=documents_indexed > 0,
            errors=errors if errors else None,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reindexing knowledge base: {str(e)}")

@router.post("/reindex/stream")
async def reindex_knowledge_base_stream(
    request: ReindexRequest,
    kb = Depends(get_knowledge_base_system),
    processor = Depends(get_processor),
    storage = Depends(get_doc_storage)
):
    """
    Rebuild knowledge base with streaming progress
    
    Returns Server-Sent Events showing reindexing progress.
    """
    try:
        streamer = DocumentProcessingStreamer(streaming_manager)
        
        # Create async generator for streaming reindex progress
        async def reindex_with_stream():
            async for event in streamer.stream_document_processing(
                document_id="reindex_operation",
                user_id="system",
                processing_func=processor.reindex_knowledge_base,
                kb=kb,
                request=request,
                storage=storage
            ):
                yield event
        
        return create_sse_response(reindex_with_stream())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting reindex stream: {str(e)}")

@router.get("/stats/overview")
async def get_document_stats(
    storage = Depends(get_doc_storage),
    kb = Depends(get_knowledge_base_system)
):
    """
    Get document statistics and overview
    
    Returns counts by status, file types, and other metrics.
    """
    try:
        stats = await storage.get_document_stats()
        
        # Get knowledge base stats if available
        kb_stats = {}
        if kb and hasattr(kb, 'get_stats'):
            kb_stats = await kb.get_stats()
        
        return {
            "success": True,
            "document_stats": stats,
            "knowledge_base_stats": kb_stats,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document stats: {str(e)}")

@router.get("/processing/status")
async def get_processing_status():
    """
    Get current document processing status
    
    Returns information about ongoing processing operations.
    """
    try:
        # Get active streams related to document processing
        active_streams = []
        for stream_id, stream_info in streaming_manager.active_streams.items():
            if stream_info.get('stream_type') == 'document_processing':
                active_streams.append({
                    "stream_id": stream_id,
                    "document_id": stream_info.get('session_id'),  # document_id stored as session_id
                    "status": stream_info.get('status'),
                    "events_sent": stream_info.get('events_sent', 0),
                    "created_at": stream_info.get('created_at')
                })
        
        return {
            "success": True,
            "active_processing_operations": len(active_streams),
            "operations": active_streams,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving processing status: {str(e)}")