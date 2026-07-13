@echo off
setlocal

title Apply SmartArchive Update v4
set "PROJECT=C:\Users\amin\Desktop\SmartArchive"
set "UPDATE=%~dp0UpdateFiles"
set "BACKUP=%USERPROFILE%\Desktop\SmartArchive_Backup_v4"

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

for %%F in (main.py archiver.py file_analyzer.py gemma_connector.py) do (
    if exist "%PROJECT%\%%F" copy /Y "%PROJECT%\%%F" "%BACKUP%\%%F" >nul
    copy /Y "%UPDATE%\%%F" "%PROJECT%\%%F" >nul
)

echo.
echo SmartArchive Update v4 was applied successfully.
echo A backup of the previous files was saved here:
echo %BACKUP%
echo.
echo AutoSync will commit and push these changes automatically.
pause
endlocal
