@echo off
setlocal

title Apply SmartArchive Update v16
set "PROJECT=C:\Users\amin\Desktop\SmartArchive"
set "UPDATE=%~dp0UpdateFiles"
set "BACKUP=%USERPROFILE%\Desktop\SmartArchive_Backup_v16"

if not exist "%PROJECT%\main.py" (
    echo ERROR: SmartArchive project was not found at:
    echo %PROJECT%
    pause
    exit /b 1
)

if not exist "%UPDATE%\main.py" (
    echo ERROR: UpdateFiles folder is incomplete.
    pause
    exit /b 1
)

mkdir "%BACKUP%" 2>nul

for %%F in (main.py archiver.py styles.py file_analyzer.py gemma_connector.py audio_analyzer.py fast_image_analyzer.py photo_analyzer.py taxonomy.py requirements.txt) do (
    if exist "%PROJECT%\%%F" copy /Y "%PROJECT%\%%F" "%BACKUP%\%%F" >nul
    copy /Y "%UPDATE%\%%F" "%PROJECT%\%%F" >nul
)

REM taxonomy.json is user-editable; only create it if it does not exist yet.
if not exist "%PROJECT%\taxonomy.json" copy /Y "%UPDATE%\taxonomy.json" "%PROJECT%\taxonomy.json" >nul

echo.
echo SmartArchive Update v16 was applied successfully.
echo A backup of the previous files was saved here:
echo %BACKUP%
echo.
echo Your existing taxonomy.json was preserved.
echo AutoSync will commit and push these changes automatically.
pause
endlocal
