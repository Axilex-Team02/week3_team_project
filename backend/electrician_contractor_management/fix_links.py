import glob
import os

files = glob.glob('templates/*.html')

replacements = {
    'href="css/': 'href="/static/css/',
    'src="js/': 'src="/static/js/',
    'href="dashboard.html"': 'href="/dashboard"',
    'href="index.html"': 'href="/"',
    'href="login.html"': 'href="/login"',
    'href="register.html"': 'href="/register"',
    'href="electricians.html"': 'href="/electricians"',
    'href="jobs.html"': 'href="/jobs"',
    'href="tasks.html"': 'href="/tasks"',
    'href="materials.html"': 'href="/materials"',
    'href="reporter.html"': 'href="/reporter"',
    'href="profile.html"': 'href="/profile"'
}

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print(f"Fixed links in {len(files)} files.")
