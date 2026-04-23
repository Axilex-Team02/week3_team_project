import sqlite3
import os

DB_PATH = os.path.join('backend', 'electrician_contractor_management', 'contractor.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add completed_at to Tasks
    try:
        cursor.execute('ALTER TABLE Tasks ADD COLUMN completed_at TEXT')
        print("Added completed_at to Tasks")
    except sqlite3.OperationalError:
        print("completed_at already exists in Tasks")
        
    # Create Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users (id)
        )
    ''')
    print("Ensured Notifications table exists")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
