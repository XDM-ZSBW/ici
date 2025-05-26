# Main Flask app factory and entry point
from flask import Flask
from flask_socketio import SocketIO

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    # Import and register blueprints here (to be added)
    return app, socketio

# For running directly
if __name__ == "__main__":
    from backend import app as backend_app
    app, socketio = backend_app.create_app()
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
