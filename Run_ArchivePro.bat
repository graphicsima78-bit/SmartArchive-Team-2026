@echo off
setlocal
cd /d "%~dp0"
title ArchivePro Studio
python main.py
if errorlevel 1 (
    echo.
    echo ArchivePro could not start. Read the error above.
    pause
)
endlocal
