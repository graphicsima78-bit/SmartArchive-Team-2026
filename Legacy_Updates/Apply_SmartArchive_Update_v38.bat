@echo off
title ArchivePro v38 Audio Polish
echo ===============================================
echo      ArchivePro Studio v38.0 (Audio Fix)
echo ===============================================
echo.
echo Cleaning Audio Filenames and Syncing Logic...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%archiver.py" "archiver.py"
copy /Y "%CURR_DIR%main.py" "main.py"
copy /Y "%CURR_DIR%styles.py" "styles.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"
echo.
echo [DONE] Version 38.0 Applied! (Audio Renaming Fixed)
pause
