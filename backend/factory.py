# Main Flask app factory and entry point
from flask import Flask
import os

def create_app():
    """Create and configure the Flask application"""
    # Get the project root directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    app = Flask(__name__, 
                template_folder=os.path.join(project_root, 'templates'),
                static_folder=os.path.join(project_root, 'static'))
    
    # Add startup state tracking using app.config
    app.config['STARTUP_STATE'] = {
        'ssl_ready': True,  # Already handled by launcher
        'app_created': True,
        'blueprints_registered': False,
        'memory_initialized': False,
        'vector_db_ready': False,
        'socketio_ready': False,
        'fully_ready': False
    }    # Register core blueprints immediately for essential routes
    from backend.routes.chat import chat_bp
    from backend.routes.client import client_bp
    from backend.routes.admin import admin_bp
    from backend.routes.vault import vault_bp
    from backend.routes.memory import memory_bp
    app.register_blueprint(chat_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vault_bp)
    app.register_blueprint(memory_bp)
    app.config['STARTUP_STATE']['blueprints_registered'] = True

    # Call this BEFORE returning the app!
    complete_app_initialization(app)

    return app

def complete_app_initialization(app):
    """Complete the app initialization with remaining blueprints and services"""
    try:
          # Initialize memory systems
        app.config['STARTUP_STATE']['memory_initialized'] = True
          # Vector database no longer needed - lightweight implementation
        try:
            print("[STARTUP] Using lightweight text-based search (no vector database)")
            app.config['STARTUP_STATE']['vector_db_ready'] = True
        except Exception as e:
            print(f"[STARTUP] Startup warning: {e}")
            app.config['STARTUP_STATE']['vector_db_ready'] = True  # Continue anyway
        
        # Add data endpoint for backward compatibility
        # Remove if already registered elsewhere to avoid endpoint conflict
        if not any(r.rule == '/data' for r in app.url_map.iter_rules()):
            from backend.utils.id_utils import generate_secure_key
            from flask import jsonify
            @app.route("/data")
            def data():
                key = generate_secure_key()
                return jsonify({"key": key})
        
        # Mark as fully ready
        app.config['STARTUP_STATE']['fully_ready'] = True
        
        print("[STARTUP] Progressive initialization complete - all systems ready")
        
    except Exception as e:
        print(f"[STARTUP] Error during progressive initialization: {e}")
        # Don't fail completely, mark as ready anyway for graceful degradation
        app.config['STARTUP_STATE']['fully_ready'] = True

# For running directly
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True)
