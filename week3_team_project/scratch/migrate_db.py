import sqlite3
import os

DB_PATH = os.path.join('e:\\week2_team_project', 'backend', 'electrician_contractor_management', 'contractor.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add columns to Jobs
    try:
        cursor.execute("ALTER TABLE Jobs ADD COLUMN location TEXT")
        print("Added 'location' to Jobs")
    except sqlite3.OperationalError:
        print("'location' already exists in Jobs")

    try:
        cursor.execute("ALTER TABLE Jobs ADD COLUMN deadline TEXT")
        print("Added 'deadline' to Jobs")
    except sqlite3.OperationalError:
        print("'deadline' already exists in Jobs")

    # Add columns to Tasks
    try:
        cursor.execute("ALTER TABLE Tasks ADD COLUMN assigned_electrician_id INTEGER")
        print("Added 'assigned_electrician_id' to Tasks")
    except sqlite3.OperationalError:
        print("'assigned_electrician_id' already exists in Tasks")

    # Update Tasks status from 'Incomplete' to 'Pending' if needed
    cursor.execute("UPDATE Tasks SET status = 'Pending' WHERE status = 'Incomplete'")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == '__main__':
    migrate()
