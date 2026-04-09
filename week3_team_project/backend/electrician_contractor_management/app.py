from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contractor.db')

app = Flask(__name__)
app.secret_key = 'electrician_secret_key' # In production, use a secure random key

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone')
        role = request.form.get('role', 'admin')
        
        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        # To ensure the registration "takes successfully" as requested, 
        # we delete any existing users that conflict with this username or email
        # and then insert the new record. This is a robust "upsert" for a simple CMS.
        conn.execute('DELETE FROM Users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)', (username, email))
        
        conn.execute('INSERT INTO Users (username, email, password, phone, role) VALUES (?, ?, ?, ?, ?)',
                     (username, email, hashed_pw, phone, role))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
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
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    electricians_count = conn.execute('SELECT COUNT(*) FROM Electricians').fetchone()[0]
    jobs_count = conn.execute('SELECT COUNT(*) FROM Jobs').fetchone()[0]
    tasks_count = conn.execute('SELECT COUNT(*) FROM Tasks').fetchone()[0]
    
    # Fetch data for dashboard summary and cards
    recent_jobs = conn.execute('''
        SELECT Jobs.*, Electricians.name as electrician_name 
        FROM Jobs 
        LEFT JOIN Electricians ON Jobs.assigned_electrician_id = Electricians.id
        ORDER BY Jobs.id DESC LIMIT 5
    ''').fetchall()
    
    low_stock_materials = conn.execute('SELECT * FROM Materials WHERE quantity < 10').fetchall()
    recent_electricians = conn.execute('SELECT * FROM Electricians ORDER BY id DESC LIMIT 5').fetchall()
    
    # Fetch ALL electricians and jobs for modals
    all_electricians = conn.execute('SELECT * FROM Electricians ORDER BY name ASC').fetchall()
    all_jobs = conn.execute('SELECT * FROM Jobs ORDER BY title ASC').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                          electricians_count=electricians_count,
                          jobs_count=jobs_count,
                          tasks_count=tasks_count,
                          recent_jobs=recent_jobs,
                          low_stock_materials=low_stock_materials,
                          recent_electricians=recent_electricians,
                          all_electricians=all_electricians,
                          all_jobs=all_jobs)

@app.route('/electricians', methods=['GET', 'POST'])
def electricians():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        if name:
            conn.execute('INSERT INTO Electricians (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
            conn.commit()
            flash('Electrician added successfully!', 'success')
        
        # Smart redirect: if AJAX or from dashboard, handle appropriately
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Electrician added successfully'}
        return redirect(request.referrer or url_for('electricians'))

    electricians = conn.execute('SELECT * FROM Electricians').fetchall()
    conn.close()
    return render_template('electricians.html', electricians=electricians)

@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        deadline = request.form.get('deadline')
        assignee_id = request.form.get('assignee_id')
        if title:
            conn.execute('INSERT INTO Jobs (title, description, location, deadline, assigned_electrician_id) VALUES (?, ?, ?, ?, ?)', 
                         (title, description, location, deadline, assignee_id if assignee_id != 'None' else None))
            conn.commit()
            flash('Job created successfully!', 'success')
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Job created successfully'}
        return redirect(request.referrer or url_for('jobs'))

    jobs = conn.execute('''
        SELECT Jobs.*, Electricians.name as electrician_name 
        FROM Jobs 
        LEFT JOIN Electricians ON Jobs.assigned_electrician_id = Electricians.id
    ''').fetchall()
    electricians = conn.execute('SELECT id, name FROM Electricians').fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs, electricians=electricians)

@app.route('/electricians/update/<int:id>', methods=['POST'])
def update_electrician(id):
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Unauthorized'}, 401
    
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    status = request.form.get('status', 'Available')
    
    conn = get_db_connection()
    conn.execute('UPDATE Electricians SET name = ?, email = ?, phone = ?, status = ? WHERE id = ?',
                 (name, email, phone, status, id))
    conn.commit()
    conn.close()
    return {'status': 'success', 'message': 'Electrician updated successfully'}

@app.route('/electricians/delete/<int:id>', methods=['POST'])
def delete_electrician(id):
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Unauthorized'}, 401
    
    conn = get_db_connection()
    conn.execute('DELETE FROM Electricians WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return {'status': 'success', 'message': 'Electrician deleted successfully'}

@app.route('/materials', methods=['GET', 'POST'])
def materials():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        if name:
            conn.execute('INSERT INTO Materials (name, quantity, unit) VALUES (?, ?, ?)', (name, quantity, unit))
            conn.commit()
            flash('Material added successfully!', 'success')
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Material added successfully'}
        return redirect(request.referrer or url_for('materials'))

    materials = conn.execute('SELECT * FROM Materials').fetchall()
    conn.close()
    return render_template('materials.html', materials=materials)

@app.route('/materials/update_usage/<int:id>', methods=['POST'])
def update_material_usage(id):
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Unauthorized'}, 401
    
    usage = request.form.get('usage', 0)
    try:
        usage = int(usage)
    except ValueError:
        return {'status': 'error', 'message': 'Invalid usage amount'}, 400
        
    conn = get_db_connection()
    material = conn.execute('SELECT * FROM Materials WHERE id = ?', (id,)).fetchone()
    if material and material['quantity'] >= usage:
        new_quantity = material['quantity'] - usage
        import datetime
        last_usage = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute('UPDATE Materials SET quantity = ?, last_usage = ? WHERE id = ?',
                     (new_quantity, last_usage, id))
        conn.commit()
        conn.close()
        return {'status': 'success', 'message': f'Logged usage of {usage} {material["unit"]}'}
    else:
        conn.close()
        return {'status': 'error', 'message': 'Insufficient quantity'}, 400

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        job_id = request.form.get('job_id')
        description = request.form.get('description')
        assignee_id = request.form.get('assignee_id')
        if job_id and description:
            conn.execute('INSERT INTO Tasks (job_id, description, assigned_electrician_id, status) VALUES (?, ?, ?, ?)', 
                         (job_id, description, assignee_id if assignee_id != 'None' else None, 'Pending'))
            conn.commit()
            flash('Task added successfully!', 'success')
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'status': 'success', 'message': 'Task added successfully'}
        return redirect(request.referrer or url_for('tasks'))

    status_filter = request.args.get('status')
    query = '''
        SELECT Tasks.*, Jobs.title as job_title, Electricians.name as electrician_name 
        FROM Tasks 
        JOIN Jobs ON Tasks.job_id = Jobs.id
        LEFT JOIN Electricians ON Tasks.assigned_electrician_id = Electricians.id
    '''
    params = []
    if status_filter:
        query += ' WHERE Tasks.status = ?'
        params.append(status_filter)
        
    tasks = conn.execute(query, params).fetchall()
    jobs = conn.execute('SELECT id, title FROM Jobs').fetchall()
    electricians = conn.execute('SELECT id, name FROM Electricians').fetchall()
    conn.close()
    return render_template('tasks.html', tasks=tasks, jobs=jobs, electricians=electricians)

@app.route('/tasks/update_status/<int:id>', methods=['POST'])
def update_task_status(id):
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Unauthorized'}, 401
    
    new_status = request.form.get('status')
    if new_status not in ['Pending', 'In Progress', 'Completed']:
        return {'status': 'error', 'message': 'Invalid status'}, 400
        
    conn = get_db_connection()
    conn.execute('UPDATE Tasks SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    return {'status': 'success', 'message': f'Task status updated to {new_status}'}

@app.route('/reporter')
def reporter():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('reporter.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
