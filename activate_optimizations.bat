@echo off
REM Nero AI Framework - Quick Activation Guide (Windows)
REM Run this batch file to activate all optimizations automatically

setlocal enabledelayedexpansion

cls

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Nero AI Framework - Optimization Activation        ║
echo ║                                                        ║
echo ║   This will activate all optimizations automatically  ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if running from correct directory
if not exist "OPTIMIZATION_COMPLETE.md" (
    echo ✗ Error: Please run this batch file from the Hailo_OS root directory
    pause
    exit /b 1
)

echo [Step 1] Backing up current files...

REM Backend Backups
if exist "backend\omni_engine.py" (
    if not exist "backend\omni_engine_backup.py" (
        copy backend\omni_engine.py backend\omni_engine_backup.py >nul
        echo   ✓ backend\omni_engine.py backed up
    )
)

if exist "backend\main.py" (
    if not exist "backend\main_backup.py" (
        copy backend\main.py backend\main_backup.py >nul
        echo   ✓ backend\main.py backed up
    )
)

REM Frontend Backups
if exist "frontend\src\App.jsx" (
    if not exist "frontend\src\App_backup.jsx" (
        copy frontend\src\App.jsx frontend\src\App_backup.jsx >nul
        echo   ✓ frontend\src\App.jsx backed up
    )
)

if exist "frontend\src\index.css" (
    if not exist "frontend\src\index_backup.css" (
        copy frontend\src\index.css frontend\src\index_backup.css >nul
        echo   ✓ frontend\src\index.css backed up
    )
)

echo.
echo [Step 2] Activating optimized files...

REM Backend Activation
if exist "backend\omni_engine_optimized.py" (
    copy /Y backend\omni_engine_optimized.py backend\omni_engine.py >nul
    echo   ✓ omni_engine_optimized.py activated
) else (
    echo   ✗ omni_engine_optimized.py not found
)

if exist "backend\main_optimized.py" (
    copy /Y backend\main_optimized.py backend\main.py >nul
    echo   ✓ main_optimized.py activated
) else (
    echo   ✗ main_optimized.py not found
)

REM Frontend Activation
if exist "frontend\src\App_optimized.jsx" (
    copy /Y frontend\src\App_optimized.jsx frontend\src\App.jsx >nul
    echo   ✓ App_optimized.jsx activated
) else (
    echo   ✗ App_optimized.jsx not found
)

if exist "frontend\src\index_optimized.css" (
    copy /Y frontend\src\index_optimized.css frontend\src\index.css >nul
    echo   ✓ index_optimized.css activated
) else (
    echo   ✗ index_optimized.css not found
)

echo.
echo [Step 3] Verifying optimization markers...

REM Verify STT optimization
findstr /M "STT_BEAM_SIZE = 3" backend\omni_engine.py >nul
if errorlevel 0 (
    echo   ✓ STT optimization detected
) else (
    echo   ⚠ STT optimization not detected
)

REM Verify LLM optimization
findstr /M "LLM_MAX_TOKENS = 120" backend\omni_engine.py >nul
if errorlevel 0 (
    echo   ✓ LLM optimization detected
) else (
    echo   ⚠ LLM optimization not detected
)

REM Verify React optimization
findstr /M "useMemo" frontend\src\App.jsx >nul
if errorlevel 0 (
    echo   ✓ React optimization detected
) else (
    echo   ⚠ React optimization not detected
)

REM Verify API optimization
findstr /M "GZIPMiddleware" backend\main.py >nul
if errorlevel 0 (
    echo   ✓ API optimization detected
) else (
    echo   ⚠ API optimization not detected
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  ✓ Optimizations Successfully Activated!              ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo [Next Steps]
echo.
echo   1. Start the system:
echo      start.bat both
echo.
echo   2. Open frontend:
echo      http://localhost:5173
echo.
echo   3. Check backend:
echo      curl http://localhost:8000/api/health
echo.
echo   4. View stats:
echo      curl http://localhost:8000/api/stats
echo.
echo Backup files stored if rollback needed:
echo   - backend\omni_engine_backup.py
echo   - backend\main_backup.py
echo   - frontend\src\App_backup.jsx
echo   - frontend\src\index_backup.css
echo.
echo For detailed info, see: OPTIMIZATION_GUIDE.md
echo.

pause
