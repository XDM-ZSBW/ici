import subprocess
import sys
from flask import Flask, render_template
import datetime
import unittest
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

app = Flask(__name__, template_folder='e:\\zip-myl-dev\\templates'
'')

@app.route("/")
def index():
    """
    Defines the index route for the application.
    Returns:
        str: Content of index.html or an error message if the file is not found.
    """
    logging.info("Index route called.")
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Failed to render index.html: {e}")
        # Report error to health providers (replace with actual reporting mechanism)
        print("ERROR: Could not serve index.html. Please check the file.")  # Echo to console
        return "<h1>Error: index.html not found</h1>", 500  # Return an error response

@app.route("/uptime")
def uptime():
    """
    Defines the uptime route for the application.
    Returns:
        str: A string containing "System Uptime: " followed by the current date and time.
    """
    logging.info("Uptime route called.")
    uptime_str = "System Uptime: " + str(datetime.datetime.now())
    logging.info(f"Uptime: {uptime_str}")
    return uptime_str

class TestApp(unittest.TestCase):
    """
    Defines the unit tests for the application.
    """
    def test_index(self):
        """
        Tests the index route.
        It checks if the response status code is 200.
        """
        logging.info("Testing index route...")
        with app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
        logging.info("Index route test passed.")

    def test_uptime(self):
        """
        Tests the uptime route.
        It checks if the response status code is 200 and if the response data starts with "System Uptime:".
        """
        logging.info("Testing uptime route...")
        with app.test_client() as client:
            response = client.get('/uptime')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data.decode('utf-8').startswith("System Uptime:"))
        logging.info("Uptime route test passed.")

if __name__ == "__main__":
    import os
    logging.info("Application starting...")
    if os.environ.get("ENV") == "TEST":
        logging.info("Running tests...")
        unittest.main()
    else:
        logging.info("Starting Flask development server...")
        # Use the environment variable defined by Google Cloud Run
        port = int(os.environ.get("PORT", 8080))
        app.run(debug=True, host="0.0.0.0", port=port)