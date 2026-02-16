@echo off
chcp 65001 >nul
title Установка Tesseract OCR

echo ========================================
echo    Установка Tesseract OCR для Windows
echo ========================================
echo.

:: Проверка, установлен ли уже Tesseract
where tesseract >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Tesseract уже установлен!
    tesseract --version
    goto :check_langs
)

:: Скачивание установщика
echo [1/4] Скачивание Tesseract...
set "TESSERACT_URL=https://github.com/UB-Mannheim/tesseract/releases/download/v5.5.0.20241111/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
set "INSTALLER=%TEMP%\tesseract-installer.exe"

powershell -Command "Invoke-WebRequest -Uri '%TESSERACT_URL%' -OutFile '%INSTALLER%'"

if not exist "%INSTALLER%" (
    echo ❌ Ошибка скачивания!
    echo Пожалуйста, скачайте вручную:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

:: Запуск установщика
echo [2/4] Запуск установщика...
echo ⚠️ ВНИМАНИЕ: При установке выберите компонент "Language data"!
echo    (нужен для русского языка)
echo.
echo Нажмите любую клавишу для продолжения...
pause >nul

start /wait "" "%INSTALLER%"

:: Добавление в PATH
echo [3/4] Добавление в PATH...
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR" /M >nul 2>&1

:: Очистка
echo [4/4] Очистка временных файлов...
del "%INSTALLER%" 2>nul

:check_langs
:: Проверка языков
echo.
echo Проверка установленных языков...
tesseract --list-langs

echo.
echo ✅ Установка завершена!
echo.
echo Если русский язык (rus) отсутствует в списке,
echo скачайте файл вручную:
echo https://github.com/tesseract-ocr/tessdata/blob/main/rus.traineddata
echo и поместите в C:\Program Files\Tesseract-OCR\tessdata\
echo.
pause