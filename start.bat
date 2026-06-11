@echo off
REM Nero AI Framework - Start Script (Windows)
REM Usage: start.bat [backend|frontend|both]

setlocal enabledelayedexpansion

set MODE=%1
if "%MODE%"=="" set MODE=both

title Nero AI Framework

echo.
echo ===============================================
echo   Nero AI Framework - Windows Starter
echo ===============================================
echo.

goto %MODE%

:backend
echo Starting Backend Service...
cd backend
echo.
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.
    pause
    exit /b 1
)

echo Creating directories...
if not exist temp mkdir temp
if not exist logs mkdir logs

echo Activating optimized backend files...
if exist omni_engine_optimized.py (
    copy /Y omni_engine_optimized.py omni_engine.py >nul
    copy /Y main_optimized.py main.py >nul
    echo Optimized files activated.
)

echo Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

echo.
echo ===============================================
echo   Starting Uvicorn Server...
echo ===============================================
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info
goto end

:frontend
echo Starting Frontend Service...
cd frontend
echo.
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js.
    pause
    exit /b 1
)

echo Activating optimized frontend files...
if exist src\App_optimized.jsx (
    copy /Y src\App_optimized.jsx src\App.jsx >nul
    copy /Y src\index_optimized.css src\index.css >nul
    echo Optimized files activated.
)

echo Checking dependencies...
if not exist node_modules (
    echo Installing Node dependencies...
    call npm install
)

echo.
echo ===============================================
echo   Starting Vite Dev Server...
echo ===============================================
echo.
call npm run dev
goto end

:both
echo Starting Nero AI Framework (Backend + Frontend)...
echo.

REM Create logs directory
if not exist logs mkdir logs

REM Start Backend
echo Starting Backend in background...
cd backend
if not exist temp mkdir temp
if not exist ..\logs mkdir ..\logs
if exist omni_engine_optimized.py (
    copy /Y omni_engine_optimized.py omni_engine.py >nul
    copy /Y main_optimized.py main.py >nul
)

REM Check dependencies
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install -r requirements.txt
)

start "Nero Backend" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info"
timeout /t 5 /nobreak

REM Check backend
echo Checking backend health...
for /l %%i in (1,1,10) do (
    powershell -Command "(New-Object System.Net.WebClient).DownloadString('http://localhost:8000/api/health')" >nul 2>&1
    if errorlevel 0 goto backend_ok
    timeout /t 1 /nobreak
)
echo WARNING: Backend may not be ready

:backend_ok
cd ..\frontend

echo Starting Frontend in background...
if exist src\App_optimized.jsx (
    copy /Y src\App_optimized.jsx src\App.jsx >nul
    copy /Y src\index_optimized.css src\index.css >nul
)

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

start "Nero Frontend" cmd /k "npm run dev"

echo.
echo ===============================================
echo   Nero AI Framework Running!
echo ===============================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo.
echo Close the backend/frontend windows to stop services.
echo.
pause
goto end

:end
endlocal
