#!/usr/bin/env python3
"""
Startup script for the Data Agent Interface

This script starts the custom FastAPI interface for the Data Agent system.
It provides a web-based dashboard for interacting with the AI agents.

Usage:
    python start_interface.py

The interface will be available at:
    - Main Dashboard: http://localhost:7778/dashboard
    - API Docs: http://localhost:7778/docs
    - Agent OS Interface: http://localhost:7778/ (default AgentOS interface)

Features:
    - Interactive dashboard for data analysis
    - Custom endpoints for querying agents
    - File upload capabilities
    - Visualization generation
    - Data export functionality
    - Health monitoring
"""

import uvicorn
import sys
import os
from pathlib import Path

def main():
    """Start the Data Agent Interface"""
    
    print("🚀 Starting Data Agent Interface...")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:7778/dashboard")
    print("📋 API Docs: http://localhost:7778/docs")
    print("🤖 Agent OS: http://localhost:7778/")
    print("=" * 50)
    print()
    
    # Ensure required directories exist
    os.makedirs("output", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    try:
        # Start the server
        uvicorn.run(
            "agent_interface:app",
            host="0.0.0.0",
            port=7778,
            reload=True,
            reload_dirs=["."],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Data Agent Interface...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()