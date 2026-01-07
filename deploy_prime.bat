@echo off
echo [IronWall] PRIME DEPLOYMENT INITIATED...

:: 1. Cleanup
if exist .git (
    rmdir /s /q .git
)

:: 2. Init
git init
git add .
git commit -m "IronWall Prime: Clean Room Build"

:: 3. Push
git remote add origin https://github.com/Aditya-9-6/IRONWALL-final-public.git
git branch -M main
git push -u origin main --force

echo.
echo [Success] Code Pushed.
echo [Next] Go to Render -> Manual Deploy -> Clear Build Cache & Deploy.
pause
