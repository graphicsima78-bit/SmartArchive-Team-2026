@echo off
setlocal EnableExtensions

title Apply ArchivePro Studio v68
set "PROJECT=C:\Users\amin\Desktop\SmartArchive"
set "CORE=%~dp0Core"
set "BACKUP=%USERPROFILE%\Desktop\SmartArchive_Backup_v68"
set "LEGACY=%PROJECT%\Legacy_Updates"

if not exist "%PROJECT%\main.py" (
    echo ERROR: Existing SmartArchive project was not found:
    echo %PROJECT%
    pause
    exit /b 1
)

if not exist "%CORE%\main.py" (
    echo ERROR: Core source files were not found next to this script.
    pause
    exit /b 1
)

mkdir "%BACKUP%" 2>nul
mkdir "%LEGACY%" 2>nul

REM Backup and replace the canonical source files.
for %%F in (main.py archiver.py styles.py audio_analyzer.py database.py fast_image_analyzer.py file_analyzer.py gemma_connector.py photo_analyzer.py taxonomy.py requirements.txt .gitignore Run_ArchivePro.bat) do (
    if exist "%PROJECT%\%%F" copy /Y "%PROJECT%\%%F" "%BACKUP%\%%F" >nul
    copy /Y "%CORE%\%%F" "%PROJECT%\%%F" >nul
)

REM taxonomy.json contains user-defined rules. Keep it if it already exists.
if not exist "%PROJECT%\taxonomy.json" copy /Y "%CORE%\taxonomy.json" "%PROJECT%\taxonomy.json" >nul

REM Refresh the one supported AutoSync folder.
robocopy "%CORE%\Automation" "%PROJECT%\Automation" /E /R:1 /W:1 >nul
if not exist "%PROJECT%\Team_Shared\WORK_LOG.md" (
    mkdir "%PROJECT%\Team_Shared" 2>nul
    copy /Y "%CORE%\Team_Shared\WORK_LOG.md" "%PROJECT%\Team_Shared\WORK_LOG.md" >nul
)

REM Preserve old update packages and duplicate workers instead of deleting them.
for %%F in ("%PROJECT%\Apply_ArchivePro_*.bat" "%PROJECT%\Apply_SmartArchive_Update_v*.bat" "%PROJECT%\ArchivePro_*.zip" "%PROJECT%\SmartArchive_Update_v*.zip") do (
    if exist "%%~fF" move /Y "%%~fF" "%LEGACY%\" >nul
)
for %%F in (master_engine.py media_archiver.py media_main.py visual_archiver.py visual_main.py) do (
    if exist "%PROJECT%\%%F" move /Y "%PROJECT%\%%F" "%LEGACY%\" >nul
)
for /d %%D in ("%PROJECT%\SmartArchive_Update_v*") do (
    if exist "%%~fD" move /Y "%%~fD" "%LEGACY%\" >nul
)

copy /Y "%CORE%\Legacy_Updates\README.md" "%LEGACY%\README.md" >nul

echo.
echo ArchivePro Studio v68 was applied successfully.
echo Core source files are now unified in the project root.
echo Legacy update files were moved to:
echo %LEGACY%
echo Backup of replaced files:
echo %BACKUP%
echo.
echo AutoSync will commit and push the cleaned structure automatically.
pause
endlocal
