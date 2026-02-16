@echo off
chcp 65001 >nul
title Tesseract OCR Setup

echo ========================================
echo    Tesseract OCR Setup for Windows
echo ========================================
echo.

:: Check if Tesseract is already installed
where tesseract >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Tesseract already installed!
    tesseract --version
    goto :download_russian
)

:: Download installer
echo [1/5] Downloading Tesseract...
set "TESSERACT_URL=https://github.com/UB-Mannheim/tesseract/releases/download/v5.5.0.20241111/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
set "INSTALLER=%TEMP%\tesseract-installer.exe"

powershell -Command "Invoke-WebRequest -Uri '%TESSERACT_URL%' -OutFile '%INSTALLER%'"

if not exist "%INSTALLER%" (
    echo [ERROR] Download failed!
    echo Please download manually:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

:: Run installer
echo [2/5] Running installer...
echo IMPORTANT: Select "Language data" component during installation!
echo (Required for Russian language)
echo.
echo Press any key to continue...
pause >nul

start /wait "" "%INSTALLER%"

:: Add to PATH
echo [3/5] Adding to PATH...
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR" /M >nul 2>&1

:: Cleanup
echo [4/5] Cleaning up...
del "%INSTALLER%" 2>nul

:download_russian
:: Download Russian language
echo [5/5] Downloading Russian language...
set "RUSSIAN_URL=https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata"
set "TESSDATA_DIR=C:\Program Files\Tesseract-OCR\tessdata"

if not exist "%TESSDATA_DIR%" (
    mkdir "%TESSDATA_DIR%"
)

echo Downloading rus.traineddata...
powershell -Command "Invoke-WebRequest -Uri '%RUSSIAN_URL%' -OutFile '%TESSDATA_DIR%\rus.traineddata'"

if exist "%TESSDATA_DIR%\rus.traineddata" (
    echo [OK] Russian language downloaded successfully!
) else (
    echo [ERROR] Failed to download Russian language!
    echo Download manually:
    echo https://github.com/tesseract-ocr/tessdata/blob/main/rus.traineddata
    echo Copy to: %TESSDATA_DIR%
)

:: Check installed languages
echo.
echo Installed languages:
tesseract --list-langs

echo.
echo [OK] Setup complete!
pause