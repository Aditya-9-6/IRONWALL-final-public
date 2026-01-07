@echo off
echo [IronWall] Initializing FINAL Public Deployment...

:: 1. Force Clean Slate
if exist .git (
    rmdir /s /q .git
)
git init
git add .
git commit -m "Final Release: IronWall v2.0"

:: 2. Set Remote to NEW Public Repo
echo.
echo [!] IMPORTANT: Go to GitHub and create ONE LAST REPO:
echo     Link: https://github.com/new
echo     Name: IRONWALL-final-public
echo     Visibility: PUBLIC
echo.
timeout /t 5

git remote remove origin
git remote add origin https://github.com/Aditya-9-6/IRONWALL-final-public.git
git branch -M main

:: 3. Push with Failure Check
echo.
echo [IronWall] Pushing to https://github.com/Aditya-9-6/IRONWALL-final-public.git
echo [!] Sign in if asked...
git push -u origin main --force

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PUSH FAILED!
    echo [Check] 1. Did you create the repo "IRONWALL-final-public"?
    echo [Check] 2. Are you signed in?
    pause
    exit /b
)

echo.
echo [Success] Code is LIVE.
echo [Next Step] Deploy "IRONWALL-final-public" on Render.
pause
