#!/usr/bin/env python3
"""
ICI Chat Application Launcher
Starts the refactored ICI Chat application using the new modular backend structure.
"""
import sys
import os
import subprocess
from backend.app import create_app

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

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
    print("Starting ICI Chat with refactored backend...")
    app, socketio = create_app()
    use_ssl = CERT_FILE and KEY_FILE and os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)
    if use_ssl:
        print("[SSL] Running with HTTPS at https://localhost:8080 ...")
        socketio.run(app, host="0.0.0.0", port=8080, debug=True, keyfile=KEY_FILE, certfile=CERT_FILE)
    else:
        print("[SSL] Running without HTTPS (no certs found or generated). Use HTTP only.")
        socketio.run(app, host="0.0.0.0", port=8080, debug=True)
