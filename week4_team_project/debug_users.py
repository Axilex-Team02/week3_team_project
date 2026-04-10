import sqlite3
import os

DB_PATH = os.path.join('backend', 'electrician_contractor_management', 'contractor.db')

def debug_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    users = conn.execute('SELECT id, username, email FROM Users').fetchall()
    print("All Users:")
    for u in users:
        print(dict(u))
    conn.close()

if __name__ == '__main__':
    debug_users()
