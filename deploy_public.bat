@echo off
echo [IronWall] Initializing Public Deployment for Aditya-9-6...

:: 1. Force Git Re-initialization (to reset remote)
if exist .git (
    rmdir /s /q .git
)
git init
git add .
git commit -m "Public Release: IronWall v2"

:: 2. Set Remote to Public Repo
echo.
echo [!] IMPORTANT: Go to https://github.com/new
echo     Name: IRONWALL-public
echo     Visibility: PUBLIC
echo.
timeout /t 5

git remote add origin https://github.com/Aditya-9-6/IRONWALL-public.git
git branch -M main

:: 3. Push
echo.
echo [IronWall] Pushing to https://github.com/Aditya-9-6/IRONWALL-public.git
echo [!] You may be asked to sign in...
git push -u origin main --force

echo.
echo [Success] Code is LIVE on GitHub.
echo [Next Step] Go to Render.com -> New Web Service -> Connect 'IRONWALL-public'
pause
