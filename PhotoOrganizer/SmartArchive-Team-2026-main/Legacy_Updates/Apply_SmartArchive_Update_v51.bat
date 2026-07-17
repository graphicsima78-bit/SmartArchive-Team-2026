@echo off
title ArchivePro v51 Persian Singer Update
echo ===============================================
echo      ArchivePro Studio v51.0 (Smart Artist)
echo ===============================================
echo.
echo Adding Persian Artist Logic and Language Selection...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 51.0 Applied! (Persian Artist Support)
pause
