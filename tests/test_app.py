import unittest
from app import create_app
from services.sentiment_service import SentimentService
from services.feedback_analyzer import FeedbackAnalyzer

class AcademicFeedbackTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------
    # 1. Authentication Tests
    # -------------------------------------------------------------
    def test_01_admin_login_success(self):
        res = self.client.post('/api/login', json={
            'email': 'admin@college.edu',
            'password': 'admin123'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['role'], 'admin')
        self.assertEqual(data['redirect'], '/admin/dashboard')

    def test_02_student_login_success(self):
        res = self.client.post('/api/login', json={
            'email': 'alex.turner@college.edu',
            'password': 'student123'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['role'], 'student')
        self.assertEqual(data['redirect'], '/student/dashboard')

    def test_03_invalid_login_password(self):
        res = self.client.post('/api/login', json={
            'email': 'admin@college.edu',
            'password': 'wrongpassword'
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid', data['message'])

    def test_04_empty_login_credentials(self):
        res = self.client.post('/api/login', json={'email': '', 'password': ''})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_05_unauthorized_admin_access(self):
        # Fresh unauthenticated client
        unauth_client = self.app.test_client()
        res = unauth_client.get('/api/dashboard')
        self.assertEqual(res.status_code, 403)

    # -------------------------------------------------------------
    # 2. AI & NLP Analysis Tests
    # -------------------------------------------------------------
    def test_06_sentiment_positive_analysis(self):
        text = "The faculty explains complex algorithms with great clarity and provides practical code examples."
        res = SentimentService.analyze(text)
        self.assertEqual(res['sentiment'], 'Positive')
        self.assertGreater(res['sentiment_score'], 0.2)

    def test_07_sentiment_negative_analysis(self):
        text = "The air conditioning in lecture hall is broken and the projector blinks constantly during seminars."
        res = SentimentService.analyze(text)
        self.assertEqual(res['sentiment'], 'Negative')
        self.assertLess(res['sentiment_score'], -0.2)

    def test_08_sentiment_mixed_analysis(self):
        text = "The faculty explains concepts clearly, but the laboratory equipment is outdated and needs improvement."
        res = FeedbackAnalyzer.analyze_feedback(text, category='Laboratory', rating=3)
        self.assertEqual(res['sentiment'], 'Mixed')
        self.assertTrue(len(res['strengths']) > 0)
        self.assertTrue(len(res['problems']) > 0)
        self.assertTrue(len(res['recommendations']) > 0)

    # -------------------------------------------------------------
    # 3. Feedback Workflow & Validation Tests
    # -------------------------------------------------------------
    def test_09_feedback_submission_short_text(self):
        student_client = self.app.test_client()
        student_client.post('/api/login', json={'email': 'alex.turner@college.edu', 'password': 'student123'})

        res = student_client.post('/api/feedback', json={
            'category': 'Faculty',
            'rating': 5,
            'feedback_text': 'Short'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('too short', res.get_json()['message'])

    def test_10_feedback_submission_invalid_rating(self):
        student_client = self.app.test_client()
        student_client.post('/api/login', json={'email': 'alex.turner@college.edu', 'password': 'student123'})

        res = student_client.post('/api/feedback', json={
            'category': 'Faculty',
            'rating': 9,
            'feedback_text': 'Excellent explanations and great lectures in class.'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('Rating must be', res.get_json()['message'])

    def test_11_feedback_end_to_end_submission_and_retrieval(self):
        student_client = self.app.test_client()
        student_client.post('/api/login', json={'email': 'alex.turner@college.edu', 'password': 'student123'})

        # Submit
        sub_res = student_client.post('/api/feedback', json={
            'category': 'Teaching',
            'rating': 5,
            'feedback_text': 'Exceptional pedagogy and very engaging case studies throughout the semester.'
        })
        self.assertEqual(sub_res.status_code, 201)
        sub_data = sub_res.get_json()
        fb_id = sub_data['feedback_id']

        # Retrieve
        get_res = student_client.get(f'/api/feedback/{fb_id}')
        self.assertEqual(get_res.status_code, 200)
        fb_item = get_res.get_json()['feedback']
        self.assertEqual(fb_item['category'], 'Teaching')
        self.assertEqual(fb_item['sentiment'], 'Positive')

    # -------------------------------------------------------------
    # 4. Reports & CSV Export Tests
    # -------------------------------------------------------------
    def test_12_admin_report_and_csv_export(self):
        admin_client = self.app.test_client()
        admin_client.post('/api/login', json={'email': 'admin@college.edu', 'password': 'admin123'})

        # Report JSON
        rep_res = admin_client.get('/api/reports?category=all&sentiment=all')
        self.assertEqual(rep_res.status_code, 200)
        rep_data = rep_res.get_json()
        self.assertTrue(rep_data['success'])
        self.assertGreater(rep_data['data']['summary']['total_responses'], 0)

        # CSV Export
        csv_res = admin_client.get('/api/reports/export')
        self.assertEqual(csv_res.status_code, 200)
        self.assertEqual(csv_res.headers.get('Content-Type'), 'text/csv; charset=utf-8')
        content = csv_res.data.decode('utf-8')
        self.assertIn('Feedback ID,Roll Number,Student Name', content)

if __name__ == '__main__':
    unittest.main()
