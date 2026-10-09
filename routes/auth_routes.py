from flask import Blueprint, request, jsonify, session, redirect, url_for
from models.user import User
from routes import login_required

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or request.form
    identifier = data.get('email', '').strip()
    password = data.get('password', '').strip()
    remember = data.get('remember', False)

    if not identifier:
        return jsonify({'success': False, 'message': 'Please enter your email or student ID.'}), 400

    if not password:
        return jsonify({'success': False, 'message': 'Please enter your password.'}), 400

    # Search by email or student ID
    user = User.get_by_email(identifier)
    if not user:
        user = User.get_by_student_id(identifier)

    if not user or not User.verify_password(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid email/ID or password.'}), 401

    # Populate session
    session.clear()
    session['user_id'] = user['id']
    session['role'] = user['role']
    session['name'] = user['name']
    session['email'] = user['email']
    session['student_id'] = user.get('student_id')
    session['department'] = user.get('department')
    session['year'] = user.get('year')
    session['semester'] = user.get('semester')

    if remember:
        session.permanent = True

    redirect_url = '/admin/dashboard' if user['role'] == 'admin' else '/student/dashboard'

    return jsonify({
        'success': True,
        'message': f"Welcome back, {user['name']}!",
        'role': user['role'],
        'redirect': redirect_url,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'student_id': user.get('student_id'),
            'department': user.get('department')
        }
    })

@auth_bp.route('/api/logout', methods=['GET', 'POST'])
def api_logout():
    session.clear()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logged out successfully.', 'redirect': '/login'})
    return redirect(url_for('login_page'))

@auth_bp.route('/api/me', methods=['GET'])
@login_required
def api_me():
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'success': False, 'message': 'User session expired.'}), 401

    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'student_id': user.get('student_id'),
            'department': user.get('department'),
            'year': user.get('year'),
            'semester': user.get('semester')
        }
    })
