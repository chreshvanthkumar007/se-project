import json
from database.db import db

class Feedback:
    @staticmethod
    def create(student_id, category, rating, feedback_text, sentiment='Neutral', sentiment_score=0.00, status='Analyzed'):
        query = """
            INSERT INTO feedback (student_id, category, rating, feedback_text, sentiment, sentiment_score, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        feedback_id = db.execute_non_query(
            query,
            (student_id, category, rating, feedback_text.strip(), sentiment, sentiment_score, status)
        )
        return feedback_id

    @staticmethod
    def save_analysis(feedback_id, keywords, topics, strengths, problems, recommendations):
        kw_json = json.dumps(keywords if isinstance(keywords, list) else [keywords])
        top_json = json.dumps(topics if isinstance(topics, list) else [topics])
        str_json = json.dumps(strengths if isinstance(strengths, list) else [strengths])
        prb_json = json.dumps(problems if isinstance(problems, list) else [problems])
        rec_json = json.dumps(recommendations if isinstance(recommendations, list) else [recommendations])

        query = """
            INSERT INTO feedback_analysis (feedback_id, keywords, topics, strengths, problems, recommendations)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                keywords = VALUES(keywords),
                topics = VALUES(topics),
                strengths = VALUES(strengths),
                problems = VALUES(problems),
                recommendations = VALUES(recommendations),
                analyzed_at = CURRENT_TIMESTAMP
        """
        return db.execute_non_query(query, (feedback_id, kw_json, top_json, str_json, prb_json, rec_json))

    @staticmethod
    def get_by_id(feedback_id):
        query = """
            SELECT 
                f.id, f.student_id, f.category, f.rating, f.feedback_text,
                f.sentiment, f.sentiment_score, f.status, f.created_at,
                u.name as student_name, u.email as student_email,
                u.student_id as student_roll_no, u.department, u.year, u.semester,
                fa.keywords, fa.topics, fa.strengths, fa.problems, fa.recommendations, fa.analyzed_at
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            LEFT JOIN feedback_analysis fa ON f.id = fa.feedback_id
            WHERE f.id = %s
        """
        row = db.execute_query(query, (feedback_id,), fetchone=True)
        if not row:
            return None
        
        # Parse JSON fields safely
        for col in ['keywords', 'topics', 'strengths', 'problems', 'recommendations']:
            val = row.get(col)
            if val:
                try:
                    row[col] = json.loads(val)
                except Exception:
                    row[col] = [val] if val else []
            else:
                row[col] = []
        return row

    @staticmethod
    def get_by_student(student_id):
        query = """
            SELECT 
                f.id, f.category, f.rating, f.feedback_text,
                f.sentiment, f.sentiment_score, f.status, f.created_at,
                fa.keywords, fa.topics, fa.strengths, fa.problems, fa.recommendations
            FROM feedback f
            LEFT JOIN feedback_analysis fa ON f.id = fa.feedback_id
            WHERE f.student_id = %s
            ORDER BY f.created_at DESC
        """
        rows = db.execute_query(query, (student_id,), fetchall=True)
        for row in rows:
            for col in ['keywords', 'topics', 'strengths', 'problems', 'recommendations']:
                val = row.get(col)
                if val:
                    try:
                        row[col] = json.loads(val)
                    except Exception:
                        row[col] = [val] if val else []
                else:
                    row[col] = []
        return rows

    @staticmethod
    def get_all(search=None, category=None, sentiment=None, rating=None, department=None, start_date=None, end_date=None, page=1, per_page=10):
        where_clauses = ["1=1"]
        params = []

        if search:
            search_term = f"%{search.strip()}%"
            where_clauses.append("(u.name LIKE %s OR u.student_id LIKE %s OR f.feedback_text LIKE %s OR f.category LIKE %s)")
            params.extend([search_term, search_term, search_term, search_term])

        if category and category.lower() != 'all':
            where_clauses.append("f.category = %s")
            params.append(category)

        if sentiment and sentiment.lower() != 'all':
            where_clauses.append("f.sentiment = %s")
            params.append(sentiment)

        if rating and rating.lower() != 'all':
            where_clauses.append("f.rating = %s")
            params.append(int(rating))

        if department and department.lower() != 'all':
            where_clauses.append("u.department = %s")
            params.append(department)

        if start_date:
            where_clauses.append("DATE(f.created_at) >= %s")
            params.append(start_date)

        if end_date:
            where_clauses.append("DATE(f.created_at) <= %s")
            params.append(end_date)

        where_sql = " AND ".join(where_clauses)

        # Count total matching rows
        count_query = f"""
            SELECT COUNT(*) as total
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            WHERE {where_sql}
        """
        total_row = db.execute_query(count_query, tuple(params), fetchone=True)
        total = total_row['total'] if total_row else 0

        # Paged rows query
        offset = (page - 1) * per_page
        list_query = f"""
            SELECT 
                f.id, f.student_id, f.category, f.rating, f.feedback_text,
                f.sentiment, f.sentiment_score, f.status, f.created_at,
                u.name as student_name, u.student_id as student_roll_no, u.department
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            WHERE {where_sql}
            ORDER BY f.created_at DESC
            LIMIT {int(per_page)} OFFSET {int(offset)}
        """
        rows = db.execute_query(list_query, tuple(params), fetchall=True)

        return {
            'items': rows,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        }

    @staticmethod
    def delete(feedback_id):
        # Cascades to feedback_analysis
        return db.execute_non_query("DELETE FROM feedback WHERE id = %s", (feedback_id,))

    @staticmethod
    def get_categories():
        return db.execute_query("SELECT id, category_name, description FROM categories ORDER BY category_name ASC")

    @staticmethod
    def get_departments():
        rows = db.execute_query("SELECT DISTINCT department FROM users WHERE department IS NOT NULL AND department != '' ORDER BY department ASC")
        return [r['department'] for r in rows]
