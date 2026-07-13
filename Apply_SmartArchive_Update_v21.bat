@echo off
title SmartArchive v21 Ultimate Taxonomy Update
echo ===============================================
echo   SmartArchive Enterprise v21.0 (Final Taxonomy)
echo ===============================================
echo Applying new categorization system...
copy /Y archiver.py ..\archiver.py
copy /Y main.py ..\main.py
copy /Y database.py ..\database.py
copy /Y styles.py ..\styles.py
copy /Y file_analyzer.py ..\file_analyzer.py
echo.
echo [DONE] Ultimate Categorization System Applied!
pause
