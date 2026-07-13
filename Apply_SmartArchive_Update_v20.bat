@echo off
title SmartArchive v20 Stable Update
echo ===========================================
echo   SmartArchive Enterprise v20.0 (Stable)
echo ===========================================
echo.
echo [1/2] Copying core files to parent directory...
copy /Y main.py ..\main.py
copy /Y archiver.py ..\archiver.py
copy /Y database.py ..\database.py
copy /Y styles.py ..\styles.py
echo.
echo [2/2] Cleaning old version files...
if exist ..\Apply_SmartArchive_Update_v18.bat del /Q ..\Apply_SmartArchive_Update_v18.bat
if exist ..\Apply_SmartArchive_Update_v19.bat del /Q ..\Apply_SmartArchive_Update_v19.bat

echo.
echo [SUCCESS] Version 20.0 is ready!
echo You can now close this window and run the program from the main folder.
pause
