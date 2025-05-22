import http.server
import socketserver
import logging
import os
import datetime
import json
import secrets  # Import the secrets module
import string  # Import the string module
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TEMPLATES_DIR = "templates"
clients = {}  # Dictionary to store connected clients for each endpoint

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
        elif self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if "/events" not in clients:
                clients["/events"] = []
            clients["/events"].append(self.wfile)  # Add client to the list
            logging.info("Client connected to /events event stream.")
            try:
                while True:
                    time.sleep(10)  # Keep connection alive
            except BrokenPipeError:
                clients["/events"].remove(self.wfile)  # Remove client if connection is closed
                logging.info("Client disconnected from /events event stream.")
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if "/health" not in clients:
                clients["/health"] = []
            clients["/health"].append(self.wfile)  # Add client to the list
            logging.info("Client connected to /health event stream.")
            try:
                while True:
                    time.sleep(10)  # Keep connection alive
            except BrokenPipeError:
                clients["/health"].remove(self.wfile)  # Remove client if connection is closed
                logging.info("Client disconnected from /health event stream.")
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

def send_server_sent_event(endpoint, data):
    """Sends a Server-Sent Event to all connected clients."""
    event_string = f"data: {data}\n\n"
    encoded_string = event_string.encode('utf-8')
    if endpoint in clients:
        # Iterate over a copy of the clients list to avoid modification during iteration
        for client in list(clients[endpoint]):
            try:
                client.write(encoded_string)
                client.flush()  # Ensure data is sent immediately
            except (BrokenPipeError, ConnectionResetError):
                clients[endpoint].remove(client)  # Remove client if connection is closed
                logging.info("Client disconnected from event stream.")
            except Exception as e:
                logging.error(f"Error sending event: {e}")
                if client in clients[endpoint]:
                    clients[endpoint].remove(client)

def background_data_generator():
    """Generates random data and sends it to clients via SSE."""
    while True:
        time.sleep(5)  # Send data every 5 seconds
        random_string = ''.join(secrets.choice(string.ascii_letters) for i in range(128))
        data = {"random_string": random_string}
        json_data = json.dumps(data)
        send_server_sent_event("/events", json_data)
        logging.info("Sent random data via SSE.")

def background_health_generator():
    """Generates health data and sends it to clients via SSE."""
    while True:
        time.sleep(10)  # Send data every 10 seconds
        health_data = {"status": "ok"}
        health_json = json.dumps(health_data)
        send_server_sent_event("/health", health_json)
        logging.info("Sent health data via SSE.")

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    logging.info(f"Starting server on port {PORT}...")

    # Start the background data generator thread
    data_thread = threading.Thread(target=background_data_generator)
    data_thread.daemon = True  # Allow the main thread to exit even if this thread is running
    data_thread.start()

    # Start the background health generator thread
    health_thread = threading.Thread(target=background_health_generator)
    health_thread.daemon = True  # Allow the main thread to exit even if this thread is running
    health_thread.start()

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()