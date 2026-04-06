@echo off
title MoneyPrinter Short Video - Setup
color 0A
setlocal EnableDelayedExpansion

echo ===================================================
echo     SETUP: MoneyPrinter Short Video
echo ===================================================
echo.

REM == Kiem tra Python ==
python --version >/dev/null 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat hoac khong co trong PATH!
    echo Tai Python tai: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python da san sang.

REM == Kiem tra Node.js ==
node --version >/dev/null 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js chua duoc cai dat!
    echo Tai Node.js tai: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js da san sang.

REM == Tao venv ==
if not exist "%~dp0venv" (
    echo [1/3] Tao Python virtual environment...
    python -m venv "%~dp0venv"
    if errorlevel 1 (
        echo [ERROR] Khong the tao venv!
        pause
        exit /b 1
    )
    echo [OK] venv da duoc tao.
) else (
    echo [SKIP] venv da ton tai.
)

REM == Cai Python packages ==
echo [2/3] Cai dat Python dependencies...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip
"%~dp0venv\Scripts\pip.exe" install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [WARNING] Co loi khi cai Python packages. Kiem tra log tren.
)
echo [OK] Python packages da cai xong.

REM == Cai npm packages ==
echo [3/3] Cai dat npm dependencies cho frontend...
cd /d "%~dp0frontend"
npm install
if errorlevel 1 (
    echo [ERROR] Khong the cai npm packages!
    pause
    exit /b 1
)
cd /d "%~dp0"
echo [OK] npm packages da cai xong.

echo.
echo ===================================================
echo  Setup hoan tat! Bay gio ban co the chay:
echo  =^> start_hub.bat
echo ===================================================
echo.
pause
