@echo off
chcp 65001 >nul
title AutoClicker

echo ================================
echo    AutoClickerCtS Launcher
echo ================================
echo.

:: Check for virtual environment
if not exist venv\Scripts\activate (
    echo [1/4] Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo [2/4] Activating environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo [4/4] Installing dependencies...
pip install -r requirements.txt

:: Run the program
echo.
echo Starting program...
echo.
python main.py

pause