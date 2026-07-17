@echo off
title ArchivePro v69 Master Masterpiece
cd /d "%~dp0"
echo Initializing ArchivePro Studio v69...
python "%~dp0main.py"
if %errorlevel% neq 0 pause
pause
