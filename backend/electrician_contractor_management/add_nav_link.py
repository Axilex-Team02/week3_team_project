import glob
import os

files = glob.glob(r"e:\final_team_project\backend\electrician_contractor_management\templates\*.html")

link_to_insert = """                <a href="/payments" class="sidebar-link">
                    <i class="fa-solid fa-credit-card"></i> Payments
                </a>
"""

for path in files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if '<a href="/payments"' in content:
        continue
        
    # Insert after reporter link if it exists, otherwise after tasks
    if 'href="/reporter"' in content:
        content = content.replace(
            '<a href="/reporter" class="sidebar-link">\n                    <i class="fa-solid fa-file-contract"></i> Reports\n                </a>',
            '<a href="/reporter" class="sidebar-link">\n                    <i class="fa-solid fa-file-contract"></i> Reports\n                </a>\n' + link_to_insert
        )
    elif 'href="/tasks"' in content:
        content = content.replace(
            '<a href="/tasks" class="sidebar-link">\n                    <i class="fa-solid fa-list-check"></i> Tasks\n                </a>',
            '<a href="/tasks" class="sidebar-link">\n                    <i class="fa-solid fa-list-check"></i> Tasks\n                </a>\n' + link_to_insert
        )
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Updated nav links.")
