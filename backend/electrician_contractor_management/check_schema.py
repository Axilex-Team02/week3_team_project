import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contractor.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
print(c.execute("SELECT sql FROM sqlite_master WHERE name='Users'").fetchone()[0])
conn.close()
