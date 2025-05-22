import http.server
import socketserver
import logging
import os
import datetime
import json  # Import the json module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TEMPLATES_DIR = "templates"

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
            self.send_header("Content-type", "application/json")  # Set content type to JSON
            self.end_headers()
            now = datetime.datetime.now()
            uptime_data = {"uptime": str(now)}  # Create a dictionary
            uptime_json = json.dumps(uptime_data)  # Convert to JSON
            self.wfile.write(uptime_json.encode())  # Encode and send
            logging.info(f"Served uptime: {uptime_json}")
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

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    logging.info(f"Starting server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()