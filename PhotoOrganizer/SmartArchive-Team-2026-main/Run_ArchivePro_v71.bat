@echo off
title ArchivePro v71 Master Masterpiece
cd /d "%~dp0"
echo Initializing ArchivePro Studio v71...
python "%~dp0main.py"
if %errorlevel% neq 0 pause
pause
