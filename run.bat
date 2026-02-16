@echo off
chcp 65001 >nul
title AutoClickerCtS

echo ========================================
echo    Запуск AutoClickerCtS
echo ========================================
echo.

:: Проверка наличия виртуального окружения
if not exist venv\Scripts\activate (
    echo [1/3] Создание виртуального окружения...
    python -m venv venv
)

:: Активация виртуального окружения
echo [2/3] Активация окружения...
call venv\Scripts\activate.bat

:: Проверка и установка зависимостей
echo [3/3] Проверка зависимостей...
pip install -q -r requirements.txt

:: Запуск программы
echo.
echo Запуск программы...
echo.
python main.py

pause