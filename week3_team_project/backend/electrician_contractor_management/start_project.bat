@echo off
echo ========================================================
echo Starting Electrician Contractor Management System...
echo ========================================================
echo.

cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please ensure the 'venv' folder exists.
    pause
    exit /b
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Flask server...
echo The website will open automatically in your browser!
echo.
echo (Do not close this window while using the application)
echo.

timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000/

python app.py

pause
