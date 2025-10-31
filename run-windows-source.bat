@echo off
REM Run VideoWall from Source - Windows
REM Launches the app directly from source code

setlocal enabledelayedexpansion

REM Configuration
set MAIN_SCRIPT=src\main.py

REM Get the script directory
cd /d "%~dp0\.."

REM Colors for output (Windows 10+)
echo [94m[%TIME:~0,8%][0m Starting VideoWall from source...

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where python3 >nul 2>nul
    if %errorlevel% neq 0 (
        echo [91m[%TIME:~0,8%] X[0m Python 3 is not installed. Please install Python 3.8 or higher.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

REM Check if main script exists
if not exist "%MAIN_SCRIPT%" (
    echo [91m[%TIME:~0,8%] X[0m %MAIN_SCRIPT% not found. Make sure you're in the project root directory.
    pause
    exit /b 1
)

REM Create venv if it doesn't exist
if not exist "venv" (
    echo [94m[%TIME:~0,8%][0m Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [91m[%TIME:~0,8%] X[0m Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [92m[%TIME:~0,8%] v[0m Virtual environment created
)

REM Activate virtual environment
echo [94m[%TIME:~0,8%][0m Activating virtual environment...
call venv\Scripts\activate.bat
echo [92m[%TIME:~0,8%] v[0m Virtual environment activated

REM Install dependencies if needed
if exist "requirements.txt" (
    REM Check if dependencies are installed
    pip show tkinter >nul 2>nul
    if %errorlevel% neq 0 (
        echo [94m[%TIME:~0,8%][0m Installing dependencies...
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo [91m[%TIME:~0,8%] X[0m Failed to install dependencies
            pause
            exit /b 1
        )
        echo [92m[%TIME:~0,8%] v[0m Dependencies installed
    ) else (
        echo [96m[%TIME:~0,8%] i[0m Dependencies already installed
    )
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [96m[%TIME:~0,8%] i[0m Python version: %PYTHON_VERSION%

REM Launch the application
echo [94m[%TIME:~0,8%][0m Launching VideoWall from source code...
echo [96m[%TIME:~0,8%] i[0m Press Ctrl+C to stop the application
echo.

REM Run the Python application
python "%MAIN_SCRIPT%"

REM Check exit code
if %errorlevel% equ 0 (
    echo [92m[%TIME:~0,8%] v[0m Application terminated successfully
) else (
    echo [91m[%TIME:~0,8%] X[0m Application terminated with error code: %errorlevel%
)

REM Deactivate virtual environment
call deactivate
echo [96m[%TIME:~0,8%] i[0m Virtual environment deactivated

pause
endlocal