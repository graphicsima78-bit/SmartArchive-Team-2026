@echo off
title ArchivePro v28 Designer Update
echo ===============================================
echo      ArchivePro Studio v28.0 (Designer Taxonomy)
echo ===============================================
echo.
echo Synchronizing Professional Taxonomy...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 28.0 Designer Edition Applied!
pause
