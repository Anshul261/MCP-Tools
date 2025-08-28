import os
import sqlite3
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from contextlib import contextmanager
import json
import logging

from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory

from ..models.requests import DocumentProcessingStatus
from ..models.responses import ChatSession, DocumentInfo, MemoryStats

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations for the API"""
    
    def __init__(self, 
                 memory_db_path: str = "agent_memory.db",
                 storage_db_path: str = "agent_sessions.db",
                 api_db_path: str = "api_data.db"):
        self.memory_db_path = memory_db_path
        self.storage_db_path = storage_db_path
        self.api_db_path = api_db_path
        
        # Initialize existing AGNO database components
        self.memory_db = SqliteMemoryDb(
            table_name="agent_memory",
            db_file=memory_db_path
        )
        
        self.storage = SqliteStorage(
            table_name="agent_sessions", 
            db_file=storage_db_path
        )
        
        self.memory = Memory(db=self.memory_db)
        
        # Initialize API-specific database
        self._init_api_database()
    
    def _init_api_database(self):
        """Initialize API-specific database tables"""
        with self._get_api_connection() as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    content_type TEXT,
                    size_bytes INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    description TEXT,
                    tags TEXT,  -- JSON array
                    pages INTEGER,
                    word_count INTEGER,
                    processing_error TEXT,
                    metadata TEXT,  -- JSON object
                    file_path TEXT,
                    converted_path TEXT
                )
            ''')
            
            # API sessions table (extended version of agent sessions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT,  -- JSON object
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # API requests log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_requests (
                    request_id TEXT PRIMARY KEY,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time REAL,
                    status_code INTEGER,
                    error_message TEXT,
                    metadata TEXT  -- JSON object
                )
            ''')
            
            # Streaming sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS streaming_sessions (
                    stream_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    stream_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP,
                    events_sent INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    metadata TEXT  -- JSON object
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def _get_api_connection(self):
        """Get API database connection with proper cleanup"""
        conn = sqlite3.connect(self.api_db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager 
    def _get_memory_connection(self):
        """Get memory database connection"""
        conn = sqlite3.connect(self.memory_db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def _get_storage_connection(self):
        """Get storage database connection"""
        conn = sqlite3.connect(self.storage_db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

class SessionManager:
    """Manages chat sessions and session-related operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_session(self, user_id: str, title: Optional[str] = None, 
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new chat session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO api_sessions 
                (session_id, user_id, title, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id, user_id, title, 
                json.dumps(metadata) if metadata else None,
                datetime.utcnow(), datetime.utcnow()
            ))
            conn.commit()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session information"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM api_sessions WHERE session_id = ? AND is_active = 1
            ''', (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ChatSession(
                session_id=row['session_id'],
                user_id=row['user_id'],
                title=row['title'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                message_count=row['message_count'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            )
    
    def list_user_sessions(self, user_id: str, limit: int = 20, 
                          offset: int = 0) -> List[ChatSession]:
        """List sessions for a user"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM api_sessions 
                WHERE user_id = ? AND is_active = 1 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append(ChatSession(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    message_count=row['message_count'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                ))
            
            return sessions
    
    def update_session(self, session_id: str, title: Optional[str] = None,
                      increment_messages: bool = False) -> bool:
        """Update session information"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            
            if title is not None:
                cursor.execute('''
                    UPDATE api_sessions 
                    SET title = ?, updated_at = ? 
                    WHERE session_id = ?
                ''', (title, datetime.utcnow(), session_id))
            
            if increment_messages:
                cursor.execute('''
                    UPDATE api_sessions 
                    SET message_count = message_count + 1, updated_at = ? 
                    WHERE session_id = ?
                ''', (datetime.utcnow(), session_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_session(self, session_id: str) -> bool:
        """Soft delete a session"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE api_sessions 
                SET is_active = 0, updated_at = ? 
                WHERE session_id = ?
            ''', (datetime.utcnow(), session_id))
            conn.commit()
            return cursor.rowcount > 0
    

