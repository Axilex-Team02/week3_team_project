import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contractor.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Starting database migration...")

    # 1. Add user_id to Electricians table
    try:
        cursor.execute('ALTER TABLE Electricians ADD COLUMN user_id INTEGER REFERENCES Users(id)')
        print("- Added user_id to Electricians table.")
    except sqlite3.OperationalError:
        print("- user_id already exists in Electricians table.")

    # 2. Add image_path to Jobs table
    try:
        cursor.execute('ALTER TABLE Jobs ADD COLUMN image_path TEXT')
        print("- Added image_path to Jobs table.")
    except sqlite3.OperationalError:
        print("- image_path already exists in Jobs table.")

    # 3. Add report_path to Tasks table
    try:
        cursor.execute('ALTER TABLE Tasks ADD COLUMN report_path TEXT')
        print("- Added report_path to Tasks table.")
    except sqlite3.OperationalError:
        print("- report_path already exists in Tasks table.")

    # 4. Ensure some initial roles are correct (if needed)
    cursor.execute("UPDATE Users SET role = 'admin' WHERE username = 'admin'")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == '__main__':
    migrate()
