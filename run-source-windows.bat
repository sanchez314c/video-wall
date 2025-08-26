@echo off
setlocal enabledelayedexpansion

REM Run VideoWall from Source on Windows
REM PyQt5 multi-display video wall application

set CYAN=[96m
set GREEN=[92m
set RED=[91m
set NC=[0m

echo %CYAN%[%TIME%]%NC% Starting VideoWall from source (Windows)...

REM Navigate to script directory
cd /d "%~dp0"

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[%TIME%] Python is not installed. Download from https://python.org%NC%
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo %CYAN%[%TIME%]%NC% Using %PYTHON_VER%

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo %CYAN%[%TIME%]%NC% Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    REM Check for PyQt5 in system Python
    python -c "import PyQt5" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo %CYAN%[%TIME%]%NC% Installing dependencies...
        python -m pip install -r requirements.txt
        if %ERRORLEVEL% NEQ 0 (
            echo %RED%[%TIME%] Failed to install dependencies%NC%
            pause
            exit /b 1
        )
    )
)

REM Run the application
echo %GREEN%[%TIME%]%NC% Launching VideoWall...
python -m src %*

set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% EQU 0 (
    echo %GREEN%[%TIME%] VideoWall session ended%NC%
) else (
    echo %RED%[%TIME%] VideoWall exited with code %EXIT_CODE%%NC%
)

pause
exit /b %EXIT_CODE%
