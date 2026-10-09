import csv
import io
from database.db import db
from models.user import User

class ReportService:
    """
    Analytics, Dashboard KPI calculation, Chart data generation, and Report export service.
    """

    @staticmethod
    def get_dashboard_summary():
        total_students = User.count_students()
        
        # Feedback counts and rating
        summary_query = """
            SELECT 
                COUNT(*) as total_feedback,
                COALESCE(AVG(rating), 0) as avg_rating,
                SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END) as negative_count,
                SUM(CASE WHEN sentiment = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
                SUM(CASE WHEN sentiment = 'Mixed' THEN 1 ELSE 0 END) as mixed_count,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_count
            FROM feedback
        """
        summary = db.execute_query(summary_query, fetchone=True) or {}
        
        total_fb = summary.get('total_feedback', 0)
        avg_rating = round(float(summary.get('avg_rating', 0)), 1)
        pos = summary.get('positive_count', 0) or 0
        neg = summary.get('negative_count', 0) or 0
        neu = summary.get('neutral_count', 0) or 0
        mix = summary.get('mixed_count', 0) or 0
        pending = summary.get('pending_count', 0) or 0

        pos_pct = round((pos / total_fb * 100), 1) if total_fb > 0 else 0
        neg_pct = round((neg / total_fb * 100), 1) if total_fb > 0 else 0
        neu_pct = round((neu / total_fb * 100), 1) if total_fb > 0 else 0
        mix_pct = round((mix / total_fb * 100), 1) if total_fb > 0 else 0

        # Most reported problematic category (lowest average rating or highest negative count)
        prob_query = """
            SELECT category, COUNT(*) as neg_count, AVG(rating) as avg_rate
            FROM feedback
            WHERE sentiment IN ('Negative', 'Mixed') OR rating <= 2
            GROUP BY category
            ORDER BY neg_count DESC, avg_rate ASC
            LIMIT 1
        """
        prob_row = db.execute_query(prob_query, fetchone=True)
        most_reported_issue = prob_row['category'] if prob_row else "None"

        # Most praised area
        praise_query = """
            SELECT category, COUNT(*) as pos_count, AVG(rating) as avg_rate
            FROM feedback
            WHERE sentiment = 'Positive' OR rating >= 4
            GROUP BY category
            ORDER BY pos_count DESC, avg_rate DESC
            LIMIT 1
        """
        praise_row = db.execute_query(praise_query, fetchone=True)
        most_praised_area = praise_row['category'] if praise_row else "None"

        return {
            'total_students': total_students,
            'total_feedback': total_fb,
            'avg_rating': avg_rating,
            'positive_pct': pos_pct,
            'negative_pct': neg_pct,
            'neutral_pct': neu_pct,
            'mixed_pct': mix_pct,
            'positive_count': pos,
            'negative_count': neg,
            'neutral_count': neu,
            'mixed_count': mix,
            'pending_count': pending,
            'most_reported_issue': most_reported_issue,
            'most_praised_area': most_praised_area
        }

    @staticmethod
    def get_chart_analytics():
        # 1. Sentiment Distribution
        sent_query = """
            SELECT sentiment, COUNT(*) as count 
            FROM feedback 
            GROUP BY sentiment
        """
        sent_rows = db.execute_query(sent_query)
        sentiment_dist = {'Positive': 0, 'Negative': 0, 'Neutral': 0, 'Mixed': 0}
        for r in sent_rows:
            sentiment_dist[r['sentiment']] = r['count']

        # 2. Feedback by Category
        cat_query = """
            SELECT category, COUNT(*) as count 
            FROM feedback 
            GROUP BY category 
            ORDER BY count DESC
        """
        cat_rows = db.execute_query(cat_query)
        categories = [r['category'] for r in cat_rows]
        cat_counts = [r['count'] for r in cat_rows]

        # 3. Average Rating by Category
        rating_query = """
            SELECT category, ROUND(AVG(rating), 2) as avg_rating 
            FROM feedback 
            GROUP BY category 
            ORDER BY avg_rating DESC
        """
        rating_rows = db.execute_query(rating_query)
        rating_categories = [r['category'] for r in rating_rows]
        rating_values = [float(r['avg_rating']) for r in rating_rows]

        # 4. Feedback Trend (Submissions per day over recent period)
        trend_query = """
            SELECT DATE(created_at) as sub_date, COUNT(*) as count, ROUND(AVG(rating), 2) as avg_rate
            FROM feedback
            GROUP BY DATE(created_at)
            ORDER BY sub_date ASC
            LIMIT 15
        """
        trend_rows = db.execute_query(trend_query)
        trend_dates = [str(r['sub_date']) for r in trend_rows]
        trend_counts = [r['count'] for r in trend_rows]
        trend_ratings = [float(r['avg_rate']) for r in trend_rows]

        return {
            'sentiment': {
                'labels': ['Positive', 'Negative', 'Neutral', 'Mixed'],
                'data': [sentiment_dist['Positive'], sentiment_dist['Negative'], sentiment_dist['Neutral'], sentiment_dist['Mixed']]
            },
            'categories': {
                'labels': categories,
                'data': cat_counts
            },
            'ratings': {
                'labels': rating_categories,
                'data': rating_values
            },
            'trends': {
                'labels': trend_dates,
                'counts': trend_counts,
                'ratings': trend_ratings
            }
        }

    @staticmethod
    def generate_report_data(filters=None):
        filters = filters or {}
        where_clauses = ["1=1"]
        params = []

        if filters.get('start_date'):
            where_clauses.append("DATE(f.created_at) >= %s")
            params.append(filters['start_date'])

        if filters.get('end_date'):
            where_clauses.append("DATE(f.created_at) <= %s")
            params.append(filters['end_date'])

        if filters.get('department') and filters['department'].lower() != 'all':
            where_clauses.append("u.department = %s")
            params.append(filters['department'])

        if filters.get('category') and filters['category'].lower() != 'all':
            where_clauses.append("f.category = %s")
            params.append(filters['category'])

        if filters.get('sentiment') and filters['sentiment'].lower() != 'all':
            where_clauses.append("f.sentiment = %s")
            params.append(filters['sentiment'])

        if filters.get('rating') and filters['rating'].lower() != 'all':
            where_clauses.append("f.rating = %s")
            params.append(int(filters['rating']))

        where_sql = " AND ".join(where_clauses)

        # Aggregate metrics
        agg_sql = f"""
            SELECT 
                COUNT(*) as total_responses,
                COALESCE(AVG(f.rating), 0) as avg_rating,
                SUM(CASE WHEN f.sentiment = 'Positive' THEN 1 ELSE 0 END) as pos_count,
                SUM(CASE WHEN f.sentiment = 'Negative' THEN 1 ELSE 0 END) as neg_count,
                SUM(CASE WHEN f.sentiment = 'Neutral' THEN 1 ELSE 0 END) as neu_count,
                SUM(CASE WHEN f.sentiment = 'Mixed' THEN 1 ELSE 0 END) as mix_count
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            WHERE {where_sql}
        """
        agg = db.execute_query(agg_sql, tuple(params), fetchone=True) or {}
        total = agg.get('total_responses', 0)
        avg_rate = round(float(agg.get('avg_rating', 0)), 2)
        pos = agg.get('pos_count', 0) or 0
        neg = agg.get('neg_count', 0) or 0
        neu = agg.get('neu_count', 0) or 0
        mix = agg.get('mix_count', 0) or 0

        pos_pct = round((pos / total * 100), 1) if total > 0 else 0
        neg_pct = round((neg / total * 100), 1) if total > 0 else 0
        neu_pct = round((neu / total * 100), 1) if total > 0 else 0
        mix_pct = round((mix / total * 100), 1) if total > 0 else 0

        # Most problematic category in filtered set
        prob_sql = f"""
            SELECT f.category, COUNT(*) as cnt
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            WHERE {where_sql} AND (f.sentiment IN ('Negative', 'Mixed') OR f.rating <= 2)
            GROUP BY f.category
            ORDER BY cnt DESC
            LIMIT 1
        """
        prob_row = db.execute_query(prob_sql, tuple(params), fetchone=True)
        most_problematic = prob_row['category'] if prob_row else "None"

        # Most praised area in filtered set
        praise_sql = f"""
            SELECT f.category, COUNT(*) as cnt
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            WHERE {where_sql} AND (f.sentiment = 'Positive' OR f.rating >= 4)
            GROUP BY f.category
            ORDER BY cnt DESC
            LIMIT 1
        """
        praise_row = db.execute_query(praise_sql, tuple(params), fetchone=True)
        most_praised = praise_row['category'] if praise_row else "None"

        # Fetch records
        records_sql = f"""
            SELECT 
                f.id, f.category, f.rating, f.feedback_text, f.sentiment,
                f.sentiment_score, f.status, f.created_at,
                u.name as student_name, u.student_id as student_roll_no, u.department
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            WHERE {where_sql}
            ORDER BY f.created_at DESC
        """
        records = db.execute_query(records_sql, tuple(params))

        return {
            'summary': {
                'total_responses': total,
                'avg_rating': avg_rate,
                'positive_pct': pos_pct,
                'negative_pct': neg_pct,
                'neutral_pct': neu_pct,
                'mixed_pct': mix_pct,
                'positive_count': pos,
                'negative_count': neg,
                'neutral_count': neu,
                'mixed_count': mix,
                'most_problematic': most_problematic,
                'most_praised': most_praised
            },
            'records': records
        }

    @staticmethod
    def export_csv_stream(filters=None):
        data = ReportService.generate_report_data(filters)
        records = data['records']

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Feedback ID', 'Roll Number', 'Student Name', 'Department',
            'Category', 'Rating', 'Sentiment', 'Sentiment Score',
            'Feedback Text', 'Status', 'Submission Date'
        ])

        for r in records:
            writer.writerow([
                r['id'],
                r.get('student_roll_no', 'N/A'),
                r.get('student_name', 'Anonymous'),
                r.get('department', 'General'),
                r['category'],
                r['rating'],
                r['sentiment'],
                float(r['sentiment_score']),
                r['feedback_text'].replace('\n', ' ').strip(),
                r['status'],
                str(r['created_at'])
            ])

        output.seek(0)
        return output
