# Routes package
from functools import wraps
from flask import session, jsonify, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required. Please login.'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Unauthorized. Admin privileges required.'}), 403
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Unauthorized. Student privileges required.'}), 403
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function
