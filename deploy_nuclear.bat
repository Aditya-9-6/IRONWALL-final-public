@echo off
echo [IronWall] NUCLEAR DEPLOYMENT PROTOCOL INITIATED...
echo [Warning] This will wipe your local git history and force a fresh push.

:: 1. Force Clean Slate
if exist .git (
    echo [Cleaning] Removing old git repository...
    rmdir /s /q .git
)

:: 2. Initialize Fresh
echo [Init] Creating fresh repository...
git init
git add .
git commit -m "Nuclear Reset: IronWall v2.0 Final"

:: 3. Set Remote
echo.
echo [Config] Setting remote to: https://github.com/Aditya-9-6/IRONWALL-final-public.git
git remote add origin https://github.com/Aditya-9-6/IRONWALL-final-public.git
git branch -M main

:: 4. Force Push
echo.
echo [Push] Usage of force...
git push -u origin main --force

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PUSH FAILED!
    echo [Check] 1. Internet Connection
    echo [Check] 2. GitHub Credentials
    pause
    exit /b
)

echo.
echo [Success] Reset Complete.
echo [Next] Go to Render -> Manual Deploy -> 'Clear Build Cache & Deploy'
pause
