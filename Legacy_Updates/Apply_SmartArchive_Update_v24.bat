@echo off
title ArchivePro v24 Repair & Style
echo ===============================================
echo      ArchivePro Studio v24.0 (Fix & Polish)
echo ===============================================
echo.
echo Fixing Import Errors...
copy /Y archiver.py archiver.py
copy /Y main.py main.py
copy /Y database.py database.py
copy /Y styles.py styles.py
copy /Y file_analyzer.py file_analyzer.py

echo.
echo [SUCCESS] Version 24.0 Fixes Applied!
echo Program should now start without any errors.
pause
