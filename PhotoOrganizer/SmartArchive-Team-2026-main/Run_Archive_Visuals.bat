@echo off
title ArchivePro - Visual Master
echo Path: %~dp0
echo Starting Specialized Design & Image Tool...
python "%~dp0visual_main.py"
if %errorlevel% neq 0 pause
pause
