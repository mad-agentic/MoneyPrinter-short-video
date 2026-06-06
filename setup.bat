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
    echo [1/4] Tao Python virtual environment...
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
echo [2/4] Cai dat Python dependencies...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip
"%~dp0venv\Scripts\pip.exe" install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [WARNING] Co loi khi cai Python packages. Kiem tra log tren.
)
echo [3/4] Dam bao OmniVoice dependencies moi...
"%~dp0venv\Scripts\python.exe" -m pip install -U "transformers>=5.3.0" soxr
if errorlevel 1 (
    echo [WARNING] Khong the update transformers/soxr cho OmniVoice. Kiem tra log tren.
)
"%~dp0venv\Scripts\python.exe" -c "import transformers; from transformers import HiggsAudioV2TokenizerModel; from omnivoice import OmniVoice; print('[OK] OmniVoice deps ready: transformers ' + transformers.__version__)"
if errorlevel 1 (
    echo [WARNING] OmniVoice import check failed. TTS engine omnivoice co the khong chay.
)
echo [OK] Python packages da cai xong.

REM == Cai npm packages ==
echo [4/4] Cai dat npm dependencies cho frontend...
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
