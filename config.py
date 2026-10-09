import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'se_lab_project_ai_student_feedback_secure_key_2026')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'resh')
    DB_NAME = os.getenv('DB_NAME', 'ai_student_feedback')
    
    # Optional offline SQLite fallback mode for smooth evaluation on systems without MySQL
    USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1', 't')
    SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'ai_student_feedback.db')
    
    # Optional Gemini API Key (offline rule/lexicon engine runs automatically if unset)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
