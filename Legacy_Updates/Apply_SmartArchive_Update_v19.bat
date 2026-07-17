@echo off
title SmartArchive v19 Light & Fast
echo ===========================================
echo   SmartArchive Enterprise v19.0 (Ultra Light)
echo ===========================================
echo Cleaning and Updating...
copy /Y archiver.py ..\archiver.py
copy /Y main.py ..\main.py
copy /Y database.py ..\database.py
copy /Y styles.py ..\styles.py
echo.
echo [DONE] Version 19.0 Applied! (Files Cleaned)
pause
