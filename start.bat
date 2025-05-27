@echo off
echo Starting ICI Chat Application...
echo.

:: Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found at .venv
    echo Please create a virtual environment first
    pause
    exit /b 1
)

:: Kill any existing processes on port 8080
echo Checking for existing processes on port 8080...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo Killing process %%i on port 8080...
    taskkill /F /PID %%i >nul 2>&1
)

:: Wait a moment for cleanup
timeout /t 2 >nul

:: Start the application
echo Starting the refactored ICI Chat application...
.venv\Scripts\python.exe app.py

pause
