"""
Main Server Application for AI Data Analyst v0.1

Integrates the chatbot backend with the v0.1 frontend for intelligent canvas control.
Based on the proven implementation from tests/python/llm_canvas_chatbot.py.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# FastAPI imports
try:
    from fastapi import FastAPI, WebSocket, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("❌ FastAPI not installed. Install with: pip install fastapi uvicorn websockets")
    sys.exit(1)

# Core imports
try:
    from core.chatbot import chatbot
    from core.canvas_bridge import canvas_bridge
    from api.routes import router
    from api.websocket import websocket_endpoint
except ImportError:
    # Try absolute imports if relative imports fail
    import sys
    from pathlib import Path
    backend_path = Path(__file__).parent
    sys.path.insert(0, str(backend_path))
    
    from core.chatbot import chatbot
    from core.canvas_bridge import canvas_bridge
    from api.routes import router
    from api.websocket import websocket_endpoint


class AIDataAnalystServer:
    """Main server application for AI Data Analyst v0.1"""
    
    def __init__(self):
        self.app = FastAPI(
            title="AI Data Analyst v0.1",
            description="Intelligent canvas control with natural language interface",
            version="0.1.0"
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify exact origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes and static files
        self.setup_routes()
        self.setup_static_files()
        
        print("🚀 AI Data Analyst v0.1 Server initialized")
    
    def setup_routes(self):
        """Setup API routes and WebSocket endpoints"""
        
        # Include API routes
        self.app.include_router(router)
        
        # WebSocket endpoint
        @self.app.websocket("/ws")
        async def websocket_handler(websocket: WebSocket):
            await websocket_endpoint(websocket)
        
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                canvas_state = canvas_bridge.get_canvas_state()
                return {
                    "status": "healthy",
                    "version": "v0.1.0",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "services": {
                        "chatbot": "active",
                        "canvas_bridge": "active",
                        "websocket": "active"
                    },
                    "canvas": {
                        "container_count": canvas_state["containerCount"]
                    }
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
        
        # Root endpoint - serve the frontend
        @self.app.get("/", response_class=HTMLResponse)
        async def serve_frontend():
            """Serve the main frontend page"""
            frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
            
            print(f"🔍 Looking for frontend at: {frontend_path}")
            print(f"🔍 Frontend exists: {frontend_path.exists()}")
            print(f"🔍 Current working directory: {Path.cwd()}")
            
            if not frontend_path.exists():
                raise HTTPException(status_code=404, detail=f"Frontend not found at {frontend_path}")
            
            return FileResponse(frontend_path)
    
    def setup_static_files(self):
        """Setup static file serving for the frontend"""
        frontend_dir = Path(__file__).parent.parent / "frontend"
        
        print(f"🔍 Setting up static files from: {frontend_dir}")
        print(f"🔍 Frontend directory exists: {frontend_dir.exists()}")
        
        if frontend_dir.exists():
            # Mount the frontend directory as static files
            self.app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
            
            # Also serve CSS and JS files directly
            @self.app.get("/styles.css")
            async def serve_css():
                css_path = frontend_dir / "styles.css"
                print(f"🔍 Serving CSS from: {css_path}")
                if css_path.exists():
                    return FileResponse(css_path, media_type="text/css")
                raise HTTPException(status_code=404, detail=f"CSS file not found at {css_path}")
            
            @self.app.get("/script.js")
            async def serve_js():
                js_path = frontend_dir / "script.js"
                print(f"🔍 Serving JS from: {js_path}")
                if js_path.exists():
                    return FileResponse(js_path, media_type="application/javascript")
                raise HTTPException(status_code=404, detail=f"JavaScript file not found at {js_path}")
            
            print(f"✅ Frontend static files mounted from: {frontend_dir}")
        else:
            print(f"⚠️ Frontend directory not found: {frontend_dir}")
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
        """Run the server"""
        print(f"🌐 Starting AI Data Analyst v0.1 Server...")
        print(f"📍 Server will be available at: http://{host}:{port}")
        print(f"🎨 Frontend will be available at: http://{host}:{port}")
        print(f"📡 WebSocket endpoint: ws://{host}:{port}/ws")
        print(f"📚 API documentation: http://{host}:{port}/docs")
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️ Warning: OPENAI_API_KEY environment variable not set.")
            print("   The chatbot will not function without an OpenAI API key.")
            print("   Set it in your environment or .env file.")
        
        try:
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                reload=reload,
                log_level="info"
            )
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")


# Create the FastAPI app instance
server = AIDataAnalystServer()
app = server.app


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🔧 Initializing AI Data Analyst v0.1...")
    
    # Check if chatbot is properly initialized
    if chatbot.llm_client is None:
        print("⚠️ Warning: LLM client not initialized. Check OpenAI API key.")
    else:
        print("✅ Chatbot initialized successfully")
    
    print("✅ AI Data Analyst v0.1 ready!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("🛑 Shutting down AI Data Analyst v0.1...")
    
    # Clear conversation history
    chatbot.clear_conversation_history()
    
    # Clear canvas state
    await canvas_bridge.clear_canvas()
    
    print("✅ Shutdown complete")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Data Analyst v0.1 Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    # Run the server
    server.run(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main() 