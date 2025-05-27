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
    
    # SocketIO will be initialized later during progressive startup
    socketio = None
    
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
    from backend.routes.learn import learn_bp
    app.register_blueprint(chat_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(learn_bp)
    app.config['STARTUP_STATE']['blueprints_registered'] = True
      # Home page route - serves immediately and always shows home content
    @app.route("/")
    def home_page():
        """Serve home page with ICI information and QR code functionality"""
        from flask import render_template
        if app.config['STARTUP_STATE'].get('fully_ready', False):
            # If app is fully ready, show the main home page
            return render_template("index.html")
        else:
            # Show loading page during startup
            return render_template("loading.html")
    
    # Progressive initialization routes
    @app.route("/startup-status")
    def startup_status():
        """Get current startup status for loading page"""
        from flask import jsonify
        return jsonify(app.config['STARTUP_STATE'])
    
    # Immediate health check for early availability
    @app.route("/health")
    def health_check():
        """Basic health check that works during startup"""
        from flask import jsonify
        status = "starting" if not app.config['STARTUP_STATE'].get('fully_ready', False) else "ready"
        return jsonify({
            "status": status,
            "startup_state": app.config['STARTUP_STATE'],
            "message": "Server is starting up..." if status == "starting" else "Server ready"
        })
    
    # Initialize SocketIO early for basic functionality
    socketio = SocketIO(app, cors_allowed_origins="*")
    app.config['STARTUP_STATE']['socketio_ready'] = True
    
    return app, socketio

def complete_app_initialization(app):
    """Complete the app initialization with remaining blueprints and services"""
    try:
        # Import and register remaining blueprints
        from backend.routes.vault import vault_bp
        from backend.routes.memory import memory_bp
        
        app.register_blueprint(vault_bp)
        app.register_blueprint(memory_bp)
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
    app, socketio = create_app()
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
