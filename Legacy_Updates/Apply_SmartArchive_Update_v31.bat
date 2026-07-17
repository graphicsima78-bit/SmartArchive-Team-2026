@echo off
title ArchivePro v31 Ultra Taxonomy Update
echo ===============================================
echo      ArchivePro Studio v31.0 (Ultra Taxonomy)
echo ===============================================
echo.
echo Synchronizing Materials, Metals, and Symbols...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 31.0 Applied! (Ultra Categorization Ready)
pause
