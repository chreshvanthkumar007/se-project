from flask import Blueprint, jsonify
from services.report_service import ReportService
from models.feedback import Feedback
from routes import admin_required

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/api/dashboard', methods=['GET'])
@admin_required
def get_dashboard_kpis():
    stats = ReportService.get_dashboard_summary()
    return jsonify({
        'success': True,
        'stats': stats
    })

@admin_bp.route('/api/analytics', methods=['GET'])
@admin_required
def get_analytics_charts():
    charts = ReportService.get_chart_analytics()
    return jsonify({
        'success': True,
        'charts': charts
    })

@admin_bp.route('/api/categories', methods=['GET'])
def get_categories_list():
    cats = Feedback.get_categories()
    return jsonify({
        'success': True,
        'categories': cats
    })

@admin_bp.route('/api/departments', methods=['GET'])
def get_departments_list():
    depts = Feedback.get_departments()
    return jsonify({
        'success': True,
        'departments': depts
    })
