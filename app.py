import subprocess
import sys
import http.server
import socketserver
import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def install_dependencies():
    """
    Installs the necessary dependencies for the application.
    Specifically, it checks if Flask is installed and installs it if it's not.
    """
    logging.info("Installing dependencies...")
    try:
        import flask
        logging.info("Flask is already installed.")
    except ImportError:
        logging.info("Flask not found. Installing...")
        try:
            # Use the python3 executable explicitly
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "--target", "/app"])
            logging.info("Flask installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Flask: {e}")
            sys.exit(1)  # Exit if installation fails

install_dependencies()

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
            self.wfile.write(b"<p>Served without Flask!</p>\n")
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
    import os
    logging.info("Application starting...")
    if os.environ.get("ENV") == "TEST":
        logging.info("Running tests...")
        unittest.main()
    else:
        logging.info("Starting server...")
        # Use the environment variable defined by Google Cloud Run
        port = int(os.environ.get("PORT", 8080))
        with socketserver.TCPServer(("", port), MyHandler) as httpd:
            logging.info(f"Serving on port {port}...")
            httpd.serve_forever()