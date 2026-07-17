@echo off
title ArchivePro Folder Fixer
echo Cleaning up nested folders and heavy junk...

:: ۱. حذف پوشه تکراری و تودرتو
if exist SmartArchive-Team-2026 (
    echo Removing duplicate folder: SmartArchive-Team-2026...
    rd /s /q SmartArchive-Team-2026
)

:: ۲. حذف فایل‌های سنگین و زائد
echo Deleting heavy installers and temp files...
del /f /q dlib-19.24.99-cp312-cp312-win_amd64.whl
del /f /q setup.iss
del /f /q main.spec
del /f /q *.zip
del /f /q gemma_connector.py
del /f /q photo_analyzer.py
del /f /q fast_image_analyzer.py
del /f /q database.py
del /f /q main.py
del /f /q archiver.py

:: ۳. حذف پوشه‌های موقت
rd /s /q build
rd /s /q dist
rd /s /q __pycache__
rd /s /q ai
rd /s /q Automation
rd /s /q Output
rd /s /q Team_Shared

echo.
echo [SUCCESS] Your folder is now CLEAN and PROFESSIONALLY organized.
echo Please copy the new media_main.py and visual_main.py here.
pause
