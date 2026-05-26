@echo off
cd /d "%~dp0"

echo Starting Recipe Collector...

start "Recipe Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload"

start "Recipe Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Backend and Frontend are starting...
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
pause