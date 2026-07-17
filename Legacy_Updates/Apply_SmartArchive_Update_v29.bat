@echo off
title ArchivePro v29 Total Taxonomy Update
echo ===============================================
echo      ArchivePro Studio v29.0 (Total Taxonomy)
echo ===============================================
echo.
echo Synchronizing Global Classification System...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 29.0 Global System Applied!
pause
