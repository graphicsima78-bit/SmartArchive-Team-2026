@echo off
setlocal EnableExtensions

title SmartArchive Shared Folder Cleanup
set "PROJECT=%~dp0"
set "BACKUP=%USERPROFILE%\Desktop\SmartArchive_Legacy_Backup"

if not exist "%PROJECT%main.py" (
    echo ERROR: Put this file directly inside the SmartArchive project folder.
    echo Expected: SmartArchive\Clean_Shared_Project.bat
    pause
    exit /b 1
)

echo.
echo This cleanup will move old update files outside the shared project folder.
echo It will NOT delete main.py, archiver.py, Automation, Team_Shared, Output,
echo taxonomy.json, your project files, or your database.
echo.
echo Backup location:
echo %BACKUP%
echo.
choice /C YN /M "Continue with safe cleanup"
if errorlevel 2 goto :end

mkdir "%BACKUP%" 2>nul

REM Move old update packages and old worker copies outside the project.
for %%F in ("%PROJECT%Apply_ArchivePro_*.bat" "%PROJECT%Apply_SmartArchive_Update_*.bat" "%PROJECT%ArchivePro_*.zip" "%PROJECT%SmartArchive_Update_*.zip" "%PROJECT%ArchivePro_Studio_Clean_*.zip") do (
    if exist "%%~fF" move /Y "%%~fF" "%BACKUP%\" >nul
)

for %%F in (master_engine.py media_archiver.py media_main.py visual_archiver.py visual_main.py) do (
    if exist "%PROJECT%%%F" move /Y "%PROJECT%%%F" "%BACKUP%\" >nul
)

REM Move old update folders outside the shared project.
for /d %%D in ("%PROJECT%SmartArchive_Update_v*") do (
    if exist "%%~fD" move /Y "%%~fD" "%BACKUP%\" >nul
)

REM Safe cache cleanup.
for /r "%PROJECT%" %%F in (*.pyc) do del /q "%%F" 2>nul
for /d /r "%PROJECT%" %%D in (__pycache__) do rd /s /q "%%D" 2>nul
if exist "%PROJECT%Desktop - Shortcut.lnk" move /Y "%PROJECT%Desktop - Shortcut.lnk" "%BACKUP%\" >nul

echo.
echo Cleanup completed.
echo Old update files were moved to:
echo %BACKUP%
echo.
echo The shared project folder now contains only the active project files.

:end
pause
endlocal
