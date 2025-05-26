#!/usr/bin/env python3
"""
ICI Chat Application Launcher
Starts the refactored ICI Chat application using the new modular backend structure.
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.app import create_app

if __name__ == "__main__":
    print("Starting ICI Chat with refactored backend...")
    app, socketio = create_app()
    
    # Run the application
    try:
        socketio.run(app, host="0.0.0.0", port=8080, debug=True)
    except KeyboardInterrupt:
        print("\nShutting down ICI Chat...")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
