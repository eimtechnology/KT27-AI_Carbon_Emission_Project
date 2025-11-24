@echo off
setlocal

echo ===================================================
echo Food Carbon Emission Detection System Launcher
echo ===================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

REM Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
if exist "requirements.txt" (
    echo Checking dependencies...
    pip install -r requirements.txt >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installing dependencies...
        pip install -r requirements.txt
    )
) else (
    echo Warning: requirements.txt not found!
)

REM Run application
echo Starting application...
python gui_main.py

if %errorlevel% neq 0 (
    echo Application crashed with error code %errorlevel%
    pause
)

deactivate
endlocal