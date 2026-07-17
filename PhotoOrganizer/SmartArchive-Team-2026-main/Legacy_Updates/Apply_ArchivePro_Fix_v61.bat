@echo off
title ArchivePro v61 Folder Harmonizer
echo ===============================================
echo      ArchivePro Studio v61.0 (Merge Fix)
echo ===============================================
echo.
echo Harmonizing Folder Structure and Logic...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%media_archiver.py" "media_archiver.py"
copy /Y "%CURR_DIR%visual_archiver.py" "visual_archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [DONE] Folders will now MERGE instead of DUPLICATE.
pause
