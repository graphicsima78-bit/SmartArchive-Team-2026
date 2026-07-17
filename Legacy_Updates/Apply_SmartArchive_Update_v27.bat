@echo off
title ArchivePro v27 Compact Updater
echo ===============================================
echo      ArchivePro Studio v27.0 (Compact UI)
echo ===============================================
echo.
echo Installing updates from current folder...

:: استفاده از مسیر فعلی برای جلوگیری از خطای "File not found"
set CURR_DIR=%~dp0

copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%database.py" "database.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
copy /Y "%CURR_DIR%file_analyzer.py" "file_analyzer.py"

echo.
echo [SUCCESS] v27.0 Compact Applied!
echo UI is now optimized for space and performance.
pause
