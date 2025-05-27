# Main Flask app factory and entry point
from flask import Flask
from flask_socketio import SocketIO
import os

def create_app():
    """Create and configure the Flask application"""
    # Get the project root directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    app = Flask(__name__, 
                template_folder=os.path.join(project_root, 'templates'),
                static_folder=os.path.join(project_root, 'static'))
    
    socketio = SocketIO(app, cors_allowed_origins="*")    # Import and register blueprints
    from backend.routes.chat import chat_bp
    from backend.routes.client import client_bp
    from backend.routes.admin import admin_bp
    from backend.routes.vault import vault_bp
    from backend.routes.learn import learn_bp
    from backend.routes.memory import memory_bp
    
    app.register_blueprint(chat_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vault_bp)
    app.register_blueprint(learn_bp)
    app.register_blueprint(memory_bp)
    
    # Add data endpoint for backward compatibility
    from backend.utils.id_utils import generate_secure_key
    from flask import jsonify
    
    @app.route("/data")
    def data():
        key = generate_secure_key()
        return jsonify({"key": key})
    
    return app, socketio

# For running directly
if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
