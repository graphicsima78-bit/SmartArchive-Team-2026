@echo off
title ArchivePro v32 Supreme Taxonomy Update
echo ===============================================
echo      ArchivePro Studio v32.0 (Supreme Taxonomy)
echo ===============================================
echo.
echo Synchronizing Everything (Interior, Tech, Art)...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
echo.
echo [DONE] Version 32.0 Applied! (Infinite Classification Active)
pause
