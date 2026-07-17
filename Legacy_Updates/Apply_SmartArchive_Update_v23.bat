@echo off
title ArchivePro v23 Auto-Deploy
echo ===============================================
echo      ArchivePro Studio v23.0 (Smart Deploy)
echo ===============================================
echo.
echo Check current directory...
if not exist main.py (
    echo [ERROR] Please run this BAT file INSIDE the main SmartArchive folder.
    pause
    exit
)

echo Updating core components...
:: کپی فایل‌ها در همان پوشه (بدون نیاز به ..\)
:: این کار باعث می‌شود اگر فایل‌ها کنار بات باشند، جایگزین فایل‌های اصلی شوند.
copy /Y archiver.py archiver.py
copy /Y main.py main.py
copy /Y database.py database.py
copy /Y styles.py styles.py
copy /Y file_analyzer.py file_analyzer.py

echo.
echo [SUCCESS] Version 23.0 Applied Successfully!
echo All professional styles and logic are now active.
pause
