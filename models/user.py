from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db

class User:
    @staticmethod
    def get_by_id(user_id):
        return db.execute_query(
            "SELECT id, student_id, name, email, role, department, year, semester, created_at FROM users WHERE id = %s",
            (user_id,),
            fetchone=True
        )

    @staticmethod
    def get_by_email(email):
        return db.execute_query(
            "SELECT id, student_id, name, email, password_hash, role, department, year, semester, created_at FROM users WHERE LOWER(email) = LOWER(%s)",
            (email.strip(),),
            fetchone=True
        )

    @staticmethod
    def get_by_student_id(student_id):
        return db.execute_query(
            "SELECT id, student_id, name, email, role, department, year, semester, created_at FROM users WHERE student_id = %s",
            (student_id.strip(),),
            fetchone=True
        )

    @staticmethod
    def verify_password(stored_hash, password):
        if not stored_hash or not password:
            return False
        return check_password_hash(stored_hash, password)

    @staticmethod
    def create(name, email, password, role='student', department='Computer Science & Engineering', year=1, semester=1, student_id=None):
        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO users (student_id, name, email, password_hash, role, department, year, semester)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        user_id = db.execute_non_query(
            query,
            (student_id, name.strip(), email.strip().lower(), password_hash, role, department, year, semester)
        )
        return user_id

    @staticmethod
    def count_students():
        res = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'student'", fetchone=True)
        return res['count'] if res else 0

    @staticmethod
    def get_all_students():
        return db.execute_query(
            "SELECT id, student_id, name, email, department, year, semester, created_at FROM users WHERE role = 'student' ORDER BY name ASC"
        )
