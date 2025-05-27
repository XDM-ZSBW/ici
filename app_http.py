#!/usr/bin/env python3
"""
ICI Chat Application Launcher - HTTP Only for VS Code Simple Browser Debugging
Forces HTTP-only mode to work around Simple Browser's HTTPS certificate issues.
"""
import sys
import os
import threading
import time
from backend.factory import create_app, complete_app_initialization
from graceful_shutdown import get_shutdown_manager

# Configuration - Force HTTP only
PORT = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    print("Starting ICI Chat - HTTP Only Mode for VS Code Simple Browser")
    print("This mode avoids HTTPS certificate issues in VS Code's embedded browser")

    # Only run shutdown/cleanup logic if not in a Flask code reload
    is_reloader = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    shutdown_mgr = None
    if not is_reloader:
        shutdown_mgr = get_shutdown_manager()
        shutdown_mgr.prepare_for_startup()

    # Create app with lightweight architecture
    print("[STARTUP] Creating lightweight Flask app (no vector database)...")
    app = create_app()

    if shutdown_mgr:
        shutdown_mgr.register_app(app, None)

    # Start server in background thread to serve loading page immediately
    def complete_initialization():
        """Complete app initialization in background"""
        print("[STARTUP] Starting background initialization...")
        time.sleep(1)  # Brief delay to ensure server is responding
        
        complete_app_initialization(app)
        
        print("[STARTUP] Lightweight initialization complete!")
    
    # Start background initialization
    init_thread = threading.Thread(target=complete_initialization, daemon=True)
    init_thread.start()
    
    # Start HTTP-only server for VS Code debugging
    print(f"[LOCAL] Running HTTP only at http://localhost:{PORT}")
    print(f"[STARTUP] Chat page available at http://localhost:{PORT}/chat")
    print("[DEBUG] This HTTP-only mode is for VS Code Simple Browser debugging")
    print("[NOTICE] Some features requiring HTTPS (like screenshots) may not work")
    
    try:
        app.run(host="0.0.0.0", port=PORT, debug=True)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Received keyboard interrupt")
    except Exception as e:
        print(f"[ERROR] Local server error: {e}")
    finally:
        if shutdown_mgr:
            shutdown_mgr.cleanup()
