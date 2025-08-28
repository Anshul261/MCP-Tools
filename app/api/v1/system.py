from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, Any
import time
import os
import psutil
from datetime import datetime, timedelta
from pathlib import Path

from ...models.requests import HealthCheckRequest, MemoryQuery
from ...models.responses import (
    HealthResponse,
    MemoryStatusResponse,
    AgentStatusResponse,
    ComponentStatus,
    MemoryStats,
    AgentStatus
)
from ...core.agents import get_agent_system, get_knowledge_base
from ...core.database import get_session_storage, get_memory_system, get_document_storage
from ...core.streaming import streaming_manager

router = APIRouter(prefix="/api/v1/system", tags=["system"])

# Track application start time
APP_START_TIME = time.time()

# Dependencies
async def get_agents():
    return get_agent_system()

async def get_storage():
    return get_session_storage()

async def get_memory():
    return get_memory_system()

async def get_kb():
    return get_knowledge_base()

async def get_doc_storage():
    return get_document_storage()

@router.get("/health", response_model=HealthResponse)
async def health_check(
    detailed: bool = Query(False, description="Include detailed component status"),
    check_db: bool = Query(True, description="Check database connectivity"),
    check_agents: bool = Query(True, description="Check agent availability"),
    check_knowledge_base: bool = Query(True, description="Check knowledge base status"),
    agents = Depends(get_agents) if True else None,
    storage = Depends(get_storage) if True else None,
    memory = Depends(get_memory) if True else None,
    kb = Depends(get_kb) if True else None,
    doc_storage = Depends(get_doc_storage) if True else None
):
    """
    System health check endpoint
    
    Returns overall system status and component health information.
    """
    try:
        components = []
        overall_status = "healthy"
        
        # System uptime
        uptime_seconds = time.time() - APP_START_TIME
        
        if detailed:
            # Check system resources
            try:
                memory_usage = psutil.virtual_memory()
                disk_usage = psutil.disk_usage('/')
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # System resources component
                system_status = "healthy"
                if memory_usage.percent > 90 or disk_usage.percent > 90 or cpu_percent > 90:
                    system_status = "degraded"
                    overall_status = "degraded"
                
                components.append(ComponentStatus(
                    name="System Resources",
                    status=system_status,
                    details=f"Memory: {memory_usage.percent:.1f}%, Disk: {disk_usage.percent:.1f}%, CPU: {cpu_percent:.1f}%",
                    last_check=datetime.utcnow(),
                    response_time=0.1,
                    metadata={
                        "memory_used_gb": round(memory_usage.used / (1024**3), 2),
                        "memory_total_gb": round(memory_usage.total / (1024**3), 2),
                        "disk_used_gb": round(disk_usage.used / (1024**3), 2),
                        "disk_total_gb": round(disk_usage.total / (1024**3), 2),
                        "cpu_count": psutil.cpu_count(),
                        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
                    }
                ))
            except Exception as e:
                components.append(ComponentStatus(
                    name="System Resources",
                    status="unhealthy",
                    details=f"Error checking system resources: {str(e)}",
                    last_check=datetime.utcnow()
                ))
                overall_status = "degraded"
        
        # Check databases
        if check_db:
            # Memory database check
            try:
                if memory:
                    # Test memory system connection
                    memory_status = await memory.health_check() if hasattr(memory, 'health_check') else "healthy"
                    components.append(ComponentStatus(
                        name="Memory Database",
                        status="healthy" if memory_status == "healthy" else "degraded",
                        details="Memory system operational",
                        last_check=datetime.utcnow(),
                        response_time=0.05
                    ))
                else:
                    components.append(ComponentStatus(
                        name="Memory Database",
                        status="unavailable",
                        details="Memory system not initialized",
                        last_check=datetime.utcnow()
                    ))
                    if overall_status == "healthy":
                        overall_status = "degraded"
            except Exception as e:
                components.append(ComponentStatus(
                    name="Memory Database",
                    status="unhealthy",
                    details=f"Memory database error: {str(e)}",
                    last_check=datetime.utcnow()
                ))
                overall_status = "degraded"
            
            # Session storage check
            try:
                if storage:
                    storage_status = await storage.health_check() if hasattr(storage, 'health_check') else "healthy"
                    components.append(ComponentStatus(
                        name="Session Storage",
                        status="healthy" if storage_status == "healthy" else "degraded",
                        details="Session storage operational",
                        last_check=datetime.utcnow(),
                        response_time=0.05
                    ))
                else:
                    components.append(ComponentStatus(
                        name="Session Storage",
                        status="unavailable",
                        details="Session storage not initialized",
                        last_check=datetime.utcnow()
                    ))
            except Exception as e:
                components.append(ComponentStatus(
                    name="Session Storage",
                    status="unhealthy",
                    details=f"Session storage error: {str(e)}",
                    last_check=datetime.utcnow()
                ))
                overall_status = "degraded"
            
            # Document storage check
            try:
                if doc_storage:
                    doc_status = await doc_storage.health_check() if hasattr(doc_storage, 'health_check') else "healthy"
                    components.append(ComponentStatus(
                        name="Document Storage",
                        status="healthy" if doc_status == "healthy" else "degraded",
                        details="Document storage operational",
                        last_check=datetime.utcnow(),
                        response_time=0.05
                    ))
            except Exception as e:
                components.append(ComponentStatus(
                    name="Document Storage",
                    status="unhealthy",
                    details=f"Document storage error: {str(e)}",
                    last_check=datetime.utcnow()
                ))
        
        # Check knowledge base
        if check_knowledge_base:
            try:
                if kb:
                    kb_status = "healthy"
                    kb_details = "Knowledge base operational"
                    
                    # Check if knowledge base has documents
                    if hasattr(kb, 'get_document_count'):
                        doc_count = await kb.get_document_count()
                        kb_details = f"Knowledge base operational with {doc_count} documents"
                    
                    components.append(ComponentStatus(
                        name="Knowledge Base",
                        status=kb_status,
                        details=kb_details,
                        last_check=datetime.utcnow(),
                        response_time=0.1
                    ))
                else:
                    components.append(ComponentStatus(
                        name="Knowledge Base",
                        status="unavailable",
                        details="Knowledge base not initialized",
                        last_check=datetime.utcnow()
                    ))
            except Exception as e:
                components.append(ComponentStatus(
                    name="Knowledge Base",
                    status="unhealthy",
                    details=f"Knowledge base error: {str(e)}",
                    last_check=datetime.utcnow()
                ))
                overall_status = "degraded"
        
        # Check agents
        if check_agents:
            try:
                if agents:
                    agent_status = "healthy"
                    agent_details = "Agent system operational"
                    
                    # Check if we can get agent info
                    if hasattr(agents, 'get_agent_info'):
                        agent_info = await agents.get_agent_info()
                        agent_count = len(agent_info) if agent_info else 0
                        agent_details = f"Agent system operational with {agent_count} agents"
                    
                    components.append(ComponentStatus(
                        name="Agent System",
                        status=agent_status,
                        details=agent_details,
                        last_check=datetime.utcnow(),
                        response_time=0.1
                    ))
                else:
                    components.append(ComponentStatus(
                        name="Agent System",
                        status="unavailable",
                        details="Agent system not initialized",
                        last_check=datetime.utcnow()
                    ))
                    if overall_status == "healthy":
                        overall_status = "degraded"
            except Exception as e:
                components.append(ComponentStatus(
                    name="Agent System",
                    status="unhealthy",
                    details=f"Agent system error: {str(e)}",
                    last_check=datetime.utcnow()
                ))
                overall_status = "degraded"
        
        # Check streaming system
        if detailed:
            try:
                active_streams = len(streaming_manager.active_streams)
                stream_status = "healthy" if active_streams < 100 else "degraded"  # Arbitrary threshold
                
                components.append(ComponentStatus(
                    name="Streaming System",
                    status=stream_status,
                    details=f"Streaming system operational with {active_streams} active streams",
                    last_check=datetime.utcnow(),
                    response_time=0.01,
                    metadata={"active_streams": active_streams}
                ))
            except Exception as e:
                components.append(ComponentStatus(
                    name="Streaming System",
                    status="unhealthy",
                    details=f"Streaming system error: {str(e)}",
                    last_check=datetime.utcnow()
                ))
        
        # System information
        system_info = {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name,
            "architecture": os.uname().machine if hasattr(os, 'uname') else "unknown",
            "working_directory": str(Path.cwd()),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        if detailed:
            system_info.update({
                "process_id": os.getpid(),
                "thread_count": psutil.Process().num_threads() if psutil else None,
                "file_descriptors": psutil.Process().num_fds() if psutil and hasattr(psutil.Process(), 'num_fds') else None
            })
        
        return HealthResponse(
            success=True,
            overall_status=overall_status,
            components=components,
            system_info=system_info,
            uptime_seconds=uptime_seconds,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/memory-status", response_model=MemoryStatusResponse)
async def get_memory_status(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    include_recent: bool = Query(True, description="Include recent activity"),
    memory = Depends(get_memory),
    storage = Depends(get_storage)
):
    """
    Get memory database statistics and status
    
    Returns detailed information about the memory system.
    """
    try:
        if not memory:
            raise HTTPException(status_code=503, detail="Memory system not available")
        
        # Get memory statistics
        memory_stats = MemoryStats(
            total_memories=0,
            user_memories=0,
            session_summaries=0,
            database_size_mb=0.0,
            active_sessions=0,
            unique_users=0
        )
        
        # Try to get actual stats from memory system
        if hasattr(memory, 'get_stats'):
            stats = await memory.get_stats()
            memory_stats = MemoryStats(
                total_memories=stats.get('total_memories', 0),
                user_memories=stats.get('user_memories', 0),
                session_summaries=stats.get('session_summaries', 0),
                database_size_mb=stats.get('database_size_mb', 0.0),
                active_sessions=stats.get('active_sessions', 0),
                unique_users=stats.get('unique_users', 0),
                last_memory_created=stats.get('last_memory_created')
            )
        else:
            # Get basic stats from files if available
            memory_db_path = Path("agent_memory.db")
            if memory_db_path.exists():
                memory_stats.database_size_mb = memory_db_path.stat().st_size / (1024 * 1024)
        
        # Get storage information
        storage_info = {}
        if storage:
            if hasattr(storage, 'get_stats'):
                storage_info = await storage.get_stats()
            else:
                storage_db_path = Path("agent_sessions.db")
                if storage_db_path.exists():
                    storage_info = {
                        "database_size_mb": storage_db_path.stat().st_size / (1024 * 1024),
                        "database_path": str(storage_db_path)
                    }
        
        # Get recent activity
        recent_activity = []
        if include_recent and hasattr(memory, 'get_recent_activity'):
            try:
                recent_activity = await memory.get_recent_activity(limit=10)
            except Exception as e:
                print(f"Warning: Could not get recent activity: {e}")
        
        return MemoryStatusResponse(
            success=True,
            memory_stats=memory_stats,
            storage_info=storage_info,
            recent_activity=recent_activity,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting memory status: {str(e)}")

@router.get("/agents/status", response_model=AgentStatusResponse)
async def get_agents_status(
    agents = Depends(get_agents),
    kb = Depends(get_kb)
):
    """
    Get agent availability and configuration status
    
    Returns detailed information about all agents in the system.
    """
    try:
        if not agents:
            raise HTTPException(status_code=503, detail="Agent system not available")
        
        agent_statuses = []
        
        # Try to get agent information from the system
        if hasattr(agents, 'get_members'):
            # For team-based agent systems
            members = agents.get_members()
            for member in members:
                try:
                    status = AgentStatus(
                        agent_name=getattr(member, 'name', 'Unknown'),
                        agent_type="team_member",
                        status="available",
                        model_info={
                            "model_id": getattr(member.model, 'id', 'unknown') if hasattr(member, 'model') else 'unknown',
                            "provider": getattr(member.model, 'provider', 'unknown') if hasattr(member, 'model') else 'unknown'
                        },
                        capabilities=[
                            "chat",
                            "memory" if getattr(member, 'memory', None) else None,
                            "tools" if getattr(member, 'tools', None) else None,
                            "knowledge_search" if getattr(member, 'search_knowledge', False) else None
                        ],
                        last_activity=None,  # Would need to track this
                        total_requests=0,    # Would need to track this
                        error_rate=0.0       # Would need to track this
                    )
                    # Filter out None capabilities
                    status.capabilities = [cap for cap in status.capabilities if cap is not None]
                    agent_statuses.append(status)
                except Exception as e:
                    print(f"Warning: Could not get status for agent {getattr(member, 'name', 'unknown')}: {e}")
        
        elif hasattr(agents, 'name'):
            # For single agent or team
            agent_statuses.append(AgentStatus(
                agent_name=agents.name,
                agent_type="team" if hasattr(agents, 'members') else "single",
                status="available",
                model_info={
                    "model_id": getattr(agents.model, 'id', 'unknown') if hasattr(agents, 'model') else 'unknown',
                    "provider": getattr(agents.model, 'provider', 'unknown') if hasattr(agents, 'model') else 'unknown'
                },
                capabilities=[
                    "chat",
                    "memory" if getattr(agents, 'memory', None) else None,
                    "tools" if getattr(agents, 'tools', None) else None,
                    "knowledge_search" if getattr(agents, 'search_knowledge', False) else None,
                    "team_coordination" if hasattr(agents, 'members') else None
                ],
                last_activity=None,
                total_requests=0,
                error_rate=0.0
            ))
            # Filter out None capabilities
            agent_statuses[-1].capabilities = [cap for cap in agent_statuses[-1].capabilities if cap is not None]
        
        # System information
        system_info = {
            "total_agents": len(agent_statuses),
            "available_agents": len([a for a in agent_statuses if a.status == "available"]),
            "team_mode": hasattr(agents, 'members'),
            "coordination_mode": getattr(agents, 'mode', 'unknown') if hasattr(agents, 'mode') else 'unknown'
        }
        
        # Knowledge base information
        knowledge_base_info = None
        if kb:
            try:
                kb_info = {
                    "status": "available",
                    "type": type(kb).__name__,
                    "vector_db_type": type(getattr(kb, 'vector_db', None)).__name__ if getattr(kb, 'vector_db', None) else 'unknown'
                }
                
                if hasattr(kb, 'get_document_count'):
                    kb_info['document_count'] = await kb.get_document_count()
                
                knowledge_base_info = kb_info
            except Exception as e:
                knowledge_base_info = {"status": "error", "error": str(e)}
        
        return AgentStatusResponse(
            success=True,
            agents=agent_statuses,
            system_info=system_info,
            knowledge_base_info=knowledge_base_info,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")

@router.get("/info")
async def get_system_info():
    """
    Get general system information
    
    Returns basic system details and API information.
    """
    try:
        return {
            "success": True,
            "system_info": {
                "name": "AGNO Multi-Agent API",
                "version": "1.0.0",
                "description": "REST API for AGNO multi-agent system with streaming support",
                "uptime_seconds": time.time() - APP_START_TIME,
                "start_time": datetime.fromtimestamp(APP_START_TIME).isoformat(),
                "current_time": datetime.utcnow().isoformat(),
                "environment": os.getenv("ENVIRONMENT", "development"),
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
            },
            "api_info": {
                "version": "v1",
                "endpoints": {
                    "chat": "/api/v1/chat",
                    "documents": "/api/v1/documents", 
                    "system": "/api/v1/system"
                },
                "features": [
                    "streaming_responses",
                    "session_management",
                    "document_processing",
                    "knowledge_base_search",
                    "multi_agent_coordination",
                    "memory_persistence"
                ],
                "streaming_formats": ["server_sent_events", "json"],
                "supported_document_types": [".pdf", ".docx", ".pptx", ".txt", ".md"]
            },
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")

@router.get("/metrics")
async def get_system_metrics():
    """
    Get system performance metrics
    
    Returns detailed performance and usage statistics.
    """
    try:
        metrics = {
            "success": True,
            "timestamp": datetime.utcnow(),
            "uptime_seconds": time.time() - APP_START_TIME
        }
        
        # System metrics
        try:
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            metrics["system"] = {
                "memory": {
                    "used_percent": memory_info.percent,
                    "used_gb": round(memory_info.used / (1024**3), 2),
                    "total_gb": round(memory_info.total / (1024**3), 2),
                    "available_gb": round(memory_info.available / (1024**3), 2)
                },
                "disk": {
                    "used_percent": disk_info.percent,
                    "used_gb": round(disk_info.used / (1024**3), 2),
                    "total_gb": round(disk_info.total / (1024**3), 2),
                    "free_gb": round(disk_info.free / (1024**3), 2)
                },
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": psutil.cpu_count(),
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
                }
            }
        except Exception as e:
            metrics["system"] = {"error": f"Could not get system metrics: {str(e)}"}
        
        # Streaming metrics
        try:
            streaming_metrics = {
                "active_streams": len(streaming_manager.active_streams),
                "total_streams_created": len(streaming_manager.stream_history),
                "streams_by_type": {}
            }
            
            # Count streams by type
            for stream_info in streaming_manager.active_streams.values():
                stream_type = stream_info.get('stream_type', 'unknown')
                streaming_metrics["streams_by_type"][stream_type] = streaming_metrics["streams_by_type"].get(stream_type, 0) + 1
            
            metrics["streaming"] = streaming_metrics
        except Exception as e:
            metrics["streaming"] = {"error": f"Could not get streaming metrics: {str(e)}"}
        
        # Database file sizes
        try:
            db_metrics = {}
            for db_name, db_path in [
                ("memory", "agent_memory.db"),
                ("sessions", "agent_sessions.db"),
                ("documents", "documents.db")  # Assuming document storage uses SQLite
            ]:
                path = Path(db_path)
                if path.exists():
                    size_mb = path.stat().st_size / (1024 * 1024)
                    db_metrics[db_name] = {
                        "size_mb": round(size_mb, 2),
                        "path": str(path),
                        "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                    }
                else:
                    db_metrics[db_name] = {"status": "not_found"}
            
            metrics["databases"] = db_metrics
        except Exception as e:
            metrics["databases"] = {"error": f"Could not get database metrics: {str(e)}"}
        
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system metrics: {str(e)}")