import os
import sqlite3
import pymysql
import pymysql.cursors
from config import Config

def split_sql_statements(sql_text):
    """
    Splits SQL statements by semicolon while respecting single and double quotes.
    Prevents corruption when string literals contain semicolons.
    """
    statements = []
    current_statement = []
    in_single_quote = False
    in_double_quote = False
    escape = False

    for char in sql_text:
        if escape:
            current_statement.append(char)
            escape = False
            continue

        if char == '\\':
            escape = True
            current_statement.append(char)
            continue

        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote

        if char == ';' and not in_single_quote and not in_double_quote:
            stmt = ''.join(current_statement).strip()
            if stmt:
                statements.append(stmt)
            current_statement = []
        else:
            current_statement.append(char)

    last_stmt = ''.join(current_statement).strip()
    if last_stmt:
        statements.append(last_stmt)
    return statements

class DatabaseManager:
    """
    Database Manager supporting MySQL with automatic SQLite fallback.
    Provides parameterized query execution, transaction support, and schema initialization.
    """
    def __init__(self):
        self.use_sqlite = Config.USE_SQLITE
        self.sqlite_path = Config.SQLITE_PATH
        self._check_mysql_availability()

    def _check_mysql_availability(self):
        if self.use_sqlite:
            return
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                connect_timeout=2
            )
            conn.close()
        except Exception as e:
            print(f"[DatabaseManager Warning] MySQL connection failed: {e}. Falling back to SQLite for robust execution.")
            self.use_sqlite = True

    def get_connection(self):
        if self.use_sqlite:
            os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            return pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                charset='utf8mb4'
            )

    def execute_query(self, query, params=None, fetchone=False, fetchall=True):
        """
        Executes a SELECT query with parameterized inputs.
        """
        conn = self.get_connection()
        params = params or ()
        try:
            if self.use_sqlite:
                sqlite_sql = query.replace('%s', '?')
                cursor = conn.cursor()
                cursor.execute(sqlite_sql, params)
                if fetchone:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                elif fetchall:
                    rows = cursor.fetchall()
                    return [dict(r) for r in rows]
                return None
            else:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    if fetchone:
                        return cursor.fetchone()
                    elif fetchall:
                        return cursor.fetchall()
                    return None
        finally:
            conn.close()

    def execute_non_query(self, query, params=None, commit=True):
        """
        Executes an INSERT, UPDATE, or DELETE query with parameterized inputs.
        Returns last inserted ID or rowcount.
        """
        conn = self.get_connection()
        params = params or ()
        try:
            if self.use_sqlite:
                sqlite_sql = query.replace('%s', '?')
                cursor = conn.cursor()
                cursor.execute(sqlite_sql, params)
                last_id = cursor.lastrowid
                if commit:
                    conn.commit()
                return last_id or cursor.rowcount
            else:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    last_id = cursor.lastrowid
                    if commit:
                        conn.commit()
                    return last_id or cursor.rowcount
        except Exception as e:
            if not self.use_sqlite:
                conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self, force_reset=False):
        """
        Initializes the database schema and sample data.
        """
        if self.use_sqlite:
            self._init_sqlite(force_reset)
        else:
            self._init_mysql(force_reset)

    def _init_mysql(self, force_reset=False):
        # 1. Connect without database to ensure database exists
        server_conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset='utf8mb4'
        )
        with server_conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        server_conn.commit()
        server_conn.close()

        # 2. Check if tables exist and have data
        db_conn = self.get_connection()
        try:
            with db_conn.cursor() as cur:
                cur.execute("SHOW TABLES LIKE 'users';")
                has_users = cur.fetchone()
                if has_users and not force_reset:
                    cur.execute("SELECT COUNT(*) as cnt FROM users;")
                    row = cur.fetchone()
                    if row and row['cnt'] > 0:
                        print("[DatabaseManager] MySQL database already initialized with users.")
                        return

            # Read and execute schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_content = f.read()
                statements = split_sql_statements(schema_content)
                with db_conn.cursor() as cur:
                    for stmt in statements:
                        clean_stmt = stmt.strip()
                        if not clean_stmt or clean_stmt.upper().startswith('CREATE DATABASE') or clean_stmt.upper().startswith('USE '):
                            continue
                        cur.execute(clean_stmt)
                db_conn.commit()
                print("[DatabaseManager] MySQL Schema successfully applied.")

            # Read and execute sample_data.sql
            sample_path = os.path.join(os.path.dirname(__file__), 'sample_data.sql')
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    sample_content = f.read()
                statements = split_sql_statements(sample_content)
                with db_conn.cursor() as cur:
                    for stmt in statements:
                        clean_stmt = stmt.strip()
                        if not clean_stmt or clean_stmt.upper().startswith('USE '):
                            continue
                        cur.execute(clean_stmt)
                db_conn.commit()
                print("[DatabaseManager] MySQL Sample data successfully seeded.")
        finally:
            db_conn.close()

    def _init_sqlite(self, force_reset=False):
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            department TEXT DEFAULT 'Computer Science & Engineering',
            year INTEGER DEFAULT 3,
            semester INTEGER DEFAULT 5,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            feedback_text TEXT NOT NULL,
            sentiment TEXT NOT NULL DEFAULT 'Neutral',
            sentiment_score REAL NOT NULL DEFAULT 0.00,
            status TEXT NOT NULL DEFAULT 'Analyzed',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS feedback_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback_id INTEGER NOT NULL UNIQUE,
            keywords TEXT,
            topics TEXT,
            strengths TEXT,
            problems TEXT,
            recommendations TEXT,
            analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (feedback_id) REFERENCES feedback(id) ON DELETE CASCADE
        );
        """)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0 or force_reset:
            admin_pwd = 'scrypt:32768:8:1$B0UAVvY4h7y9KcVb$8b465fe28a18d3ea7072b8e90fb5760bc19865ced9b20c0d93d918c73d68e6b867b724464b95bc5fba236fa5b5c3827d1a8e8488b01a19222a8864d16ff2b562'
            stu_pwd = 'scrypt:32768:8:1$ctZJm1AG6m2Dx96l$987895c2006d9dd7551d592d6809eeb0b01bfa5285b9da149e4f834d4b75fa049a515539c9276b8f6dba1592033d72a3919005449328b72aa5af4fd67a3004ef'
            
            cur.execute("INSERT INTO users (student_id, name, email, password_hash, role, department, year, semester) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (None, 'Dean Dr. Ronald Vance', 'admin@college.edu', admin_pwd, 'admin', 'Academic Administration', 0, 0))
            
            students = [
                ('STU202401', 'Alex Turner', 'alex.turner@college.edu', stu_pwd, 'student', 'Computer Science & Engineering', 3, 5),
                ('STU202402', 'Priya Sharma', 'priya.sharma@college.edu', stu_pwd, 'student', 'Computer Science & Engineering', 3, 5),
                ('STU202403', 'Rahul Verma', 'rahul.verma@college.edu', stu_pwd, 'student', 'Information Technology', 2, 3),
                ('STU202404', 'Ananya Sen', 'ananya.sen@college.edu', stu_pwd, 'student', 'Electronics & Communication', 4, 7),
                ('STU202405', 'David Miller', 'david.miller@college.edu', stu_pwd, 'student', 'Mechanical Engineering', 2, 4),
                ('STU202406', 'Sneha Patel', 'sneha.patel@college.edu', stu_pwd, 'student', 'Civil Engineering', 3, 6),
                ('STU202407', 'Arjun Nair', 'arjun.nair@college.edu', stu_pwd, 'student', 'Computer Science & Engineering', 4, 8),
                ('STU202408', 'Kavita Reddy', 'kavita.reddy@college.edu', stu_pwd, 'student', 'Information Technology', 1, 2)
            ]
            cur.executemany("INSERT INTO users (student_id, name, email, password_hash, role, department, year, semester) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", students)

            cats = [
                ('Faculty', 'Feedback related to faculty behavior, guidance, and mentorship.'),
                ('Course', 'Curriculum relevance, syllabus pacing, and academic content.'),
                ('Teaching', 'Teaching methodologies, pedagogy, and classroom explanations.'),
                ('Laboratory', 'Lab equipment, hardware, practical experiments, and technical staff.'),
                ('Infrastructure', 'Classrooms, projectors, air conditioning, seating, and power outlets.'),
                ('Library', 'Availability of books, digital journals, study spaces, and reading halls.'),
                ('Campus', 'Campus cleanliness, cafeteria, green spaces, sports facilities, and parking.'),
                ('Student Services', 'Administrative desk, placement cell, scholarship help, and grievance cell.'),
                ('Overall Experience', 'General college atmosphere, institutional culture, and student life.')
            ]
            cur.executemany("INSERT OR IGNORE INTO categories (category_name, description) VALUES (?, ?)", cats)
            conn.commit()
            print("[DatabaseManager] SQLite Database initialized with seed accounts.")
        conn.close()

# Singleton instance
db = DatabaseManager()
