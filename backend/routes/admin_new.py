# Administrative routes for ICI Chat backend

from flask import Blueprint, render_template, jsonify, request, Response
import markdown
from backend.utils.id_utils import get_env_id
from backend.utils.email_utils import create_email_service
from backend.utils.config import config
import json
import os
import asyncio
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

# In-memory store for lost memory reports
lost_memory_reports = {}  # key: env_id, value: list of dicts (reports)

# Roadmap Data (for /roadmap endpoint)
roadmap_data_store = {
    "project_name": "ICI Chat - Intelligent Contextual Interface",
    "phases": [
        {
            "name": "Phase 1: Core Refactor & Foundation",
            "id": "phase1_core",
            "status": "Completed",
            "target_completion": "Q2 2025",
            "features": [
                {"id": "P1F1", "title": "Decouple Pre-trained LLM", "description": "Remove dependency on external/pre-trained generative LLMs (e.g., distilgpt2) for core chat.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-20", "end_date": "2025-06-10", "impact_areas": ["AI Core", "Performance"]},
                {"id": "P1F2", "title": "Implement Per-env-id 'Learning' KB", "description": "Develop a persistent, per-env-id knowledge base using the vector database. 'Learning' means populating and querying this KB.", "type": "Backend/IT", "status": "In Progress", "start_date": "2025-05-22", "end_date": "2025-06-15", "impact_areas": ["AI Core", "Data Storage", "Privacy"]},
                {"id": "P1F3", "title": "Client-Side env-id Integration", "description": "Ensure client consistently sends env-id for shared context.", "type": "UI/UX", "status": "Planned", "start_date": "2025-06-01", "end_date": "2025-06-10", "impact_areas": ["User Interface", "API"]},
                {"id": "P1F4", "title": "Policy Updates for Shared Learning", "description": "Update policies.html to explain shared learning, env-id context, and data use.", "type": "Policy", "status": "In Progress", "start_date": "2025-05-25", "end_date": "2025-06-05", "impact_areas": ["Legal", "User Trust"]},
                {"id": "P1F5", "title": "Project File Layout Refactor", "description": "Optimize file structure for Cloud Run and developer clarity (src/, __INIT_MYL_APP__/, _DEV_ONLY/).", "type": "Backend/IT", "status": "In Progress", "start_date": "2025-05-24", "end_date": "2025-06-05", "impact_areas": ["DevOps", "Maintainability"]},
                {"id": "P1F6", "title": "Add 'Live Demo' Banner", "description": "Implement a dismissible banner on all pages indicating demo status.", "type": "UI/UX", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["User Interface", "Transparency"]},
                {"id": "P1F7", "title": "Fast Startup Loading Page", "description": "Create immediate loading page during app startup to improve perceived performance and user experience.", "type": "UI/UX", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["User Experience", "Performance", "Startup"]},
                {"id": "P1F8", "title": "Progressive App Initialization", "description": "Refactor startup sequence to serve basic HTML immediately while backend components load asynchronously.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["Performance", "Architecture", "Startup"]},
                {"id": "P1F9", "title": "Enhanced 'Who is [person]?' Memory Search", "description": "Implement cross-memory search functionality to find person mentions across all client records and memory stores.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["AI Core", "Memory System", "Search"]},
                {"id": "P1F10", "title": "Single Entry Point Architecture", "description": "Implement Single Entry Point Rule with only one app.py in root directory and clean modular backend structure.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["Architecture", "Maintainability", "DevOps"]},
                {"id": "P1F11", "title": "Test Suite Organization", "description": "Consolidate all test files into tests/ folder and remove outdated test files for non-existent endpoints.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["Testing", "Maintainability", "DevOps"]}
            ]
        },
        {
            "name": "Phase 2: Optimization & Performance Enhancement",
            "id": "phase2_optimization",
            "status": "In Progress",
            "target_completion": "Q3 2025",
            "features": [
                {"id": "P2F1", "title": "Roadmap Endpoint & Visualization", "description": "This current feature: /roadmap endpoint with JSON and HTML Gantt-like view.", "type": "UI/UX", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["Transparency", "Project Management", "API"]},
                {"id": "P2F2", "title": "Memory System Performance Optimization", "description": "Optimize memory storage and retrieval mechanisms for faster response times and better resource utilization.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-05-27", "end_date": "2025-06-10", "impact_areas": ["Performance", "Memory System", "Scalability"]},
                {"id": "P2F3", "title": "Async Request Processing", "description": "Implement asynchronous processing for chat requests and memory operations to improve concurrent user handling.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-05-27", "end_date": "2025-06-15", "impact_areas": ["Performance", "Concurrency", "User Experience"]},
                {"id": "P2F4", "title": "Response Caching Layer", "description": "Implement intelligent caching for frequently accessed data and repeated query patterns.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-06-01", "end_date": "2025-06-20", "impact_areas": ["Performance", "Response Time", "Resource Efficiency"]},
                {"id": "P2F5", "title": "Enhanced Error Handling & Logging", "description": "Implement comprehensive error handling with structured logging for better debugging and monitoring.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-06-05", "end_date": "2025-06-25", "impact_areas": ["Reliability", "Debugging", "Monitoring"]},
                {"id": "P2F6", "title": "API Rate Limiting & Security", "description": "Implement rate limiting, request validation, and enhanced security measures for all endpoints.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-06-10", "end_date": "2025-07-05", "impact_areas": ["Security", "API Management", "Stability"]},
                {"id": "P2F7", "title": "Database Optimization & Indexing", "description": "Optimize database queries and implement proper indexing for vector and traditional database operations.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-06-15", "end_date": "2025-07-10", "impact_areas": ["Database", "Query Performance", "Scalability"]},
                {"id": "P2F8", "title": "Real-time Performance Monitoring", "description": "Implement performance metrics collection and real-time monitoring dashboard for system health.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-06-20", "end_date": "2025-07-15", "impact_areas": ["Monitoring", "Performance Analysis", "Operations"]},
                {"id": "P2F9", "title": "Advanced Memory Search Algorithms", "description": "Implement more sophisticated search algorithms for better relevance and faster memory retrieval.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-06-25", "end_date": "2025-07-20", "impact_areas": ["AI Core", "Search Performance", "User Experience"]},
                {"id": "P2F10", "title": "Auto-scaling Infrastructure", "description": "Implement auto-scaling capabilities for Cloud Run deployment with load-based scaling strategies.", "type": "DevOps", "status": "Planned", "start_date": "2025-07-01", "end_date": "2025-07-25", "impact_areas": ["Infrastructure", "Scalability", "Cost Optimization"]}
            ]
        },
        {
            "name": "Phase 2.5: Usability & User Experience",
            "id": "phase2_5_usability",
            "status": "Planned",
            "target_completion": "Q3 2025",
            "features": [
                {"id": "P25F1", "title": "Refine KB Response Generation", "description": "Improve templates and logic for responses from the per-env-id KB with better formatting and relevance.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-07-01", "end_date": "2025-07-20", "impact_areas": ["AI Core", "User Experience"]},
                {"id": "P25F2", "title": "Enhanced Chat UI/UX", "description": "Improve chat interface with better message formatting, typing indicators, and user feedback.", "type": "UI/UX", "status": "Planned", "start_date": "2025-07-05", "end_date": "2025-07-25", "impact_areas": ["User Interface", "User Experience"]},
                {"id": "P25F3", "title": "Basic Admin View for KB Content", "description": "Allow admins to view (read-only) content stored per env-id for debugging/oversight.", "type": "UI/UX", "status": "Planned", "start_date": "2025-07-10", "end_date": "2025-07-30", "impact_areas": ["Admin Tools", "Support"]},
                {"id": "P25F4", "title": "User Preferences & Settings", "description": "Implement user-customizable settings for chat behavior, notifications, and interface preferences.", "type": "UI/UX", "status": "Planned", "start_date": "2025-07-15", "end_date": "2025-08-05", "impact_areas": ["User Experience", "Personalization"]},
                {"id": "P25F5", "title": "Mobile-Responsive Design", "description": "Optimize interface for mobile devices with touch-friendly controls and responsive layouts.", "type": "UI/UX", "status": "Planned", "start_date": "2025-07-20", "end_date": "2025-08-10", "impact_areas": ["Mobile Support", "Accessibility", "User Experience"]}
            ]
        },
        {
            "name": "Phase 3: Advanced Features & Intelligence",
            "id": "phase3_advanced",
            "status": "Planned",
            "target_completion": "Q4 2025",
            "features": [
                {"id": "P3F1", "title": "Cross-env-id Search (Permissioned)", "description": "Allow users to search across multiple env-ids they own or are a client of with proper permission validation.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-08-01", "end_date": "2025-08-30", "impact_areas": ["Search", "Permissions", "Data Access"]},
                {"id": "P3F2", "title": "Cross-env-id Search UI", "description": "User interface for initiating and viewing cross-env-id search results with filtering and sorting.", "type": "UI/UX", "status": "Planned", "start_date": "2025-08-15", "end_date": "2025-09-15", "impact_areas": ["User Interface", "Search"]},
                {"id": "P3F3", "title": "Advanced Fact Extraction & Relationship Mapping", "description": "Enhance KB to understand relationships between stored facts within an env-id using graph algorithms.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-08-20", "end_date": "2025-09-30", "impact_areas": ["AI Core", "Knowledge Representation"]},
                {"id": "P3F4", "title": "Intelligent Context Prediction", "description": "Implement ML-based context prediction to anticipate user needs and pre-load relevant information.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-09-01", "end_date": "2025-10-15", "impact_areas": ["AI Core", "Predictive Analytics", "User Experience"]},
                {"id": "P3F5", "title": "Multi-modal Input Support", "description": "Support for image, document, and file uploads with content extraction and analysis.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-09-15", "end_date": "2025-11-01", "impact_areas": ["Input Processing", "Content Analysis", "User Experience"]},
                {"id": "P3F6", "title": "Advanced Analytics Dashboard", "description": "Comprehensive analytics for usage patterns, popular queries, and system performance trends.", "type": "UI/UX", "status": "Planned", "start_date": "2025-10-01", "end_date": "2025-11-15", "impact_areas": ["Analytics", "Business Intelligence", "Admin Tools"]},
                {"id": "P3F7", "title": "API Ecosystem & Integrations", "description": "Develop comprehensive API for third-party integrations and webhook support.", "type": "Backend/IT", "status": "Planned", "start_date": "2025-10-15", "end_date": "2025-12-01", "impact_areas": ["Integration", "API Management", "Ecosystem"]}
            ]
        },
        {
            "name": "Phase 4: Enterprise & Strategic Scaling",
            "id": "phase4_enterprise",
            "status": "Planned",
            "target_completion": "Q1-Q2 2026",
            "features": [
                {"id": "P4F1", "title": "User Roles & Permissions for env-ids", "description": "Detailed role management (admin, member, viewer) for env-ids with granular permissions.", "type": "Security", "status": "Planned", "start_date": "2025-11-01", "end_date": "2025-12-15", "impact_areas": ["Security", "User Management", "Admin Tools"]},
                {"id": "P4F2", "title": "User-Managed KB Contributions", "description": "Allow users to view, edit, delete, and manage their contributions to an env-id's KB.", "type": "UI/UX", "status": "Planned", "start_date": "2025-11-15", "end_date": "2026-01-15", "impact_areas": ["Data Privacy", "User Control", "Policy"]},
                {"id": "P4F3", "title": "Enterprise SSO Integration", "description": "Support for enterprise single sign-on solutions (SAML, OAuth2, LDAP).", "type": "Security", "status": "Planned", "start_date": "2025-12-01", "end_date": "2026-02-01", "impact_areas": ["Enterprise Integration", "Security", "Authentication"]},
                {"id": "P4F4", "title": "Advanced Compliance & Audit Trail", "description": "Comprehensive audit logging, data retention policies, and compliance reporting (GDPR, CCPA).", "type": "Policy", "status": "Planned", "start_date": "2025-12-15", "end_date": "2026-03-01", "impact_areas": ["Compliance", "Audit", "Data Governance"]},
                {"id": "P4F5", "title": "Multi-tenant Architecture", "description": "Complete multi-tenant support with isolated environments and resource allocation.", "type": "Backend/IT", "status": "Planned", "start_date": "2026-01-01", "end_date": "2026-04-01", "impact_areas": ["Architecture", "Scalability", "Enterprise"]},
                {"id": "P4F6", "title": "AI Model Customization", "description": "Allow organizations to fine-tune AI models for their specific domain and use cases.", "type": "AI/ML", "status": "Planned", "start_date": "2026-02-01", "end_date": "2026-05-01", "impact_areas": ["AI Core", "Customization", "Enterprise"]}
            ]
        }
    ]
}

@admin_bp.route("/recovery")
def recovery():
    """Recovery page for administrators"""
    env_id = request.args.get("env_id")
    if not env_id:
        env_id = get_env_id()
    return render_template("recovery.html", env_id=env_id)

@admin_bp.route("/health-dashboard")
def health_dashboard():
    """Health dashboard endpoint (renamed to avoid conflict with API health endpoint)"""
    return render_template("health.html")

@admin_bp.route("/readme")
def readme():
    """Serve README.md as rendered HTML"""
    readme_path = os.path.join(os.path.dirname(__file__), '..', '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            html = markdown.markdown(f.read(), extensions=['fenced_code', 'extra'])
            return render_template('markdown_render.html', content=html, title="README")
    return Response('README.md not found.', mimetype='text/plain')

@admin_bp.route("/policies")
def policies():
    """Policies and terms page"""
    return render_template("policies.html")

@admin_bp.route("/changelog")
def changelog():
    """Changelog page with version history and updates"""
    return render_template("changelog.html")

@admin_bp.route("/lost-memory-report", methods=["POST"])
def lost_memory_report():
    """Submit a lost memory report"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    env_id = data.get("env_id")
    report = data.get("report")
    timestamp = data.get("timestamp")
    client_id = data.get("client_id", "unknown")
    
    if not all([env_id, report]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Store report
    if env_id not in lost_memory_reports:
        lost_memory_reports[env_id] = []
    
    report_entry = {
        "report": report,
        "timestamp": timestamp,
        "client_id": client_id,
        "id": len(lost_memory_reports[env_id]) + 1
    }
    
    lost_memory_reports[env_id].append(report_entry)
    
    # Send email notification if configured
    admin_email = config.admin_email
    email_sent = False
    
    if admin_email and config.is_email_enabled():
        email_service = create_email_service()
        if email_service:
            try:
                # Send memory report notification
                email_service.send_email(
                    to_email=admin_email,
                    subject=f"ICI Chat - Lost Memory Report from {client_id}",
                    body=f"""
A lost memory report has been submitted:

Environment ID: {env_id}
Client ID: {client_id}
Timestamp: {timestamp}

Report Details:
{report}

This report has been logged in the system for review.
                    """
                )
                email_sent = True
                print(f"[EMAIL] Memory report notification sent to {admin_email}")
            except Exception as e:
                print(f"[EMAIL] Failed to send memory report notification: {e}")
    elif admin_email and not config.is_email_enabled():
        print(f"[EMAIL] Email features disabled - Would have sent notification to {admin_email}")
    
    return jsonify({
        "success": True,
        "report_id": report_entry["id"],
        "env_id": env_id,
        "email_sent": email_sent,
        "email_disabled": not config.is_email_enabled()
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
    from backend.utils.memory_utils import get_all_env_boxes
    env_boxes = get_all_env_boxes()
    return jsonify({
        "env_boxes": env_boxes,
        "total_environments": len(env_boxes)
    })

@admin_bp.route("/debug/ip-box")
def debug_ip_box():
    """Debug endpoint to view all IP-box data"""
    from backend.utils.memory_utils import get_all_ip_boxes
    ip_boxes = get_all_ip_boxes()
    return jsonify({
        "ip_boxes": ip_boxes,
        "total_ip_environments": len(ip_boxes)
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
    from backend.utils.memory_utils import clear_all_memory
    from backend.routes.client import client_memory, client_json_table
    clear_all_memory()
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

@admin_bp.route("/roadmap")
def roadmap_view():
    current_roadmap_data = roadmap_data_store.copy()
    current_roadmap_data["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify(current_roadmap_data)
    
    # For HTML view, calculate min/max dates for Gantt scaling
    all_dates = []
    for phase in current_roadmap_data.get("phases", []):
        for feature in phase.get("features", []):
            if feature.get("start_date"):
                all_dates.append(datetime.strptime(feature["start_date"], "%Y-%m-%d"))
            if feature.get("end_date"):
                all_dates.append(datetime.strptime(feature["end_date"], "%Y-%m-%d"))
    
    min_date = min(all_dates) if all_dates else datetime(2025, 1, 1)
    max_date = max(all_dates) if all_dates else datetime(2025, 12, 31)
    
    if max_date <= min_date and all_dates:
        max_date = min_date + timedelta(days=30)
    elif not all_dates:
        min_date = datetime(datetime.now().year, 1, 1)
        max_date = datetime(datetime.now().year, 12, 31)
    
    return render_template(
        "roadmap.html",
        roadmap=current_roadmap_data,
        min_date=min_date,
        max_date=max_date,
        timedelta=timedelta,
        datetime=datetime
    )

@admin_bp.route("/test-email", methods=["POST"])
def test_email():
    """Test email functionality - Admin only endpoint"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    test_email = data.get("email", config.admin_email)
    if not test_email:
        return jsonify({"error": "No email address provided"}), 400
    
    # Check if email features are enabled
    if not config.is_email_enabled():
        return jsonify({
            "success": False,
            "error": "Email features are currently disabled",
            "details": "No email provider is configured",
            "email": test_email,
            "feature_disabled": True
        }), 400
    
    email_service = create_email_service()
    if not email_service:
        return jsonify({
            "error": "Email service not configured",
            "details": "No email provider configuration found"
        }), 400
    
    try:
        # Send test email
        success = email_service.send_email(
            to_email=test_email,
            subject="ICI Chat Email Test",
            body=f"""
This is a test email from ICI Chat.

Environment: {get_env_id()}
Timestamp: {datetime.utcnow().isoformat()}
Email Provider: {config.email_provider}

If you received this email, the email integration is working correctly!
            """
        )
        
        return jsonify({
            "success": success,
            "message": "Test email sent" if success else "Email failed",
            "email": test_email,
            "provider": config.email_provider
        })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Email test failed: {str(e)}",
            "email": test_email
        }), 500

@admin_bp.route("/email-status")
def email_status():
    """Check email gateway configuration status"""
    email_config = config.get_configuration_report()
    
    return jsonify({
        "configured": config.is_email_enabled(),
        "provider": config.email_provider,
        "email_enabled": config.is_email_enabled(),
        "admin_email_set": bool(config.admin_email),
        "admin_email": config.admin_email or 'Not set',
        "configuration_status": email_config['configuration_status'],
        "secrets_source": email_config['secrets_source'],
        "status_message": f"Using {config.email_provider}" if config.email_provider else "No email provider configured"
    })
