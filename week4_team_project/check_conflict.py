import sqlite3
import os

DB_PATH = os.path.join('backend', 'electrician_contractor_management', 'contractor.db')

def check_conflict():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    username = "Bhoomika"
    email = "bhoomi3109@gmail.com"
    
    u_name = cursor.execute('SELECT * FROM Users WHERE username=?', (username,)).fetchone()
    u_email = cursor.execute('SELECT * FROM Users WHERE email=?', (email,)).fetchone()
    
    print(f"By Name ({username}):", dict(u_name) if u_name else "None")
    print(f"By Email ({email}):", dict(u_email) if u_email else "None")
    
    conn.close()

if __name__ == '__main__':
    check_conflict()
