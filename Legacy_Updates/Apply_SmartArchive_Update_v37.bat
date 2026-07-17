@echo off
title ArchivePro v37 Precision Update
echo ===============================================
echo      ArchivePro Studio v37.0 (Precision Fix)
echo ===============================================
echo.
echo Correcting Graphics, Music, and Folder structure...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 37.0 Applied! (No numbers, Proper Logic)
pause
