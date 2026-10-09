import os
import sys

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import db

def main():
    force_reset = '--reset' in sys.argv
    print(f"Initializing AI Student Feedback database (force_reset={force_reset})...")
    db.init_database(force_reset=force_reset)
    print("Database initialization complete.")

if __name__ == '__main__':
    main()
