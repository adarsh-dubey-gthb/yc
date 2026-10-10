@echo off
title YouTube MP3 Studio
echo ========================================================
echo       Launching YouTube MP3 Studio (Streamlit)
echo ========================================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python -m streamlit run app.py
) else (
    where streamlit >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        streamlit run app.py
    ) else (
        python -m streamlit run app.py
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Could not start the app.
    echo If this is your first time, please run setup.bat first!
    echo.
    pause
)
