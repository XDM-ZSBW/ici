import http.server
import socketserver
import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

VERSION = "1.0.0"  # Or read from a file, environment variable, etc.

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<!DOCTYPE html>\n")
            self.wfile.write(b"<html lang='en'>\n")
            self.wfile.write(b"<head>\n")
            self.wfile.write(b"<meta charset='utf-8'>\n")
            self.wfile.write(b"<title>Hello World!</title>\n")
            self.wfile.write(b"</head>\n")
            self.wfile.write(b"<body>\n")
            self.wfile.write(b"<h1>Hello World!</h1>\n")
            self.wfile.write(b"<p>This is a simple HTTP server.</p>\n")
            # Add version indicator
            self.wfile.write(b"<p style='color: #ccc; font-size: smaller;'>Version: " + VERSION.encode() + b"</p>\n")
            self.wfile.write(b"</body>\n")
            self.wfile.write(b"</html>\n")
            logging.info("Served Hello World page.")
        elif self.path == "/uptime":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            uptime_str = "System Uptime: " + str(datetime.datetime.now())
            self.wfile.write(uptime_str.encode())
            logging.info(f"Served uptime: {uptime_str}")
        else:
            super().do_GET()  # Serve other files normally

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    logging.info(f"Starting server on port {PORT}...")
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()