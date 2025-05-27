#!/usr/bin/env python3
"""
ICI Chat Application Launcher
Starts the refactored ICI Chat application using the new modular backend structure.
"""
import sys
import os
import subprocess
from backend.app import create_app
from graceful_shutdown import get_shutdown_manager

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
PORT = 8080

# Auto-generate self-signed cert if not present
if not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
    print("[SSL] No cert.pem/key.pem found. Generating self-signed certificate for local HTTPS...")
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", KEY_FILE, "-out", CERT_FILE,
            "-days", "365", "-nodes", "-subj", "/CN=localhost"
        ], check=True)
        print(f"[SSL] Generated {CERT_FILE} and {KEY_FILE}.")
    except FileNotFoundError:
        print("[SSL] OpenSSL not found. Please install OpenSSL and add it to your PATH for automatic HTTPS cert generation.")
        sys.exit(1)
    except Exception as e:
        print(f"[SSL] Failed to generate self-signed cert: {e}\nHTTPS will not be available.")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting ICI Chat with progressive startup...")

    # Only run shutdown/cleanup logic if not in a Flask code reload
    is_reloader = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    shutdown_mgr = None
    if not is_reloader:
        shutdown_mgr = get_shutdown_manager()
        shutdown_mgr.prepare_for_startup()

    # Create app with basic functionality first
    print("[STARTUP] Creating basic Flask app...")
    app, socketio = create_app()

    if shutdown_mgr:
        shutdown_mgr.register_app(app, socketio)

    use_ssl = CERT_FILE and KEY_FILE and os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)
    
    # Start server in background thread to serve loading page immediately
    import threading
    import time
    
    def complete_initialization():
        """Complete app initialization in background"""
        print("[STARTUP] Starting background initialization...")
        time.sleep(1)  # Brief delay to ensure server is responding
        
        from backend.app import complete_app_initialization
        complete_app_initialization(app)
        
        print("[STARTUP] Background initialization complete!")
    
    # Start background initialization
    init_thread = threading.Thread(target=complete_initialization, daemon=True)
    init_thread.start()
    
    # Start server immediately with basic routes
    if use_ssl:
        print("[SSL] Running with HTTPS at https://localhost:8080 ...")
        print("[STARTUP] Loading page available immediately at https://localhost:8080")
        try:
            socketio.run(app, host="0.0.0.0", port=PORT, debug=True, keyfile=KEY_FILE, certfile=CERT_FILE)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received keyboard interrupt")
        except Exception as e:
            print(f"[ERROR] Server error: {e}")
        finally:
            if shutdown_mgr:
                shutdown_mgr.cleanup()
    else:
        print("[SSL] Running without HTTPS (no certs found or generated). Use HTTP only.")
        print("[STARTUP] Loading page available immediately at http://localhost:8080")
        try:
            socketio.run(app, host="0.0.0.0", port=PORT, debug=True)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received keyboard interrupt")
        except Exception as e:
            print(f"[ERROR] Server error: {e}")
        finally:
            if shutdown_mgr:
                shutdown_mgr.cleanup()