@echo off
title ArchivePro - Media Master
echo Path: %~dp0
echo Starting Professional Media Archive Engine...
python "%~dp0media_main.py"
if %errorlevel% neq 0 pause
pause
