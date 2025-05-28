#!/usr/bin/env python3
"""
ICI Chat Application Launcher - Cloud Run Optimized
Single entry point for the lightweight ICI Chat application.
Optimized for Google Cloud Run deployment with <512MB memory usage.
"""
import sys
import os
import subprocess
import threading
import time
from backend.factory import create_app, complete_app_initialization
from graceful_shutdown import get_shutdown_manager

# Configuration
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
PORT = int(os.environ.get("PORT", 8080))  # Cloud Run sets PORT env var
IS_CLOUD_RUN = os.environ.get("K_SERVICE") is not None  # Cloud Run detection

# Only generate SSL certs for local development (not Cloud Run)
if not IS_CLOUD_RUN and not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
    print("[SSL] Local development: Generating self-signed certificate for HTTPS...")
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", KEY_FILE, "-out", CERT_FILE,
            "-days", "365", "-nodes", "-subj", "/CN=localhost"
        ], check=True)
        print(f"[SSL] Generated {CERT_FILE} and {KEY_FILE} for local development.")
    except FileNotFoundError:
        print("[SSL] OpenSSL not found. Running HTTP only for local development.")
    except Exception as e:
        print(f"[SSL] Failed to generate cert: {e}. Running HTTP only for local development.")

if __name__ == "__main__":
    deployment_type = "Cloud Run" if IS_CLOUD_RUN else "Local Development"
    print(f"Starting ICI Chat Lightweight Solution - {deployment_type} Mode")
    print(f"Memory optimized for Cloud Run (<512MB)")

    # Only run shutdown/cleanup logic if not in a Flask code reload
    is_reloader = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    shutdown_mgr = None
    if not is_reloader:
        shutdown_mgr = get_shutdown_manager()
        shutdown_mgr.prepare_for_startup()

    # Create app with lightweight architecture
    print("[STARTUP] Creating lightweight Flask app (no vector database)...")
    app = create_app()

    # Print all registered routes for debugging
    print("[ROUTES] Registered Flask routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule}")

    @app.route("/")
    def root_index_app():
        print(">>> ROOT INDEX ROUTE HIT (app.py) <<<")
        from flask import render_template
        return render_template("index.html")

    use_ssl = CERT_FILE and KEY_FILE and os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)
    if use_ssl:
        print(f"[STARTUP] Running with HTTPS at https://localhost:{PORT}")
        app.run(host="0.0.0.0", port=PORT, debug=True, ssl_context=(CERT_FILE, KEY_FILE))
    else:
        print(f"[STARTUP] Running HTTP only at http://localhost:{PORT}")
        app.run(host="0.0.0.0", port=PORT, debug=True)

    if shutdown_mgr:
        shutdown_mgr.register_app(app, None)

    # SSL only for local development (Cloud Run handles SSL termination)
    use_ssl = not IS_CLOUD_RUN and CERT_FILE and KEY_FILE and os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)    
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
    
    # Start server - Cloud Run or Local Development
    if IS_CLOUD_RUN:
        print(f"[CLOUD RUN] Starting HTTP server on port {PORT} (SSL handled by Cloud Run)")
        print("[STARTUP] Health check available at /health")
        try:
            app.run(host="0.0.0.0", port=PORT, debug=False)
        except Exception as e:
            print(f"[ERROR] Cloud Run server error: {e}")
            sys.exit(1)
    elif use_ssl:
        print(f"[LOCAL] Running with HTTPS at https://localhost:{PORT}")
        print(f"[STARTUP] Loading page available immediately at https://localhost:{PORT}")
        try:
            app.run(host="0.0.0.0", port=PORT, debug=True, ssl_context=(CERT_FILE, KEY_FILE), use_reloader=False)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received keyboard interrupt")
        except Exception as e:
            print(f"[ERROR] Local server error: {e}")
        finally:
            if shutdown_mgr:
                shutdown_mgr.cleanup()
    else:
        print(f"[LOCAL] Running HTTP only at http://localhost:{PORT}")
        print(f"[STARTUP] Loading page available immediately at http://localhost:{PORT}")
        try:
            app.run(host="0.0.0.0", port=PORT, debug=True, use_reloader=False)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Received keyboard interrupt")
        except Exception as e:
            print(f"[ERROR] Local server error: {e}")
        finally:
            if shutdown_mgr:
                shutdown_mgr.cleanup()