@echo off
title ArchivePro v62 Global Sync
echo ===============================================
echo      ArchivePro Studio v62.0 (The Master)
echo ===============================================
echo.
echo Forcing Internal Metadata Priority and Persian Sync...
set CURR_DIR=%~dp0
copy /Y "%CURR_DIR%master_engine.py" "media_archiver.py"
copy /Y "%CURR_DIR%master_engine.py" "visual_archiver.py"
copy /Y "%CURR_DIR%audio_analyzer.py" "audio_analyzer.py"

echo.
echo [DONE] Metadata Priority and Persian Names Active!
pause
