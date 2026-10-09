from flask import Blueprint, request, jsonify, session
from models.feedback import Feedback
from services.feedback_analyzer import FeedbackAnalyzer
from routes import login_required, admin_required

feedback_bp = Blueprint('feedback_bp', __name__)

@feedback_bp.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json() or request.form
    category = data.get('category', '').strip()
    rating_raw = data.get('rating')
    feedback_text = data.get('feedback_text', '').strip()

    # Validations
    if not category:
        return jsonify({'success': False, 'message': 'Please select a valid feedback category.'}), 400

    if not rating_raw:
        return jsonify({'success': False, 'message': 'Please provide a rating between 1 and 5.'}), 400

    try:
        rating = int(rating_raw)
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Rating must be an integer between 1 and 5.'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Rating must be a numeric value between 1 and 5.'}), 400

    if not feedback_text:
        return jsonify({'success': False, 'message': 'Please enter your feedback before submitting.'}), 400

    if len(feedback_text) < 10:
        return jsonify({'success': False, 'message': 'Feedback is too short. Please provide at least 10 characters.'}), 400

    if len(feedback_text) > 2000:
        return jsonify({'success': False, 'message': 'Feedback exceeds maximum permitted length of 2000 characters.'}), 400

    student_id = session.get('user_id')

    # Execute Python AI Analysis
    analysis = FeedbackAnalyzer.analyze_feedback(feedback_text, category, rating)

    sentiment = analysis['sentiment']
    sentiment_score = analysis['sentiment_score']

    # Insert into MySQL database
    try:
        feedback_id = Feedback.create(
            student_id=student_id,
            category=category,
            rating=rating,
            feedback_text=feedback_text,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            status='Analyzed'
        )

        Feedback.save_analysis(
            feedback_id=feedback_id,
            keywords=analysis['keywords'],
            topics=analysis['topics'],
            strengths=analysis['strengths'],
            problems=analysis['problems'],
            recommendations=analysis['recommendations']
        )

        return jsonify({
            'success': True,
            'message': 'Feedback successfully submitted and analyzed by AI.',
            'feedback_id': feedback_id,
            'analysis': {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'keywords': analysis['keywords'],
                'topics': analysis['topics'],
                'strengths': analysis['strengths'],
                'problems': analysis['problems'],
                'recommendations': analysis['recommendations']
            }
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to store feedback in database: {str(e)}'}), 500


@feedback_bp.route('/api/feedback', methods=['GET'])
@login_required
def list_feedback():
    role = session.get('role')
    user_id = session.get('user_id')

    # If student, list only their feedback
    if role == 'student':
        items = Feedback.get_by_student(user_id)
        return jsonify({
            'success': True,
            'items': items,
            'total': len(items)
        })

    # If admin, support full filter and pagination
    search = request.args.get('search')
    category = request.args.get('category')
    sentiment = request.args.get('sentiment')
    rating = request.args.get('rating')
    department = request.args.get('department')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(1, min(100, int(request.args.get('per_page', 10))))
    except ValueError:
        page = 1
        per_page = 10

    result = Feedback.get_all(
        search=search,
        category=category,
        sentiment=sentiment,
        rating=rating,
        department=department,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'data': result
    })


@feedback_bp.route('/api/feedback/<int:feedback_id>', methods=['GET'])
@login_required
def get_feedback_details(feedback_id):
    item = Feedback.get_by_id(feedback_id)
    if not item:
        return jsonify({'success': False, 'message': 'Feedback record not found.'}), 404

    # Authorization: Student can only view their own
    if session.get('role') == 'student' and item['student_id'] != session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized access to this feedback record.'}), 403

    return jsonify({
        'success': True,
        'feedback': item
    })


@feedback_bp.route('/api/feedback/<int:feedback_id>', methods=['DELETE'])
@admin_required
def delete_feedback(feedback_id):
    item = Feedback.get_by_id(feedback_id)
    if not item:
        return jsonify({'success': False, 'message': 'Feedback record not found.'}), 404

    try:
        Feedback.delete(feedback_id)
        return jsonify({'success': True, 'message': 'Feedback record deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to delete feedback: {str(e)}'}), 500
