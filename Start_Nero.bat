@echo off
echo ===================================================
echo             Starte Nero AI Framework...
echo ===================================================
echo.

:: 1. Starte das Backend (dies lädt auch die Modelle herunter, falls nötig)
echo [1/3] Starte das Python Backend...
start "Nero Backend" cmd /k "conda activate Hailo_env && cd /d %~dp0backend && uvicorn main:app"

:: 2. Starte das Frontend
echo [2/3] Starte das React Frontend...
start "Nero Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: 3. Warte kurz, damit die Server hochfahren können
echo [3/3] Warte kurz auf die Server-Initialisierung...
timeout /t 5 /nobreak >nul

:: 4. Öffne den Browser
echo Oeffne Nero im Browser...
start http://localhost:5173

echo.
echo ===================================================
echo Nero ist jetzt aktiv! 
echo Du kannst diese Kommandozeile nun schliessen.
echo ===================================================
timeout /t 3 >nul
exit
