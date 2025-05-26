# Administrative routes for ICI Chat backend

from flask import Blueprint, render_template, jsonify, request, Response
from backend.utils.id_utils import get_env_id
import json
import os

admin_bp = Blueprint('admin', __name__)

# In-memory store for lost memory reports
lost_memory_reports = {}  # key: env_id, value: list of dicts (reports)

@admin_bp.route("/recovery")
def recovery():
    """Recovery page for administrators"""
    env_id = request.args.get("env_id")
    if not env_id:
        env_id = get_env_id()
    return render_template("recovery.html", env_id=env_id)

@admin_bp.route("/health")
def health():
    """Health check endpoint"""
    return render_template("health.html")

@admin_bp.route("/readme")
def readme():
    """Serve README.md as plain text"""
    readme_path = os.path.join(os.path.dirname(__file__), '..', '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    return Response('README.md not found.', mimetype='text/plain')

@admin_bp.route("/policies")
def policies():
    """Policies and terms page"""
    return render_template("policies.html")

@admin_bp.route("/lost-memory-report", methods=["POST"])
def lost_memory_report():
    """Submit a lost memory report"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    env_id = data.get("env_id")
    report = data.get("report")
    timestamp = data.get("timestamp")
    
    if not all([env_id, report]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Store report
    if env_id not in lost_memory_reports:
        lost_memory_reports[env_id] = []
    
    report_entry = {
        "report": report,
        "timestamp": timestamp,
        "id": len(lost_memory_reports[env_id]) + 1
    }
    
    lost_memory_reports[env_id].append(report_entry)
    
    return jsonify({
        "success": True,
        "report_id": report_entry["id"],
        "env_id": env_id
    })

@admin_bp.route("/lost-memory-reports")
def list_lost_memory_reports():
    """List all lost memory reports"""
    env_id = request.args.get("env_id")
    
    if env_id:
        reports = lost_memory_reports.get(env_id, [])
        return jsonify({
            "env_id": env_id,
            "reports": reports,
            "total": len(reports)
        })
    else:
        # Return all reports across all environments
        all_reports = {}
        total_count = 0
        for env_id, reports in lost_memory_reports.items():
            all_reports[env_id] = reports
            total_count += len(reports)
        
        return jsonify({
            "reports_by_env": all_reports,
            "total_reports": total_count
        })

@admin_bp.route("/system-info")
def system_info():
    """Get system information for debugging"""
    import sys
    import platform
    
    return jsonify({
        "python_version": sys.version,
        "platform": platform.platform(),
        "python_implementation": platform.python_implementation(),
        "env_id": get_env_id(),
        "executable": sys.executable
    })

@admin_bp.route("/debug/env-box")
def debug_env_box():
    """Debug endpoint to view all env-box data"""
    from backend.routes.chat import shared_env_box
    return jsonify({
        "env_boxes": shared_env_box,
        "total_environments": len(shared_env_box)
    })

@admin_bp.route("/debug/ip-box")
def debug_ip_box():
    """Debug endpoint to view all IP-box data"""
    from backend.routes.chat import shared_client_box
    
    # Convert tuple keys to strings for JSON serialization
    serializable_data = {}
    for (env_id, public_ip), value in shared_client_box.items():
        key = f"{env_id}:{public_ip}"
        serializable_data[key] = value
    
    return jsonify({
        "ip_boxes": serializable_data,
        "total_ip_environments": len(shared_client_box)
    })

@admin_bp.route("/debug/clients")
def debug_clients():
    """Debug endpoint to view all client data"""
    from backend.routes.client import client_memory, client_json_table
    
    return jsonify({
        "client_memory": client_memory,
        "client_table": client_json_table,
        "total_clients": len(client_json_table)
    })

@admin_bp.route("/debug/clear-all", methods=["POST"])
def debug_clear_all():
    """Debug endpoint to clear all data (use with caution)"""
    from backend.routes.chat import shared_env_box, shared_client_box
    from backend.routes.client import client_memory, client_json_table
    
    # Clear all data stores
    shared_env_box.clear()
    shared_client_box.clear()
    client_memory.clear()
    client_json_table.clear()
    lost_memory_reports.clear()
    
    return jsonify({
        "success": True,
        "message": "All data cleared",
        "timestamp": request.get_json().get("timestamp") if request.is_json else None
    })

@admin_bp.route("/admin")
def admin_dashboard():
    """Admin dashboard page"""
    env_id = get_env_id()
    return render_template("admin.html", env_id=env_id)
