from flask import Blueprint, request, jsonify, Response
from services.report_service import ReportService
from routes import admin_required

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/api/reports', methods=['GET'])
@admin_required
def get_report():
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'department': request.args.get('department'),
        'category': request.args.get('category'),
        'sentiment': request.args.get('sentiment'),
        'rating': request.args.get('rating')
    }

    report_data = ReportService.generate_report_data(filters)
    return jsonify({
        'success': True,
        'data': report_data
    })

@report_bp.route('/api/reports/export', methods=['GET'])
@admin_required
def export_csv():
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'department': request.args.get('department'),
        'category': request.args.get('category'),
        'sentiment': request.args.get('sentiment'),
        'rating': request.args.get('rating')
    }

    csv_buffer = ReportService.export_csv_stream(filters)
    return Response(
        csv_buffer.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=AI_Student_Feedback_Report.csv',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )
