"""
AI Data Analyst - Main Entry Point

This is the main entry point for the AI Data Analyst application.
It launches the web server that serves the modern web interface.
"""

import os
import sys
import argparse
from pathlib import Path
import logging

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from adapters.web_adapter.web_server import run_server


def main():
    """Main function to start the AI Data Analyst application"""
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Log to console
        ]
    )

    logger = logging.getLogger(__name__) # Get a logger for main.py

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
    
    # Log startup information
    logger.info("============================================================")
    logger.info("🤖 AI Data Analyst - Modern Web Application")
    logger.info("============================================================")
    logger.info(f"Server will run at: http://{args.host}:{args.port}")
    logger.info("Features:")
    logger.info("  • Dynamic 6x6 grid system")
    logger.info("  • Natural language data analysis")
    logger.info("  • Real-time visualizations")
    logger.info("  • WebSocket communication")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("============================================================")
    
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
        logger.warning("OPENAI_API_KEY not found in environment variables!")
        logger.warning("Please set it in your .env file or environment variables.")
    
    # Run the server
    try:
        run_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("\n\n👋 Shutting down AI Data Analyst...")
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 