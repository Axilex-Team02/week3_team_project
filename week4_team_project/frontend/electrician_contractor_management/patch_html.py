import glob
import os

# Rename reports.html to reporter.html
reports_path = "d:/bhoomi/team_project/electrician_contractor_management/reports.html"
reporter_path = "d:/bhoomi/team_project/electrician_contractor_management/reporter.html"

if os.path.exists(reports_path):
    os.rename(reports_path, reporter_path)

files = glob.glob("d:/bhoomi/team_project/electrician_contractor_management/*.html")
for path in files:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    # Replace reports.html with reporter.html
    src = src.replace('"reports.html"', '"reporter.html"')

    # Fix sidebar header
    old_aside = '<div class="sidebar-header">\n                <i class="fa-solid fa-bolt" style="margin-right: 0.5rem;"></i> AXILEX\n            </div>'
    new_aside = '<div class="sidebar-header" style="justify-content: space-between;">\n                <div><i class="fa-solid fa-bolt" style="margin-right: 0.5rem;"></i> AXILEX</div>\n                <button id="close-sidebar-btn" style="background:none; border:none; color:white; font-size:1.25rem; cursor:pointer;" class="mobile-only"><i class="fa-solid fa-xmark"></i></button>\n            </div>'
    src = src.replace(old_aside, new_aside)

    with open(path, "w", encoding="utf-8") as f:
        f.write(src)

print("Batch HTML modifications completed.")
