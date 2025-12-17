@echo off
echo ============================================
echo   Deepfake Detection Web Interface
echo ============================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================
echo Starting Flask application...
echo ============================================
echo.
echo Opening http://localhost:5000 in browser...
echo.

python app.py

pause
