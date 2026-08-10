@echo off
REM Pokretac za Windows
setlocal
cd /d "%~dp0"

py -3 -c "import customtkinter, cryptography" >nul 2>&1
if errorlevel 1 (
    echo Instaliram potrebne biblioteke...
    py -3 -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Instalacija nije uspjela. Provjerite da su Python i internet dostupni.
        pause
        exit /b 1
    )
)

py -3 app.py
if errorlevel 1 pause
