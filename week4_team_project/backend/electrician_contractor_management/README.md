- **Backend Setup**: Flask web framework implemented with modern routing and API endpoints.
- **Database**: SQLite database (`contractor.db`) structured with Users, Electricians, Jobs, Tasks, and Notifications.
- **User Authentication**: Secure user registration and login functionality using Werkzeug password hashing.
- **Advanced Reporting**: Data-driven analytics dashboard with real-time charts powered by Chart.js.
- **Search & Filter**: AJAX-ready search and multi-parameter filtering for electricians, jobs, and tasks.
- **Notification System**: Real-time alerts for task assignments, completions, and deadline warnings.
- **Premium UI/UX**: Professional "Glassmorphism" interface with custom HSL color palettes and Inter typography.

## How to Run the Project
1. **Activate the Virtual Environment**:
   ```bash
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```
2. **Install Dependencies** (if not already installed):
   ```bash
   pip install flask
   ```
3. **Run the Database Initialization** (if restoring or resetting data):
   ```bash
   python database_setup.py
   ```
4. **Start the Flask Server**:
   ```bash
   python app.py
   ```
5. **Open in Browser**:
   Open a web browser and go to `http://127.0.0.1:5000/`.

- [x] Backend Integration (Flask)
- [x] Database Connected (contractor.db)
- [x] Working Login and Registration
- [x] Dynamic Dashboard (Fetching live stats)
- [x] Reports Module (Chart.js visualization)
- [x] Real-time Notifications system
- [x] Search & Filter Functionality
- [x] Premium CSS/UX Overhaul
- [x] Code ready for GitHub push

## Pushing to GitHub
To push this project to your GitHub account:
1. Go to [GitHub](https://github.com/) and create a new repository (e.g., `electrician-contractor-management`).
2. Open your terminal in this project directory.
3. Add the remote origin and push the main branch:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/electrician-contractor-management.git
   git branch -M main
   git push -u origin main
   ```
