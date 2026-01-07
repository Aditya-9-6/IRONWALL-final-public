@echo off
echo [IronWall] Initializing Private Deployment for Aditya-9-6...

:: 1. Initialize Git
if not exist .git (
    git init
    git add .
    git commit -m "Initial Commit: IronWall v2 + IronEye"
) else (
    echo [!] Git already initialized. Adding changes...
    git add .
    git commit -m "Update: Pre-deployment polish"
)

:: 2. Set Remote for Aditya-9-6
echo.
echo [!] ensure you have created "ironwall-private" on GitHub!
echo     Link: https://github.com/new
echo     Name: ironwall-private
echo     Visibility: PRIVATE (Important!)
echo.
timeout /t 5

git remote remove origin
git remote add origin https://github.com/Aditya-9-6/IRONWALL-private.git
git branch -M main

:: 3. Push
echo.
echo [IronWall] Pushing to https://github.com/Aditya-9-6/IRONWALL-private.git
echo [!] You may be asked to sign in via browser...
git push -u origin main

echo.
echo [Success] Code is now valid in your Private Hub.
echo [Next Step] Go to Render.com -> New Web Service -> Connect GitHub -> Select 'ironwall-private'
pause
