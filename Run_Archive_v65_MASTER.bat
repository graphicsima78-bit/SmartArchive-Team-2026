@echo off
title ArchivePro v65 Golden Master
cd /d "%~dp0"
echo Initializing Golden Master Suite...
python "%~dp0media_main.py"
if %errorlevel% neq 0 pause
