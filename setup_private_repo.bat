@echo off
echo [IronWall] Initializing Secure Repository...

:: 1. Initialize Git
git init
git add .
git commit -m "Initial Commit: IronWall v2 + IronEye"

echo.
echo [!] IMPORTANT: You must create a PRIVATE repository on GitHub now.
echo     Go to: https://github.com/new
echo     Name: ironwall-private
echo     Visibility: Private
echo.
set /p REPO_URL="Paste your new Repository URL here (e.g., https://github.com/user/repo.git): "

:: 2. Add Remote and Push
git remote add origin %REPO_URL%
git branch -M main
git push -u origin main

echo.
echo [IronWall] Code securely deployed to %REPO_URL%
pause
