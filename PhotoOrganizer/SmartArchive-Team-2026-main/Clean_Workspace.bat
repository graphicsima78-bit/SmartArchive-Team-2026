@echo off
title ArchivePro Workspace Cleaner
echo Deleting old version files and temporary data...

:: Delete Old Apps
del /f /q main.py archiver.py database.py taxonomy.py taxonomy.json
del /f /q file_analyzer.py fast_image_analyzer.py photo_analyzer.py gemma_connector.py

:: Delete Old Bat files
del /f /q Apply_SmartArchive_Update_v*.bat

:: Delete Heavy Installers
del /f /q innosetup-6.7.3.exe dlib-19.24.99-cp312-cp312-win_amd64.whl main.spec setup.iss

:: Delete Folders
rd /s /q build
rd /s /q dist
rd /s /q __pycache__
rd /s /q ai

echo.
echo [DONE] Workspace is now clean and optimized!
echo Use Run_Archive_Media.bat or Run_Archive_Visuals.bat to start.
pause
