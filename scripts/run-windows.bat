@echo off
REM Run VideoWall from Compiled Binary - Windows
REM Launches the compiled application from dist folder

setlocal enabledelayedexpansion

REM Configuration
set APP_NAME=VideoWall

REM Get the script directory
cd /d "%~dp0\.."

REM Colors for output (Windows 10+)
echo [94m[%TIME:~0,8%][0m Launching compiled VideoWall application...

REM Check if dist directory exists
if not exist "dist" (
    echo [91m[%TIME:~0,8%] X[0m No dist/ directory found. Please run compile-build-dist.sh first.
    pause
    exit /b 1
)

REM Look for Windows binary
set BINARY_PATH=
if exist "dist\windows\%APP_NAME%.exe" (
    set BINARY_PATH=dist\windows\%APP_NAME%.exe
    echo [92m[%TIME:~0,8%] v[0m Found Windows executable
)

REM Launch the application if found
if defined BINARY_PATH (
    echo [92m[%TIME:~0,8%] v[0m Launching %APP_NAME%...
    start "" "!BINARY_PATH!"
    echo [92m[%TIME:~0,8%] v[0m Application launched successfully!
    echo [96m[%TIME:~0,8%] i[0m The app is now running. Check your taskbar to interact with it.
) else (
    echo [91m[%TIME:~0,8%] X[0m Could not find %APP_NAME% binary in dist/ directory
    echo [96m[%TIME:~0,8%] i[0m To build the app first, run:
    echo   compile-build-dist.sh
    echo.
    echo [96m[%TIME:~0,8%] i[0m To run from source instead:
    echo   run-windows-source.bat
    pause
    exit /b 1
)

endlocal