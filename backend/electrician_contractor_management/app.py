"""
AXILEX PVT LTD - Electrician Contractor Management System
Backend Engine (Flask Application)

This module handles all core business logic, database interactions, 
and API endpoints for the contractor management system.

Features:
- Role-Based Access Control (RBAC)
- Job and Task Lifecycle Management
- Material Inventory Tracking
- Professional Reporting and KPI Extraction
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = 'axilex_secret_key_2024' # Secure key for session encryption

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'contractor.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    """Establishes and returns a connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# RBAC Decorators
def login_required(f):
    """Decorator to ensure the user is logged in before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure the user has administrator privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    return dict(user_role=session.get('role'), username=session.get('username'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        role = request.form.get('role', 'electrician')
        
        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            # Using INSERT OR REPLACE to allow "re-registering" with the same email
            # This makes it easier for the user to "any email id will be signup or login"
            conn.execute('''INSERT OR REPLACE INTO Users (id, username, email, password, phone, role) 
                            VALUES ((SELECT id FROM Users WHERE email = ?), ?, ?, ?, ?, ?)''',
                         (email, username, email, hashed_pw, phone, role))
            conn.commit()
        except sqlite3.Error as e:
            flash(f'An error occurred: {str(e)}', 'error')
            conn.close()
            return redirect(url_for('register'))
            
        conn.close()
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    
    # Filter by role
    if session['role'] == 'admin':
        electricians_count = conn.execute('SELECT COUNT(*) FROM Electricians').fetchone()[0]
        jobs_count = conn.execute('SELECT COUNT(*) FROM Jobs').fetchone()[0]
        tasks_count = conn.execute('SELECT COUNT(*) FROM Tasks').fetchone()[0]
        recent_jobs = conn.execute('SELECT * FROM Jobs ORDER BY id DESC LIMIT 5').fetchall()
        recent_tasks = conn.execute('SELECT t.*, j.title as job_title FROM Tasks t JOIN Jobs j ON t.job_id = j.id ORDER BY t.id DESC LIMIT 5').fetchall()
    else:
        # For electricians, only show counts related to them
        el = conn.execute('SELECT id FROM Electricians WHERE email = (SELECT email FROM Users WHERE id = ?)', (session['user_id'],)).fetchone()
        if el:
            jobs_count = conn.execute('SELECT COUNT(*) FROM Jobs WHERE assigned_electrician_id = ?', (el['id'],)).fetchone()[0]
            tasks_count = conn.execute('SELECT COUNT(*) FROM Tasks WHERE assigned_electrician_id = ?', (el['id'],)).fetchone()[0]
            recent_jobs = conn.execute('SELECT * FROM Jobs WHERE assigned_electrician_id = ? ORDER BY id DESC LIMIT 5', (el['id'],)).fetchall()
            recent_tasks = conn.execute('SELECT t.*, j.title as job_title FROM Tasks t JOIN Jobs j ON t.job_id = j.id WHERE t.assigned_electrician_id = ? ORDER BY t.id DESC LIMIT 5', (el['id'],)).fetchall()
        else:
            jobs_count = tasks_count = 0
            recent_jobs = []
            recent_tasks = []
        electricians_count = 0
    
    conn.close()
    return render_template('dashboard.html', 
                           electricians_count=electricians_count,
                           jobs_count=jobs_count,
                           tasks_count=tasks_count,
                           recent_jobs=recent_jobs,
                           recent_tasks=recent_tasks)

@app.route('/electricians', methods=['GET', 'POST'])
@admin_required
def electricians():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')
        status = request.form.get('status', 'Available')
        
        try:
            conn.execute('INSERT INTO Electricians (name, phone, email, status) VALUES (?, ?, ?, ?)',
                         (name, phone, email, status))
            conn.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'success', 'message': 'Electrician added successfully'})
            flash('Electrician added successfully', 'success')
        except sqlite3.Error as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': str(e)}), 400
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.close()
        return redirect(url_for('electricians'))

    els = conn.execute('SELECT * FROM Electricians').fetchall()
    conn.close()
    return render_template('electricians.html', electricians=els)

@app.route('/electricians/update/<int:id>', methods=['POST'])
@admin_required
def update_electrician(id):
    name = request.form['name']
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    status = request.form.get('status', 'Available')
    
    conn = get_db_connection()
    conn.execute('UPDATE Electricians SET name = ?, phone = ?, email = ?, status = ? WHERE id = ?',
                 (name, phone, email, status, id))
    conn.commit()
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Electrician updated successfully'})
    flash('Electrician updated successfully', 'success')
    return redirect(url_for('electricians'))

@app.route('/electricians/delete/<int:id>', methods=['POST'])
@admin_required
def delete_electrician(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Electricians WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Electrician deleted'})
    flash('Electrician deleted', 'success')
    return redirect(url_for('electricians'))

@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    conn = get_db_connection()
    if request.method == 'POST':
        if session['role'] != 'admin':
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        title = request.form['title']
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        deadline = request.form.get('deadline', '')
        price = request.form.get('price', 0.0)
        try:
            price = float(price)
        except ValueError:
            price = 0.0
        assigned_id = request.form.get('assignee_id')
        if assigned_id == 'None': assigned_id = None
        
        try:
            cur = conn.execute('INSERT INTO Jobs (title, description, location, deadline, price, assigned_electrician_id) VALUES (?, ?, ?, ?, ?, ?)',
                         (title, description, location, deadline, price, assigned_id))
            job_id = cur.lastrowid
            
            # Create notification for the assigned electrician
            if assigned_id:
                # Find the user_id for this electrician email
                el_email = conn.execute('SELECT email FROM Electricians WHERE id = ?', (assigned_id,)).fetchone()
                if el_email:
                    target_user = conn.execute('SELECT id FROM Users WHERE email = ?', (el_email['email'],)).fetchone()
                    if target_user:
                        conn.execute('INSERT INTO Notifications (user_id, message, type) VALUES (?, ?, ?)',
                                     (target_user['id'], f'A new job "{title}" has been assigned to you.', 'info'))
            
            conn.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'success', 'message': 'Job created successfully', 'job_id': job_id})
            flash('Job created successfully', 'success')
        except sqlite3.Error as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': str(e)}), 400
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.close()
        return redirect(url_for('jobs'))

    # Search and Filter
    q = request.args.get('q', '')
    if session['role'] == 'admin':
        query = 'SELECT j.*, e.name as electrician_name FROM Jobs j LEFT JOIN Electricians e ON j.assigned_electrician_id = e.id'
        params = []
        if q:
            query += ' WHERE j.title LIKE ? OR j.location LIKE ?'
            params = [f'%{q}%', f'%{q}%']
        jobs = conn.execute(query, params).fetchall()
    else:
        el = conn.execute('SELECT id FROM Electricians WHERE email = (SELECT email FROM Users WHERE id = ?)', (session['user_id'],)).fetchone()
        if el:
            query = 'SELECT * FROM Jobs WHERE assigned_electrician_id = ?'
            params = [el['id']]
            if q:
                query += ' AND (title LIKE ? OR location LIKE ?)'
                params.extend([f'%{q}%', f'%{q}%'])
            jobs = conn.execute(query, params).fetchall()
        else:
            jobs = []
    
    els = conn.execute('SELECT id, name FROM Electricians').fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs, electricians=els)

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    conn = get_db_connection()
    if request.method == 'POST':
        if session['role'] != 'admin':
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        job_id = request.form['job_id']
        description = request.form['description']
        assigned_id = request.form.get('assignee_id')
        if assigned_id == 'None': assigned_id = None
        
        try:
            cur = conn.execute('INSERT INTO Tasks (job_id, description, assigned_electrician_id) VALUES (?, ?, ?)',
                         (job_id, description, assigned_id))
            task_id = cur.lastrowid
            
            # Create notification for assigned electrician
            if assigned_id:
                el_email = conn.execute('SELECT email FROM Electricians WHERE id = ?', (assigned_id,)).fetchone()
                if el_email:
                    target_user = conn.execute('SELECT id FROM Users WHERE email = ?', (el_email['email'],)).fetchone()
                    if target_user:
                        conn.execute('INSERT INTO Notifications (user_id, message, type) VALUES (?, ?, ?)',
                                     (target_user['id'], f'New Task: "{description}"', 'info'))
            
            conn.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'success', 'message': 'Task created successfully', 'task_id': task_id})
            flash('Task created successfully', 'success')
        except sqlite3.Error as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': str(e)}), 400
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.close()
        return redirect(url_for('tasks'))

    if session['role'] == 'admin':
        tasks = conn.execute('SELECT t.*, j.title as job_title, e.name as electrician_name FROM Tasks t JOIN Jobs j ON t.job_id = j.id LEFT JOIN Electricians e ON t.assigned_electrician_id = e.id').fetchall()
    else:
        el = conn.execute('SELECT id FROM Electricians WHERE email = (SELECT email FROM Users WHERE id = ?)', (session['user_id'],)).fetchone()
        tasks = conn.execute('SELECT t.*, j.title as job_title FROM Tasks t JOIN Jobs j ON t.job_id = j.id WHERE t.assigned_electrician_id = ?', (el['id'],)).fetchall() if el else []
    
    jobs = conn.execute('SELECT id, title FROM Jobs').fetchall()
    els = conn.execute('SELECT id, name FROM Electricians').fetchall()
    conn.close()
    return render_template('tasks.html', tasks=tasks, jobs=jobs, electricians=els)

@app.route('/tasks/update_status/<int:id>', methods=['POST'])
@login_required
def update_task_status(id):
    status = request.form['status']
    conn = get_db_connection()
    
    completed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == 'Completed' else None
    
    conn.execute('UPDATE Tasks SET status = ?, completed_at = ? WHERE id = ?', (status, completed_at, id))
    conn.commit()
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Status updated'})
    return redirect(url_for('tasks'))

@app.route('/materials', methods=['GET', 'POST'])
@admin_required
def materials():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form.get('quantity', 0)
        unit = request.form.get('unit', '')
        
        conn.execute('INSERT INTO Materials (name, quantity, unit) VALUES (?, ?, ?)',
                     (name, quantity, unit))
        conn.commit()
        conn.close()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'message': 'Material added'})
        return redirect(url_for('materials'))

    mats = conn.execute('SELECT * FROM Materials').fetchall()
    conn.close()
    return render_template('materials.html', materials=mats)

@app.route('/materials/update_usage/<int:id>', methods=['POST'])
@login_required
def update_material_usage(id):
    usage_qty = int(request.form['usage_qty'])
    conn = get_db_connection()
    mat = conn.execute('SELECT * FROM Materials WHERE id = ?', (id,)).fetchone()
    
    if mat and mat['quantity'] >= usage_qty:
        new_qty = mat['quantity'] - usage_qty
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute('UPDATE Materials SET quantity = ?, last_usage = ? WHERE id = ?', (new_qty, now, id))
        conn.commit()
        message = 'Usage logged successfully'
        status = 'success'
    else:
        message = 'Insufficient quantity'
        status = 'error'
        
    conn.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': status, 'message': message})
    flash(message, status)
    return redirect(url_for('materials'))

@app.route('/reporter')
@admin_required
def reporter():
    return render_template('reporter.html')

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        upload_type = request.form.get('type') # 'job' or 'task'
        upload_id = request.form.get('id')
        
        # Use forward slashes for URL compatibility
        file_path = f"{upload_type}/{filename}"
        
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_type)
        os.makedirs(full_path, exist_ok=True)
        file.save(os.path.join(full_path, filename))
        
        conn = get_db_connection()
        if upload_type == 'job':
            conn.execute('UPDATE Jobs SET image_path = ? WHERE id = ?', (file_path, upload_id))
        else:
            conn.execute('UPDATE Tasks SET report_path = ? WHERE id = ?', (file_path, upload_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'File uploaded successfully'})

@app.route('/api/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/reports/stats')
@login_required
def report_stats():
    conn = get_db_connection()
    completion = conn.execute('SELECT status, COUNT(*) as count FROM Tasks GROUP BY status').fetchall()
    activity = conn.execute('SELECT e.name, COUNT(t.id) as task_count FROM Electricians e LEFT JOIN Tasks t ON e.id = t.assigned_electrician_id GROUP BY e.id').fetchall()
    
    # Totals
    total_jobs = conn.execute('SELECT COUNT(*) FROM Jobs').fetchone()[0]
    total_tasks = conn.execute('SELECT COUNT(*) FROM Tasks').fetchone()[0]
    total_electricians = conn.execute('SELECT COUNT(*) FROM Electricians').fetchone()[0]
    total_materials = conn.execute('SELECT COUNT(*) FROM Materials').fetchone()[0]
    
    # Completion Rate
    completed_tasks = conn.execute("SELECT COUNT(*) FROM Tasks WHERE status = 'Completed'").fetchone()[0]
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    # High Priority Alerts (near or past deadline)
    today = datetime.date.today().strftime("%Y-%m-%d")
    priority_jobs = conn.execute('SELECT title, deadline, status FROM Jobs WHERE deadline <= ? AND status != "Completed" LIMIT 5', (today,)).fetchall()
    
    # Daily Accomplishment
    daily_count = conn.execute("SELECT COUNT(*) FROM Tasks WHERE status = 'Completed' AND completed_at LIKE ?", (f"{today}%",)).fetchone()[0]
    
    conn.close()
    return jsonify({
        'completion': [dict(row) for row in completion],
        'activity': [dict(row) for row in activity],
        'daily_count': daily_count,
        'totals': {
            'jobs': total_jobs,
            'tasks': total_tasks,
            'electricians': total_electricians,
            'materials': total_materials
        },
        'completion_rate': completion_rate,
        'projected_rate': 75,
        'target_rate': 90,
        'priority_jobs': [dict(row) for row in priority_jobs]
    })

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        password = request.form.get('password')
        if password:
            hashed_pw = generate_password_hash(password)
            conn = get_db_connection()
            conn.execute('UPDATE Users SET password = ? WHERE id = ?', (hashed_pw, session['user_id']))
            conn.commit()
            conn.close()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'success', 'message': 'Password updated successfully'})
            flash('Password updated successfully', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/api/tasks/delete-report/<int:task_id>', methods=['POST'])
@login_required
def delete_task_report(task_id):
    """Deletes a task report and removes the file from disk."""
    conn = get_db_connection()
    task = conn.execute('SELECT report_path FROM Tasks WHERE id = ?', (task_id,)).fetchone()
    
    if task and task['report_path']:
        # Remove file from disk
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], task['report_path'])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        # Update database
        conn.execute('UPDATE Tasks SET report_path = NULL WHERE id = ?', (task_id,))
        conn.commit()
    
    conn.close()
    return jsonify({'status': 'success', 'message': 'File deleted successfully'})

@app.route('/api/notifications')
@login_required
def get_notifications():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM Notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10', (session['user_id'],)).fetchall()
    unread_count = conn.execute('SELECT COUNT(*) FROM Notifications WHERE user_id = ? AND is_read = 0', (session['user_id'],)).fetchone()[0]
    conn.close()
    return jsonify({
        'notifications': [dict(row) for row in notes],
        'unread_count': unread_count
    })

@app.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    conn = get_db_connection()
    conn.execute('UPDATE Notifications SET is_read = 1 WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/jobs/<int:job_id>')
@login_required
def get_job_details(job_id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM Jobs WHERE id = ?', (job_id,)).fetchone()
    tasks = conn.execute('SELECT * FROM Tasks WHERE job_id = ?', (job_id,)).fetchall()
    conn.close()
    if job:
        return jsonify({'job': dict(job), 'tasks': [dict(t) for t in tasks]})
    return jsonify({'status': 'error', 'message': 'Job not found'}), 404

@app.route('/payments')
@login_required
def payments():
    conn = get_db_connection()
    if session['role'] == 'admin':
        # Admin can see all payments
        query = '''
            SELECT p.*, j.title as job_title, u1.username as from_user, COALESCE(u2.username, e.name) as to_user
            FROM Payments p
            LEFT JOIN Jobs j ON p.job_id = j.id
            LEFT JOIN Users u1 ON p.from_user_id = u1.id
            LEFT JOIN Users u2 ON p.to_user_id = u2.id
            LEFT JOIN Electricians e ON j.assigned_electrician_id = e.id
            ORDER BY p.created_at DESC
        '''
        payments_data = conn.execute(query).fetchall()
    else:
        # User sees payments related to them
        query = '''
            SELECT p.*, j.title as job_title, u1.username as from_user, COALESCE(u2.username, e.name) as to_user
            FROM Payments p
            LEFT JOIN Jobs j ON p.job_id = j.id
            LEFT JOIN Users u1 ON p.from_user_id = u1.id
            LEFT JOIN Users u2 ON p.to_user_id = u2.id
            LEFT JOIN Electricians e ON j.assigned_electrician_id = e.id
            WHERE p.from_user_id = ? OR p.to_user_id = ?
            ORDER BY p.created_at DESC
        '''
        payments_data = conn.execute(query, (session['user_id'], session['user_id'])).fetchall()
    conn.close()
    return render_template('payments.html', payments=payments_data)

@app.route('/api/payments/create', methods=['POST'])
@login_required
def create_payment():
    data = request.json or request.form
    job_id = data.get('job_id')
    amount = data.get('amount')
    payment_type = data.get('payment_type', 'Razorpay Demo')
    to_user_id = data.get('to_user_id') # If admin paying electrician
    
    # Simulate realistic gateway logic
    card_number = data.get('card_number', '')
    
    if not job_id or not amount:
        return jsonify({'status': 'error', 'message': 'Job ID and Amount are required.'}), 400
        
    conn = get_db_connection()
    try:
        # Simulate generating a transaction ID
        import uuid
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        # Determine status (Simulate failure for specific conditions)
        # 1. If amount is exactly 404.00, simulate failure
        # 2. If card number ends in 0000, simulate failure
        status = 'Completed'
        error_message = None
        
        try:
            amt_float = float(amount)
            if amt_float == 404.00 or card_number.endswith('0000'):
                status = 'Failed'
                error_message = "Payment declined by bank. Please try another method."
        except:
            pass

        # If admin is paying an electrician, to_user_id is provided (as an electrician ID). Else it's a client paying admin.
        if session['role'] == 'admin' and to_user_id:
            target_user = None
            el = conn.execute("SELECT email FROM Electricians WHERE id = ?", (to_user_id,)).fetchone()
            if el and el['email']:
                target_user_record = conn.execute("SELECT id FROM Users WHERE email = ?", (el['email'],)).fetchone()
                if target_user_record:
                    target_user = target_user_record['id']
        else:
            # Client to Admin flow
            admin_user = conn.execute("SELECT id FROM Users WHERE role='admin' LIMIT 1").fetchone()
            target_user = admin_user['id'] if admin_user else 1

        conn.execute('''
            INSERT INTO Payments (job_id, from_user_id, to_user_id, amount, status, transaction_id, payment_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, session['user_id'], target_user, amount, status, transaction_id, payment_type))
        conn.commit()
        
        if status == 'Completed':
            # Create notification for the receiver
            if target_user:
                conn.execute('INSERT INTO Notifications (user_id, message, type) VALUES (?, ?, ?)',
                             (target_user, f'Payment of ${amount} received for Job #{job_id}.', 'success'))
                conn.commit()
            
            return jsonify({
                'status': 'success', 
                'message': 'Payment successful', 
                'transaction_id': transaction_id
            })
        else:
            return jsonify({
                'status': 'error',
                'message': error_message or 'Payment failed at gateway.',
                'transaction_id': transaction_id
            }), 402 # Payment Required/Failed status
            
    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/payments/clear', methods=['POST'])
@login_required
def clear_payments():
    conn = get_db_connection()
    try:
        if session['role'] == 'admin':
            conn.execute('DELETE FROM Payments')
        else:
            conn.execute('DELETE FROM Payments WHERE from_user_id = ? OR to_user_id = ?', (session['user_id'], session['user_id']))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Payments cleared successfully'})
    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
