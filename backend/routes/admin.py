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
                {"id": "P1F11", "title": "Test Suite Organization", "description": "Consolidate all test files into tests/ folder and remove outdated test files for non-existent endpoints.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-26", "end_date": "2025-05-26", "impact_areas": ["Testing", "Maintainability", "DevOps"]},
                {"id": "P1F12", "title": "Hybrid Secrets Management", "description": "Implement transparent secrets management with Google Secret Manager for production and environment variables for development.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-27", "end_date": "2025-05-27", "impact_areas": ["Security", "DevOps", "Configuration"]},
                {"id": "P1F13", "title": "Real-Time Health Monitoring System", "description": "Implement comprehensive health monitoring with Server-Sent Events, live status updates, and real-time system diagnostics.", "type": "Backend/IT", "status": "Completed", "start_date": "2025-05-27", "end_date": "2025-05-27", "impact_areas": ["Monitoring", "DevOps", "User Experience", "Reliability"]}
            ]
        }
    ]
}

@admin_bp.route('/admin')
def admin_dashboard():
    """Admin dashboard with configuration status and health metrics"""
    try:
        env_id = get_env_id()
        
        # Get configuration report from our new config system
        config_report = config.get_configuration_report()
        
        # Get lost memory reports for this env_id
        reports = lost_memory_reports.get(env_id, [])
        
        # Enhanced admin data with new secrets management info
        admin_data = {
            'env_id': env_id,
            'configuration': config_report,
            'lost_memory_reports': reports,
            'email_status': {
                'enabled': config.is_email_enabled(),
                'provider': config.email_provider,
                'configured': config.config_status['email_configured']
            },
            'secrets_health': config_report.get('secrets_health', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        return render_template('admin.html', admin_data=admin_data)
    except Exception as e:
        return jsonify({'error': f'Admin dashboard error: {str(e)}'}), 500

@admin_bp.route('/admin/config')
def admin_config():
    """API endpoint for configuration status"""
    try:
        config_report = config.get_configuration_report()
        validation = config.validate_configuration()
        
        return jsonify({
            'configuration': config_report,
            'validation': validation,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Configuration check error: {str(e)}'}), 500

@admin_bp.route('/admin/secrets-health')
def secrets_health():
    """Check secrets management health"""
    try:
        from backend.utils.secrets_manager import secrets_manager
        
        health_report = {
            'secrets_source': 'Secret Manager' if secrets_manager.project_id else 'Environment Variables',
            'google_cloud_project': secrets_manager.project_id,
            'available_secrets': len(secrets_manager.list_available_secrets()),
            'configuration_health': secrets_manager.check_configuration_health(),
            'email_configured': config.is_email_enabled(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(health_report)
    except Exception as e:
        return jsonify({'error': f'Secrets health check error: {str(e)}'}), 500

@admin_bp.route('/admin/test-email', methods=['POST'])
def test_email():
    """Test email functionality with new email system"""
    try:
        if not config.is_email_enabled():
            return jsonify({
                'success': False,
                'error': 'Email not configured',
                'recommendation': 'Configure an email provider in your environment variables'
            }), 400
        
        # Create email service using new system
        email_service = create_email_service()
        if not email_service:
            return jsonify({
                'success': False,
                'error': 'Failed to create email service',
                'provider': config.email_provider
            }), 500
        
        # Get test parameters
        data = request.get_json() or {}
        to_email = data.get('to_email', config.admin_email)
        
        if not to_email:
            return jsonify({
                'success': False,
                'error': 'No recipient email address provided'
            }), 400
          # Send test email
        result = email_service.send_email(
            to_email=to_email,
            subject='ICI Chat - Email Test',
            body='This is a test email from your ICI Chat system. Email functionality is working correctly!',
            html_body='<p>This is a test email from your <strong>ICI Chat</strong> system.</p><p>Email functionality is working correctly!</p>'
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Test email sent successfully via {config.email_provider}',
                'provider': config.email_provider,
                'to_email': to_email
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown email error'),
                'provider': config.email_provider
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Email test error: {str(e)}'
        }), 500

@admin_bp.route('/lost-memory', methods=['POST'])
def report_lost_memory():
    """Report lost memory with optional email notification"""
    try:
        data = request.get_json()
        env_id = get_env_id()
        
        # Validate required fields
        required_fields = ['env_id', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create report
        report = {
            'id': f"lm_{env_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'env_id': data['env_id'],
            'description': data['description'],
            'user_email': data.get('user_email'),
            'timestamp': datetime.now().isoformat(),
            'status': 'reported'
        }
        
        # Store report
        if env_id not in lost_memory_reports:
            lost_memory_reports[env_id] = []
        lost_memory_reports[env_id].append(report)
        
        # Send email notification if email is configured
        email_sent = False
        if config.is_email_enabled() and config.admin_email:
            try:
                email_service = create_email_service()
                if email_service:
                    subject = f"ICI Chat - Lost Memory Report: {report['id']}"
                    body = f"""
Lost Memory Report Submitted

Report ID: {report['id']}
Environment ID: {report['env_id']}
Description: {report['description']}
User Email: {report.get('user_email', 'Not provided')}
Timestamp: {report['timestamp']}

Please review and address this report in the admin dashboard.
                    """
                    
                    result = email_service.send_email(
                        to_email=config.admin_email,
                        subject=subject,
                        body=body
                    )
                    email_sent = result['success']
            except Exception as e:
                print(f"Email notification error: {e}")
        
        return jsonify({
            'success': True,
            'report_id': report['id'],
            'email_sent': email_sent,
            'message': 'Lost memory report submitted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to report lost memory: {str(e)}'}), 500

@admin_bp.route('/health')
def health_check():
    """Comprehensive health check with new secrets management status"""
    try:
        env_id = get_env_id()
        config_report = config.get_configuration_report()
        validation = config.validate_configuration()
        
        health_data = {
            'status': 'healthy' if validation['valid'] else 'warning',
            'timestamp': datetime.now().isoformat(),
            'env_id': env_id,
            'configuration': config_report,
            'validation': validation,
            'services': {
                'email': {
                    'enabled': config.is_email_enabled(),
                    'provider': config.email_provider,
                    'status': 'configured' if config.config_status['email_configured'] else 'not_configured'
                },
                'database': {
                    'status': 'configured' if config.config_status['database_configured'] else 'not_configured'
                },
                'auth': {
                    'status': 'configured' if config.config_status['auth_configured'] else 'not_configured'
                },
                'secrets': {
                    'source': 'Secret Manager' if config.secrets.project_id else 'Environment Variables',
                    'health': config_report.get('secrets_health', {})
                }
            }        }
        
        return render_template('health.html', health_data=health_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@admin_bp.route('/events')
def events():
    """Server-Sent Events endpoint for health check page"""
    import time
    import random
    import string
    
    def generate_events():
        """Generate server-sent events with health status data"""
        while True:
            # Generate a random string for the health check
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Create event data in the format expected by health.html
            event_data = {
                'random_string': random_string,
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy'
            }
            
            # Format as Server-Sent Event
            yield f"data: {json.dumps(event_data)}\n\n"
            
            # Wait before sending next event
            time.sleep(5)
    
    return Response(
        generate_events(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@admin_bp.route("/roadmap")
def roadmap_view():
    """Roadmap view with HTML rendering and JSON API support"""
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

@admin_bp.route("/changelog")
def changelog():
    """Changelog page with version history and updates"""
    return render_template("changelog.html")

@admin_bp.route("/policies")
def policies():
    """Policies and terms page"""
    return render_template("policies.html")