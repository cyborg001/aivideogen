@echo off
echo =======================================================
echo      AIVideogen - LANZADOR DE EMERGENCIA (v5.6)
echo =======================================================
cd /d "%~dp0"
if exist venv\Scripts\activate.bat (
    echo [System] Activando entorno virtual...
    call venv\Scripts\activate.bat
)
cd aivideogen
python run_app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [System] El servidor ha detectado un error critico.
    pause
)
