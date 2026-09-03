@echo off
cd /d "%~dp0"
echo Serveur Vite (frontend) sur http://localhost:5173
echo.
call npm run dev
echo.
echo Le serveur frontend s'est arrete.
pause
