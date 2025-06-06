#!/usr/bin/env python3
"""
Startup script for AI Data Analyst Backend

Simple script to run the backend server with proper configuration.
"""

import os
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    """Main entry point"""
    print("Starting AI Data Analyst...")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("   Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   or check the .env file in the root directory")
        print()
    
    # Import and run the server
    try:
        # Change to backend directory for proper imports
        os.chdir(backend_dir)
        from main import main as server_main
        server_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("   Make sure you've installed the requirements:")
        print("   pip install -r backend/requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 