#!/usr/bin/env python3
"""
Startup script for the Data Agent visualization system.
This script helps you start both the backend and frontend components.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if required dependencies are available"""
    print("🔍 Checking system requirements...")
    
    # Check if we're in the right directory
    if not Path("agent.py").exists():
        print("❌ Error: agent.py not found. Please run this script from the Data-agent directory.")
        return False
    
    if not Path("ui").exists():
        print("❌ Error: ui directory not found. Please ensure the UI folder exists.")
        return False
    
    # Check if Node.js is available (for the UI)
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        print("✅ Node.js is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Node.js is not installed or not in PATH")
        return False
    
    # Check if Python dependencies are available
    try:
        import agno
        import fastapi
        print("✅ Python dependencies are available")
    except ImportError as e:
        print(f"❌ Error: Missing Python dependency: {e}")
        return False
    
    print("✅ All requirements met!")
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("\n🚀 Starting Data Agent Backend (Port 7777)...")
    try:
        # Start the agent backend
        backend_process = subprocess.Popen([
            sys.executable, "agent.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if it's still running
        if backend_process.poll() is None:
            print("✅ Backend started successfully!")
            return backend_process
        else:
            print("❌ Backend failed to start")
            return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Next.js frontend"""
    print("\n🎨 Starting Frontend UI (Port 3000)...")
    try:
        # Change to UI directory
        ui_dir = Path("ui")
        
        # Install dependencies if needed
        if not (ui_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=ui_dir, check=True)
        
        # Start the development server
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=ui_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Give it a moment to start
        time.sleep(5)
        
        # Check if it's still running
        if frontend_process.poll() is None:
            print("✅ Frontend started successfully!")
            return frontend_process
        else:
            print("❌ Frontend failed to start")
            return None
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main startup routine"""
    print("🤖 Data Agent Visualization System Startup")
    print("=" * 50)
    
    if not check_requirements():
        print("\n❌ System check failed. Please resolve the issues above.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend  
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend. Stopping backend.")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 System Started Successfully!")
    print("=" * 50)
    print("🔗 Backend API: http://localhost:7777")
    print("🔗 Agent OS UI: http://localhost:7777/docs")
    print("🔗 Custom Chat UI: http://localhost:3000")
    print("\n💡 Tips:")
    print("- Use the Custom Chat UI for the best experience with visualizations")
    print("- Ask questions like: 'Show me monthly ticket trends' or 'Create a chart of categories'")
    print("- Visualizations will appear directly in the chat")
    print("\n⚠️  Press Ctrl+C to stop both services")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n❌ Backend process stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("\n❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        
        # Terminate processes
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            print("✅ Backend stopped")
            
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            print("✅ Frontend stopped")
            
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()