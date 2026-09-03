@echo off
cd /d "%~dp0"
set DJANGO_SETTINGS_MODULE=dev_settings
echo Serveur Django (local, SQLite) sur http://127.0.0.1:8000
echo.
venv\Scripts\python.exe manage.py runserver 8000
echo.
echo Le serveur backend s'est arrete.
pause
