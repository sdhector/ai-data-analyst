"""
AI Data Analyst - Main Entry Point

This is the main entry point for the AI Data Analyst application.
It launches the web server that serves the modern web interface.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from adapters.web_adapter.web_server import run_server


def main():
    """Main function to start the AI Data Analyst application"""
    parser = argparse.ArgumentParser(description="AI Data Analyst - Modern Web Application")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the server on (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Automatically open the browser"
    )
    
    args = parser.parse_args()
    
    # Print startup information
    print("\n" + "="*60)
    print("🤖 AI Data Analyst - Modern Web Application")
    print("="*60)
    print(f"\n📍 Server will run at: http://{args.host}:{args.port}")
    print("\n🔧 Features:")
    print("  • Dynamic 6x6 grid system")
    print("  • Natural language data analysis")
    print("  • Real-time visualizations")
    print("  • WebSocket communication")
    print("\n⚡ Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Open browser if requested
    if args.open_browser:
        import webbrowser
        import threading
        import time
        
        def open_browser():
            time.sleep(2)  # Wait for server to start
            webbrowser.open(f"http://{args.host}:{args.port}")
        
        threading.Thread(target=open_browser).start()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables!")
        print("   Please set it in your .env file or environment variables.")
        print("")
    
    # Run the server
    try:
        run_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down AI Data Analyst...")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 