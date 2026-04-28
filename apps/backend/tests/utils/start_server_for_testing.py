#!/usr/bin/env python3
"""
Script to start the FastAPI server for testing table management functionality.
"""

import uvicorn
from app.main import create_app

def start_server():
    """Start the FastAPI server for testing."""
    print("🚀 Starting FastAPI server for table management testing...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation will be available at: http://localhost:8000/docs")
    print("🔧 Use Ctrl+C to stop the server")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()
