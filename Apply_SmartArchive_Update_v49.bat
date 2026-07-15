@echo off
title ArchivePro v49 Persian Artist Update
echo ===============================================
echo      ArchivePro Studio v49.0 (Persian Singer)
echo ===============================================
echo.
echo Enabling Finglish-to-Persian Translation for Singers...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 49.0 Applied! (Persian Support Active)
pause
