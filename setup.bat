@echo off
title YouTube MP3 Downloader - Setup
echo ========================================================
echo       YouTube MP3 Downloader - Setup Wizard
echo ========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check the box "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Python detected:
python --version
echo.

echo [2/3] Creating virtual environment (.venv)...
if not exist ".venv" (
    python -m venv .venv
    echo Virtual environment created.
) else (
    echo Existing virtual environment detected.
)
echo.

echo [3/3] Installing and updating dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================================
echo       Setup Completed Successfully!
echo ========================================================
echo You can now run the app anytime by double-clicking:
echo   run.bat
echo.
pause
