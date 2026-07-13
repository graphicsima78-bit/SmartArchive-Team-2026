@echo off
title SmartArchive v18 Ultimate Update
echo ===========================================
echo   SmartArchive Enterprise v18.0 (Modern UI)
echo ===========================================
echo Updating core files and styles...
copy /Y archiver.py ..\archiver.py
copy /Y main.py ..\main.py
copy /Y database.py ..\database.py
copy /Y styles.py ..\styles.py
echo.
echo [DONE] Version 18.0 Applied with Modern Theme!
pause
