@echo off
title aiVideoGen v3.0.0
set PYTHONUTF8=1
echo.
echo ================================================
echo    aiVideoGen v3.0.0
echo ================================================
echo.
echo Iniciando servidor local en puerto 8888...
echo Una vez iniciado, la aplicacion se abrira automaticamente.
echo.
echo IMPORTANTE: NO cierres esta ventana mientras uses la app
echo Para detener el servidor: presiona Ctrl+C
echo.
echo ================================================
echo.

if exist "C:\Program Files\Python312\python.exe" (
    "C:\Program Files\Python312\python.exe" run_app.py
) else (
    python run_app.py
)
