import sqlite3
import os

DB_PATH = os.path.join('backend', 'electrician_contractor_management', 'contractor.db')

def check_user():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check for User
    cursor.execute('SELECT * FROM Users WHERE username="Bhoomika" OR email="bhoomi3109@gmail.com"')
    user = cursor.fetchone()
    if user:
        print("Found matching user in Users table:")
        print(dict(user))
    else:
        print("No matching user found in Users table.")
        
    # Also check Electricians table for context
    cursor.execute('SELECT * FROM Electricians WHERE name="Bhoomika" OR email="bhoomi3109@gmail.com"')
    electrician = cursor.fetchone()
    if electrician:
        print("\nFound matching record in Electricians table:")
        print(dict(electrician))
        
    conn.close()

if __name__ == '__main__':
    check_user()
