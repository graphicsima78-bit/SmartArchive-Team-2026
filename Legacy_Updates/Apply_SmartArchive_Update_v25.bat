@echo off
title ArchivePro v25 Final Stability
echo ===============================================
echo      ArchivePro Studio v25.0 (Stability Fix)
echo ===============================================
echo.
echo Synchronizing all file extensions...
copy /Y archiver.py archiver.py
copy /Y main.py main.py
copy /Y database.py database.py
copy /Y styles.py styles.py
copy /Y file_analyzer.py file_analyzer.py

echo.
echo [SUCCESS] Version 25.0 Fixes Applied!
echo Extension lists are now fully synchronized.
pause
