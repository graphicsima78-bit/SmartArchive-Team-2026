@echo off
title ArchivePro Studio v22 Updater
echo ===============================================
echo      ArchivePro Studio v22.0 (Official UI)
echo ===============================================
echo Applying Studio-Grade interface...
copy /Y archiver.py ..\archiver.py
copy /Y main.py ..\main.py
copy /Y database.py ..\database.py
copy /Y styles.py ..\styles.py
copy /Y file_analyzer.py ..\file_analyzer.py
echo.
echo [DONE] Version 22.0 Studio Upgrade Applied!
pause