class DocumentManager:
    """Manages document storage and processing tracking"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_document(self, filename: str, size_bytes: int, 
                       content_type: Optional[str] = None,
                       description: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new document record"""
        document_id = str(uuid.uuid4())
        
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents 
                (document_id, filename, content_type, size_bytes, status, 
                 description, tags, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, filename, content_type, size_bytes, 
                DocumentProcessingStatus.PENDING.value,
                description,
                json.dumps(tags) if tags else None,
                json.dumps(metadata) if metadata else None,
                datetime.utcnow()
            ))
            conn.commit()
        
        return document_id
    
    def get_document(self, document_id: str) -> Optional[DocumentInfo]:
        """Get document information"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE document_id = ?', (document_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_document_info(row)
    
    def list_documents(self, limit: int = 20, offset: int = 0,
                      status: Optional[DocumentProcessingStatus] = None,
                      tags: Optional[List[str]] = None,
                      search: Optional[str] = None) -> List[DocumentInfo]:
        """List documents with filtering"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM documents WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if tags:
                # Simple tag search - would be more sophisticated in production
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f'%"{tag}"%')
            
            if search:
                query += " AND (filename LIKE ? OR description LIKE ?)"
                params.extend([f'%{search}%', f'%{search}%'])
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            documents = []
            for row in cursor.fetchall():
                documents.append(self._row_to_document_info(row))
            
            return documents
    
    def update_document_status(self, document_id: str, 
                              status: DocumentProcessingStatus,
                              processing_error: Optional[str] = None,
                              pages: Optional[int] = None,
                              word_count: Optional[int] = None) -> bool:
        """Update document processing status"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            
            update_fields = ["status = ?", "updated_at = ?"]
            params = [status.value, datetime.utcnow()]
            
            if status == DocumentProcessingStatus.COMPLETED:
                update_fields.append("processed_at = ?")
                params.append(datetime.utcnow())
            
            if processing_error is not None:
                update_fields.append("processing_error = ?")
                params.append(processing_error)
            
            if pages is not None:
                update_fields.append("pages = ?")
                params.append(pages)
            
            if word_count is not None:
                update_fields.append("word_count = ?")
                params.append(word_count)
            
            params.append(document_id)
            
            cursor.execute(f'''
                UPDATE documents 
                SET {", ".join(update_fields)}
                WHERE document_id = ?
            ''', params)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document record"""
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM documents WHERE document_id = ?', (document_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_document_info(self, row) -> DocumentInfo:
        """Convert database row to DocumentInfo model"""
        return DocumentInfo(
            document_id=row['document_id'],
            filename=row['filename'],
            content_type=row['content_type'],
            size_bytes=row['size_bytes'],
            status=DocumentProcessingStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            processed_at=datetime.fromisoformat(row['processed_at']) if row['processed_at'] else None,
            description=row['description'],
            tags=json.loads(row['tags']) if row['tags'] else None,
            pages=row['pages'],
            word_count=row['word_count'],
            processing_error=row['processing_error'],
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
    
    
    async def get_document_stats(self) -> dict:
        """Get document statistics"""
        return {
            "total_documents": 0,
            "by_status": {},
            "by_type": {},
            "total_size_mb": 0.0
        }

class MemoryManager:
    """Manages memory and session data using existing AGNO memory system"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.memory = db_manager.memory
    
    def get_memory_stats(self) -> MemoryStats:
        """Get memory database statistics"""
        with self.db._get_memory_connection() as conn:
            cursor = conn.cursor()
            
            # Get memory counts
            cursor.execute('SELECT COUNT(*) as count FROM agent_memory')
            total_memories = cursor.fetchone()['count']
            
            # Get unique users and sessions
            cursor.execute('SELECT COUNT(DISTINCT user_id) as count FROM agent_memory')
            unique_users = cursor.fetchone()['count']
            
            # Get database size
            db_path = Path(self.db.memory_db_path)
            db_size_mb = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0
            
            # Get recent activity
            cursor.execute('''
                SELECT created_at FROM agent_memory 
                ORDER BY created_at DESC LIMIT 1
            ''')
            last_memory_row = cursor.fetchone()
            last_memory_created = None
            if last_memory_row:
                last_memory_created = datetime.fromisoformat(last_memory_row['created_at'])
        
        # Get active sessions count from API sessions
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM api_sessions WHERE is_active = 1')
            active_sessions = cursor.fetchone()['count']
        
        return MemoryStats(
            total_memories=total_memories,
            user_memories=total_memories,  # Simplified for now
            session_summaries=0,  # Would need to query session summaries specifically
            database_size_mb=db_size_mb,
            active_sessions=active_sessions,
            unique_users=unique_users,
            last_memory_created=last_memory_created
        )
    
    def get_user_memories(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories for a specific user"""
        # This would use the AGNO memory system to retrieve user-specific memories
        # For now, return a placeholder
        return []
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary if available"""
        # This would integrate with AGNO session summary functionality
        return None

class APIRequestLogger:
    """Logs API requests for monitoring and analytics"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def log_request(self, endpoint: str, method: str, 
                   user_id: Optional[str] = None,
                   session_id: Optional[str] = None,
                   response_time: Optional[float] = None,
                   status_code: Optional[int] = None,
                   error_message: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log an API request"""
        request_id = str(uuid.uuid4())
        
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO api_requests
                (request_id, endpoint, method, user_id, session_id, 
                 response_time, status_code, error_message, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request_id, endpoint, method, user_id, session_id,
                response_time, status_code, error_message,
                json.dumps(metadata) if metadata else None,
                datetime.utcnow()
            ))
            conn.commit()
        
        return request_id
    
    def get_request_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get request statistics for the past N hours"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        with self.db._get_api_connection() as conn:
            cursor = conn.cursor()
            
            # Total requests
            cursor.execute('''
                SELECT COUNT(*) as count FROM api_requests 
                WHERE timestamp > ?
            ''', (since,))
            total_requests = cursor.fetchone()['count']
            
            # Error rate
            cursor.execute('''
                SELECT COUNT(*) as count FROM api_requests 
                WHERE timestamp > ? AND status_code >= 400
            ''', (since,))
            error_count = cursor.fetchone()['count']
            
            # Average response time
            cursor.execute('''
                SELECT AVG(response_time) as avg_time FROM api_requests 
                WHERE timestamp > ? AND response_time IS NOT NULL
            ''', (since,))
            avg_response_time = cursor.fetchone()['avg_time'] or 0
            
            return {
                'total_requests': total_requests,
                'error_count': error_count,
                'error_rate': error_count / max(total_requests, 1),
                'average_response_time': avg_response_time
            }

# Create global database manager instance
db_manager = DatabaseManager()
session_manager = SessionManager(db_manager)
document_manager = DocumentManager(db_manager)
memory_manager = MemoryManager(db_manager)
request_logger = APIRequestLogger(db_manager)

# Dependency functions for FastAPI
def get_session_storage():
    """Get session storage manager"""
    class AsyncSessionManager:
        def __init__(self, manager):
            self._manager = manager
        
        async def get_sessions(self, user_id: str, limit: int = 20, offset: int = 0):
            sessions = self._manager.list_user_sessions(user_id, limit, offset)
            return {
                "sessions": [session.dict() for session in sessions],
                "total_count": len(sessions),
                "has_more": len(sessions) == limit
            }
        
        async def create_session(self, session_data: dict):
            session_id = self._manager.create_session(
                session_data.get('user_id'),
                session_data.get('title'),
                session_data.get('metadata')
            )
            session_data['session_id'] = session_id
            return session_data
        
        async def session_exists(self, session_id: str):
            session = self._manager.get_session(session_id)
            return session is not None
        
        async def delete_session(self, session_id: str):
            return self._manager.delete_session(session_id)
        
        async def get_session_messages(self, session_id: str, limit: int = 50, offset: int = 0):
            return []
        
        async def health_check(self):
            return "healthy"
    
    return AsyncSessionManager(session_manager)

def get_memory_system():
    """Get memory manager"""
    class AsyncMemoryManager:
        def __init__(self, manager):
            self._manager = manager
        
        async def get_stats(self):
            stats = self._manager.get_memory_stats()
            return stats.dict() if hasattr(stats, 'dict') else stats
        
        async def initialize_session(self, session_id: str, user_id: str):
            return True
        
        async def clear_session(self, session_id: str):
            return True
        
        async def get_recent_activity(self, limit: int = 10):
            return []
        
        async def health_check(self):
            return "healthy"
    
    return AsyncMemoryManager(memory_manager)

def get_document_storage():
    """Get document storage manager"""
    class AsyncDocumentManager:
        def __init__(self, manager):
            self._manager = manager
        
        async def create_document(self, doc_data):
            if hasattr(doc_data, 'dict'):
                doc_data = doc_data.dict()
            return self._manager.create_document(
                doc_data.get('filename', ''),
                doc_data.get('size_bytes', 0),
                doc_data.get('content_type'),
                doc_data.get('description'),
                doc_data.get('tags'),
                doc_data.get('metadata')
            )
        
        async def get_document(self, document_id: str):
            doc = self._manager.get_document(document_id)
            return doc.dict() if doc else None
        
        async def list_documents(self, **kwargs):
            docs = self._manager.list_documents(**kwargs)
            return {
                "documents": [doc.dict() for doc in docs],
                "total_count": len(docs),
                "has_more": len(docs) == kwargs.get('limit', 20)
            }
        
        async def update_document_status(self, document_id: str, status, error_msg=None):
            return self._manager.update_document_status(document_id, status, error_msg)
        
        async def delete_document(self, document_id: str):
            return self._manager.delete_document(document_id)
        
        async def get_document_stats(self):
            return {
                "total_documents": 0,
                "by_status": {},
                "by_type": {},
                "total_size_mb": 0.0
            }
    
    return AsyncDocumentManager(document_manager)