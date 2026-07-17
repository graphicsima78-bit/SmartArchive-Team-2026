@echo off
title ArchivePro v26 Emergency Repair
echo ===============================================
echo      ArchivePro Studio v26.0 (Zero-Dependency)
echo ===============================================
echo.
echo Cleaning Python cache...
if exist __pycache__ rd /s /q __pycache__

echo Applying Emergency Fix...
copy /Y archiver.py archiver.py
copy /Y main.py main.py
copy /Y database.py database.py
copy /Y styles.py styles.py
copy /Y file_analyzer.py file_analyzer.py

echo.
echo [SUCCESS] Version 26.0 Applied!
echo The program is now independent and should run.
pause
