import asyncio
import importlib
import logging
import os
import datetime
import json
import secrets
import string
import subprocess  # Import the subprocess module
import sys  # Import the sys module
import websockets
import http.server
import socketserver
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TEMPLATES_DIR = "templates"
connected_clients = {}  # Dictionary to store connected WebSocket clients for each endpoint

# Function to install missing packages
def install_missing_packages(package_name):
    try:
        importlib.import_module(package_name)
    except ImportError:
        logging.warning(f"{package_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logging.info(f"{package_name} installed successfully.")

# Check and install missing packages
install_missing_packages("websockets")
import websockets  # Import websockets after installation check
import importlib  # Import importlib after installation check

async def handle_websocket(websocket, path):
    """Handles WebSocket connections."""
    try:
        logging.info(f"Client connected to WebSocket endpoint: {path}")
        if path not in connected_clients:
            connected_clients[path] = set()
        connected_clients[path].add(websocket)
        try:
            async for message in websocket:
                logging.info(f"Received message from client: {message}")
                # Handle messages from the client if needed
        except websockets.exceptions.ConnectionClosedOK:
            logging.info("Client disconnected normally.")
        except websockets.exceptions.ConnectionClosedError as e:
            logging.error(f"Client disconnected with error: {e}")
        finally:
            connected_clients[path].remove(websocket)
            logging.info(f"Client disconnected from WebSocket endpoint: {path}")
    except Exception as e:
        logging.error(f"Error handling WebSocket connection: {e}")

async def send_websocket_message(endpoint, data):
    """Sends a WebSocket message to all connected clients on a specific endpoint."""
    if endpoint in connected_clients:
        for websocket in connected_clients[endpoint]:
            try:
                await websocket.send(data)
            except websockets.exceptions.ConnectionClosedError:
                logging.info(f"Client disconnected from WebSocket endpoint: {endpoint}")
                connected_clients[endpoint].remove(websocket)
            except Exception as e:
                logging.error(f"Error sending message to client: {e}")
                connected_clients[endpoint].remove(websocket)

async def data_generator():
    """Generates random data and sends it to clients via WebSocket."""
    while True:
        await asyncio.sleep(5)  # Send data every 5 seconds
        random_string = ''.join(secrets.choice(string.ascii_letters) for i in range(128))
        data = {"random_string": random_string}
        json_data = json.dumps(data)
        await send_websocket_message("/events", json_data)
        logging.info("Sent random data via WebSocket.")

async def health_generator():
    """Generates health data and sends it to clients via WebSocket."""
    while True:
        await asyncio.sleep(10)  # Send data every 10 seconds
        health_data = {"status": "ok"}
        health_json = json.dumps(health_data)
        await send_websocket_message("/health", health_json)
        logging.info("Sent health data via WebSocket.")

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            try:
                # Serve index.html from the templates directory
                with open(os.path.join(TEMPLATES_DIR, "index.html"), "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)
                logging.info("Served index.html from templates directory.")
            except FileNotFoundError:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Error: index.html not found in templates directory.")
                logging.error("index.html not found in templates directory.")
        elif self.path == "/uptime":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            now = datetime.datetime.now()
            uptime_data = {"uptime": str(now)}
            uptime_json = json.dumps(uptime_data)
            self.wfile.write(uptime_json.encode())
            logging.info(f"Served uptime: {uptime_json}")
        elif self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            random_string = ''.join(secrets.choice(string.ascii_letters) for i in range(128))  # Generate 128-bit random string
            data = {"random_string": random_string}
            json_data = json.dumps(data)
            self.wfile.write(json_data.encode())
            logging.info("Served random data.")
        elif self.path == "/health.html":  # Serve health.html directly
            try:
                # Serve health.html from the templates directory
                with open(os.path.join(TEMPLATES_DIR, "health.html"), "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)
                logging.info("Served health.html from templates directory.")
            except FileNotFoundError:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Error: health.html not found in templates directory.")
                logging.error("health.html not found in templates directory.")
        else:
            # Serve other static files (if needed)
            filepath = os.path.join(TEMPLATES_DIR, self.path[1:])  # Remove leading slash
            if os.path.exists(filepath) and os.path.isfile(filepath):
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", self.guess_type(filepath))
                    self.end_headers()
                    self.wfile.write(content)
                    logging.info(f"Served static file: {self.path}")
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(f"Error serving file: {str(e)}".encode())
                    logging.error(f"Error serving file: {str(e)}")
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Error: File not found.")
                logging.warning(f"File not found: {self.path}")

async def main():
    """Main function to start the WebSocket server and HTTP server."""
    PORT = int(os.environ.get("PORT", 8080))
    logging.info(f"Starting server on port {PORT}...")

    # Start the WebSocket server
    ws_server = websockets.serve(handle_websocket, "", PORT)

    # Start the data and health generators
    data_task = asyncio.create_task(data_generator())
    health_task = asyncio.create_task(health_generator())

    # Start the HTTP server in a separate thread
    def start_http_server():
        with socketserver.TCPServer(("", PORT+1), MyHandler) as httpd: # Use a different port for the HTTP server
            logging.info(f"Starting HTTP server on port {PORT+1}...")
            httpd.serve_forever()

    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()

    # Run the WebSocket server and the generators concurrently
    try:
        await asyncio.gather(ws_server, data_task, health_task)
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
    finally:
        logging.info("Server shutting down...")

if __name__ == "__main__":
    asyncio.run(main())