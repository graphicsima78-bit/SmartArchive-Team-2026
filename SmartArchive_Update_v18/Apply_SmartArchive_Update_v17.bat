@echo off
title SmartArchive v17 Update Tool
echo ===========================================
echo   SmartArchive Enterprise v17.0 Updater
echo ===========================================
echo Updating core files...
copy /Y archiver.py ..\archiver.py
copy /Y main.py ..\main.py
copy /Y database.py ..\database.py
echo.
echo [OK] Update to v17.0 Applied successfully!
echo Press any key to finish.
pause > nul
