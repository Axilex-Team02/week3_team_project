import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contractor.db')

def populate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sample Materials
    cursor.executemany("INSERT INTO Materials (name, quantity, unit) VALUES (?, ?, ?)", [
        ('Copper Wire (12 AWG)', 500, 'Feet'),
        ('Electrical Tape (Black)', 20, 'Rolls'),
        ('Junction Box (Standard)', 50, 'Pieces'),
        ('Circuit Breaker (15A)', 15, 'Pieces')
    ])

    # Sample Jobs
    today = datetime.date.today().strftime("%Y-%m-%d")
    deadline = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.executemany("INSERT INTO Jobs (title, description, location, deadline, assigned_electrician_id, status) VALUES (?, ?, ?, ?, ?, ?)", [
        ('Residential Rewiring', 'Complete rewiring of 3-bedroom house', '123 Oak St', deadline, 1, 'In Progress'),
        ('Panel Upgrade', 'Upgrade main service panel to 200A', '456 Maple Ave', today, 2, 'Completed'),
        ('Kitchen Lighting Install', 'Install recessed lighting and dimmer switches', '789 Pine Rd', deadline, 3, 'Pending')
    ])

    # Sample Tasks
    cursor.executemany("INSERT INTO Tasks (job_id, description, status, assigned_electrician_id, completed_at) VALUES (?, ?, ?, ?, ?)", [
        (1, 'Remove old wiring', 'Completed', 1, f"{today} 09:00:00"),
        (1, 'Pull new wires', 'In Progress', 1, None),
        (2, 'Mount new panel', 'Completed', 2, f"{today} 11:00:00"),
        (2, 'Connect breakers', 'Completed', 2, f"{today} 14:00:00"),
        (3, 'Mark lighting locations', 'Pending', 3, None)
    ])

    conn.commit()
    conn.close()
    print("Sample data populated successfully.")

if __name__ == '__main__':
    populate()
