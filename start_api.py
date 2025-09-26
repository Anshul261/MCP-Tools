#!/usr/bin/env python3
"""
Startup script for the AGNO Multi-Agent API Server
"""

import os
import sys
from pathlib import Path

def main():
    """Start the AGNO Multi-Agent API Server"""
    
    # Set up environment
    print("🚀 Starting AGNO Multi-Agent API Server...")
    
    # Check if we're in the right directory
    if not Path("multi-agent-system.py").exists():
        print("❌ multi-agent-system.py not found. Please run from the project root directory.")
        return 1
    
    # Add current directory to Python path
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Set default environment variables if not already set
    env_defaults = {
        "ENVIRONMENT": "development",
        "HOST": "0.0.0.0", 
        "PORT": "8000",
        "LOG_LEVEL": "info"
    }
    
    for key, value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print(f"📡 Environment: {os.getenv('ENVIRONMENT')}")
    print(f"🌐 Server will start on: http://{os.getenv('HOST')}:{os.getenv('PORT')}")
    print(f"📖 API Documentation: http://{os.getenv('HOST')}:{os.getenv('PORT')}/docs")
    print(f"📊 Health Check: http://{os.getenv('HOST')}:{os.getenv('PORT')}/health")
    
    # Check dependencies
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: pip install -r requirements-api.txt")
        return 1
    
    # Import and start the application
    try:
        from app.main import app
        import uvicorn
        
        # Configuration
        config = {
            "host": os.getenv("HOST", "0.0.0.0"),
            "port": int(os.getenv("PORT", 8000)),
            "reload": os.getenv("ENVIRONMENT") == "development",
            "log_level": os.getenv("LOG_LEVEL", "info").lower(),
            "workers": 1,
        }
        
        print("\n" + "="*50)
        print("🚀 AGNO Multi-Agent API Server")
        print("="*50)
        print(f"📡 Server: http://{config['host']}:{config['port']}")
        print(f"📖 Docs: http://{config['host']}:{config['port']}/docs")
        print(f"🔧 Environment: {os.getenv('ENVIRONMENT')}")
        print(f"🔄 Auto-reload: {config['reload']}")
        print("="*50)
        print()
        
        # Start the server
        uvicorn.run("app.main:app", **config)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())