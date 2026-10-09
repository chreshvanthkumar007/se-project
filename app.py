import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from config import Config
from database.db import db
from routes.auth_routes import auth_bp
from routes.feedback_routes import feedback_bp
from routes.admin_routes import admin_bp
from routes.report_routes import report_bp
from routes import student_required, admin_required

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(report_bp)

    # Ensure database is ready on startup
    try:
        db.init_database(force_reset=False)
    except Exception as e:
        print(f"[App Startup Warning] Database init check: {e}")

    # -------------------------------------------------------------
    # Page Routes
    # -------------------------------------------------------------
    @app.route('/')
    def root():
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin_dashboard_page'))
            return redirect(url_for('student_dashboard_page'))
        return redirect(url_for('login_page'))

    @app.route('/login')
    def login_page():
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin_dashboard_page'))
            return redirect(url_for('student_dashboard_page'))
        return render_template('login.html')

    # Student Pages
    @app.route('/student/dashboard')
    @student_required
    def student_dashboard_page():
        return render_template('student_dashboard.html', user=session)

    @app.route('/student/feedback')
    @student_required
    def feedback_page():
        return render_template('feedback.html', user=session)

    @app.route('/student/my-feedback')
    @student_required
    def my_feedback_page():
        return render_template('my_feedback.html', user=session)

    # Admin Pages
    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard_page():
        return render_template('admin_dashboard.html', user=session)

    @app.route('/admin/feedback')
    @admin_required
    def admin_feedback_page():
        return render_template('feedback_management.html', user=session)

    @app.route('/admin/reports')
    @admin_required
    def admin_reports_page():
        return render_template('reports.html', user=session)

    # -------------------------------------------------------------
    # Error Handlers
    # -------------------------------------------------------------
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'API endpoint not found.'}), 404
        return render_template('login.html', error="Page not found. Redirected to login."), 404

    @app.errorhandler(500)
    def handle_500(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Internal server error occurred.'}), 500
        return render_template('login.html', error="An unexpected server error occurred."), 500

    return app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  AI Student Feedback Analyzer Web Application")
    print("  Local Server: http://127.0.0.1:5000")
    print("  Administrator: admin@college.edu | admin123")
    print("  Student: alex.turner@college.edu | student123")
    print("=" * 60)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1')
    app.run(host=host, port=port, debug=False if os.environ.get('PORT') else True)
