@echo off
title MoneyPrinter Short Video - Web Hub Launcher
color 0B
setlocal EnableDelayedExpansion

echo ===================================================
echo     STARTING MoneyPrinter Short Video WEB HUB
echo ===================================================
echo.

REM == Kiem tra venv ==
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] Chua co virtual environment!
    echo Hay chay setup.bat truoc de cai dat.
    pause
    exit /b 1
)

REM == Kiem tra node_modules ==
if not exist "%~dp0frontend\node_modules" (
    echo [SETUP] Dang cai dat npm packages cho frontend...
    cd /d "%~dp0frontend"
    npm install
    cd /d "%~dp0"
)

call :free_port 15001 "Backend API"
call :free_port 5174 "Frontend UI"
echo.

echo [1/2] Khoi dong FastAPI Backend (Port 15001)...
start "MoneyPrinter Backend API (Port 15001)" cmd /k "cd /d %~dp0src && ..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload"

timeout /t 2 /nobreak ^>nul

echo [2/2] Khoi dong React Frontend (Port 5174)...
start "MoneyPrinter Frontend UI (Port 5174)" cmd /k "cd /d %~dp0frontend && npm run dev -- --port 5174"

echo.
echo ===================================================
echo Mọi service da duoc khoi chay trong 2 cua so moi!
echo (Vui long khong tat 2 cua so mau den dang chay)
echo.
echo Hay truy cap duong link sau tren trinh duyet:
echo =^> http://localhost:5174
echo ===================================================
echo.
pause
goto :eof

:free_port
set "PORT=%~1"
set "LABEL=%~2"
set "FOUND_PID="

for /f %%P in ('powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %PORT% -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"') do (
	set "FOUND_PID=1"
	echo [PRECHECK] Port %PORT% dang duoc !LABEL! hoac process khac su dung. Killing PID %%P...
	taskkill /F /PID %%P >nul 2>&1
)

if not defined FOUND_PID (
	echo [PRECHECK] Port %PORT% dang trong.
)

exit /b 0
