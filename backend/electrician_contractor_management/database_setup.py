import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contractor.db')

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'admin'
        )
    ''')

    # Electricians Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Electricians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            status TEXT DEFAULT 'Available'
        )
    ''')

    # Jobs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            deadline TEXT,
            assigned_electrician_id INTEGER,
            status TEXT DEFAULT 'Pending',
            image_path TEXT,
            price REAL DEFAULT 0.0,
            FOREIGN KEY (assigned_electrician_id) REFERENCES Electricians (id)
        )
    ''')

    # Tasks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Incomplete',
            assigned_electrician_id INTEGER,
            completed_at TEXT,
            report_path TEXT,
            FOREIGN KEY (job_id) REFERENCES Jobs (id),
            FOREIGN KEY (assigned_electrician_id) REFERENCES Electricians (id)
        )
    ''')

    # Payments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            from_user_id INTEGER,
            to_user_id INTEGER,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            transaction_id TEXT,
            payment_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES Jobs(id),
            FOREIGN KEY (from_user_id) REFERENCES Users(id),
            FOREIGN KEY (to_user_id) REFERENCES Users(id)
        )
    ''')

    # Notifications Table
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
    # Materials Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            unit TEXT,
            last_usage TEXT
        )
    ''')
    cursor.execute("SELECT * FROM Users WHERE username='admin'")
    if not cursor.fetchone():
        # Using a simple raw password for demonstration; hashed passwords in real app
        from werkzeug.security import generate_password_hash
        hashed_pw = generate_password_hash('admin123')
        cursor.execute("INSERT INTO Users (username, email, password, role) VALUES (?, ?, ?, ?)", ('admin', 'admin@example.com', hashed_pw, 'admin'))

    # Insert some dummy electricians
    cursor.execute("SELECT COUNT(*) FROM Electricians")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO Electricians (name, phone, email, status) VALUES (?, ?, ?, ?)", [
            ('Bhoomika', '555-0103', 'bhoomika@example.com', 'Available'),
            ('Bhuvana', '555-0104', 'bhuvana@example.com', 'Available'),
            ('Manasa', '555-0105', 'manasa@example.com', 'Available')
        ])

    conn.commit()
    conn.close()
    print("Database contractor.db created successfully.")

if __name__ == '__main__':
    create_database()
