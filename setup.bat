@echo off
REM Illuminate Setup Script for Windows
REM Run as Administrator for best results

echo ========================================
echo   Illuminate Setup - Windows
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found! Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [+] Python found
python --version

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] pip not found! Please reinstall Python with pip
    pause
    exit /b 1
)

echo [+] pip found
echo.

REM Upgrade pip
echo [+] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install Python packages
echo [+] Installing Python packages...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [X] Failed to install some packages
    echo     Try running as Administrator
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Configure your .env file with API keys
echo   2. Test TTS: python modules\tts.py
echo   3. Run program: python main.py
echo.
pause
