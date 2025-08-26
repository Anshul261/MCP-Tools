# core/document_processor.py
from pathlib import Path
from typing import List, Dict, Any
from docling.document_converter import DocumentConverter
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document conversion and processing"""
    
    def __init__(self):
        self.converter = DocumentConverter()
        self.src_dir = settings.documents.source_dir
        self.converted_dir = settings.documents.converted_dir
        self.allowed_extensions = settings.documents.allowed_extensions
        self.max_file_size = settings.documents.max_file_size
    
    def is_valid_file(self, file_path: Path) -> tuple[bool, str]:
        """Check if file is valid for processing"""
        if not file_path.exists():
            return False, "File does not exist"
        
        if not file_path.is_file():
            return False, "Not a file"
        
        if file_path.suffix.lower() not in self.allowed_extensions:
            return False, f"Unsupported file type. Allowed: {self.allowed_extensions}"
        
        if file_path.stat().st_size > self.max_file_size:
            return False, f"File too large. Max size: {self.max_file_size / (1024*1024):.1f}MB"
        
        return True, "Valid"
    
    def convert_single_document(self, file_path: Path) -> Dict[str, Any]:
        """Convert a single document to markdown"""
        try:
            # Validate file
            is_valid, message = self.is_valid_file(file_path)
            if not is_valid:
                return {
                    "filename": file_path.name,
                    "success": False,
                    "error": message
                }
            
            # Convert document
            result = self.converter.convert(file_path)
            
            # Save markdown
            md_path = self.converted_dir / f"{file_path.stem}.md"
            md_path.write_text(result.document.export_to_markdown(), encoding='utf-8')
            
            logger.info(f"Converted {file_path.name} -> {md_path.name}")
            
            return {
                "filename": file_path.name,
                "success": True,
                "converted_path": str(md_path),
                "size": file_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Error converting {file_path.name}: {e}")
            return {
                "filename": file_path.name,
                "success": False,
                "error": str(e)
            }
    
    async def convert_all_documents(self, skip_existing: bool = True) -> Dict[str, Any]:
        """Convert all documents in source directory"""
        if not self.src_dir.exists():
            return {
                "total_files": 0,
                "converted": 0,
                "failed": 0,
                "skipped": 0,
                "results": [],
                "message": "Source directory does not exist"
            }
        
        # Ensure converted directory exists
        self.converted_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all files to convert
        all_files = [
            f for f in self.src_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in self.allowed_extensions
        ]
        
        if not all_files:
            return {
                "total_files": 0,
                "converted": 0,
                "failed": 0,
                "skipped": 0,
                "results": [],
                "message": "No valid files found for conversion"
            }
        
        # Filter out files that already exist in vector DB if skip_existing is True
        files_to_convert = []
        skipped_count = 0
        
        if skip_existing:
            # Import here to avoid circular imports
            from core.database import db_manager
            
            try:
                existing_docs = await db_manager.get_documents_in_vector_db()
                logger.info(f"Found {len(existing_docs)} existing documents in vector DB")
                
                for file_path in all_files:
                    if file_path.name in existing_docs:
                        logger.info(f"Skipping conversion for {file_path.name} - already exists in vector database")
                        skipped_count += 1
                    else:
                        files_to_convert.append(file_path)
            except Exception as e:
                logger.warning(f"Could not check existing documents, processing all: {e}")
                files_to_convert = all_files
        else:
            files_to_convert = all_files
        
        if not files_to_convert:
            return {
                "total_files": len(all_files),
                "converted": 0,
                "failed": 0,
                "skipped": skipped_count,
                "results": [],
                "message": f"All {len(all_files)} documents already exist in vector database"
            }
        
        # Convert files
        results = []
        converted_count = 0
        failed_count = 0
        
        for file_path in files_to_convert:
            result = self.convert_single_document(file_path)
            results.append(result)
            
            if result["success"]:
                converted_count += 1
            else:
                failed_count += 1
        
        return {
            "total_files": len(all_files),
            "converted": converted_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "results": results,
            "message": f"Converted {converted_count} documents, {failed_count} failed, {skipped_count} skipped"
        }
    
    def add_document(self, file_path: Path, filename: str = None) -> Dict[str, Any]:
        """Add a new document to the source directory"""
        try:
            if not file_path.exists():
                return {"success": False, "error": "Source file does not exist"}
            
            # Determine destination filename
            dest_filename = filename or file_path.name
            dest_path = self.src_dir / dest_filename
            
            # Check if file already exists
            if dest_path.exists():
                return {"success": False, "error": f"File {dest_filename} already exists"}
            
            # Validate file before copying
            is_valid, message = self.is_valid_file(file_path)
            if not is_valid:
                return {"success": False, "error": message}
            
            # Ensure source directory exists
            self.src_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            dest_path.write_bytes(file_path.read_bytes())
            
            logger.info(f"Added document: {dest_filename}")
            
            return {
                "success": True,
                "filename": dest_filename,
                "size": dest_path.stat().st_size,
                "path": str(dest_path)
            }
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_document(self, filename: str) -> Dict[str, Any]:
        """Delete a document and its converted version"""
        try:
            src_file = self.src_dir / filename
            if not src_file.exists():
                return {"success": False, "error": f"Document {filename} not found"}
            
            # Remove source file
            src_file.unlink()
            
            # Remove converted file if it exists
            converted_file = self.converted_dir / f"{src_file.stem}.md"
            if converted_file.exists():
                converted_file.unlink()
            
            logger.info(f"Deleted document: {filename}")
            
            return {
                "success": True,
                "message": f"Document {filename} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting document {filename}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about documents"""
        total_docs = 0
        converted_docs = 0
        total_size = 0
        
        if self.src_dir.exists():
            src_files = [f for f in self.src_dir.iterdir() if f.is_file()]
            total_docs = len(src_files)
            total_size = sum(f.stat().st_size for f in src_files)
        
        if self.converted_dir.exists():
            converted_files = [f for f in self.converted_dir.iterdir() if f.is_file()]
            converted_docs = len(converted_files)
        
        return {
            "total_documents": total_docs,
            "converted_documents": converted_docs,
            "total_size_bytes": total_size,
            "knowledge_base_loaded": self.converted_dir.exists() and converted_docs > 0,
            "source_directory": str(self.src_dir),
            "converted_directory": str(self.converted_dir)
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents with their status"""
        documents = []
        
        if not self.src_dir.exists():
            return documents
        
        for file_path in self.src_dir.iterdir():
            if not file_path.is_file():
                continue
            
            # Check if converted version exists
            converted_path = self.converted_dir / f"{file_path.stem}.md"
            converted = converted_path.exists()
            
            documents.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "converted": converted,
                "converted_path": str(converted_path) if converted else None,
                "extension": file_path.suffix.lower(),
                "valid": file_path.suffix.lower() in self.allowed_extensions
            })
        
        return documents


# Global document processor instance
doc_processor = DocumentProcessor()