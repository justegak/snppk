@echo off
setlocal
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

echo ================================================
echo   SNPPK - Lancement de l'environnement local
echo   (SQLite local, hors Docker - pour developpement)
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERREUR : Python n'est pas trouve dans le PATH.
    echo Installez Python 3 puis relancez ce script.
    pause
    exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
    echo ERREUR : Node.js / npm n'est pas trouve dans le PATH.
    echo Installez Node.js puis relancez ce script.
    pause
    exit /b 1
)

REM --- Backend : environnement virtuel + dependances ---
if not exist "%BACKEND%\venv\Scripts\python.exe" (
    echo [Backend] Creation de l'environnement virtuel Python...
    python -m venv "%BACKEND%\venv"
)

echo [Backend] Installation/verification des dependances...
"%BACKEND%\venv\Scripts\python.exe" -m pip install -q --upgrade pip
"%BACKEND%\venv\Scripts\python.exe" -m pip install -q -r "%BACKEND%\requirements-dev.txt"
if errorlevel 1 (
    echo ERREUR lors de l'installation des dependances backend.
    pause
    exit /b 1
)

set "FIRST_RUN=0"
if not exist "%BACKEND%\dev_db.sqlite3" set "FIRST_RUN=1"

echo [Backend] Migration de la base locale...
pushd "%BACKEND%"
set "DJANGO_SETTINGS_MODULE=dev_settings"
"%BACKEND%\venv\Scripts\python.exe" manage.py migrate --noinput
if errorlevel 1 (
    echo ERREUR lors des migrations.
    popd
    pause
    exit /b 1
)

if "%FIRST_RUN%"=="1" (
    echo [Backend] Premier lancement : creation des comptes et donnees de demonstration...
    "%BACKEND%\venv\Scripts\python.exe" seed_demo_data.py
)
popd

REM --- Frontend : dependances npm ---
if not exist "%FRONTEND%\node_modules" (
    echo [Frontend] Installation des dependances npm ^(premiere fois, peut prendre quelques minutes^)...
    pushd "%FRONTEND%"
    call npm install
    popd
)

echo.
echo [Backend]  Demarrage sur http://127.0.0.1:8000 ...
start "SNPPK - Backend (Django)" cmd /k ""%BACKEND%\run-backend.bat""

echo [Frontend] Demarrage sur http://localhost:5173 ...
start "SNPPK - Frontend (Vite)" cmd /k ""%FRONTEND%\run-frontend.bat""

echo [Navigateur] Ouverture dans quelques secondes...
timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo ================================================
echo   Application lancee :
echo     Frontend : http://localhost:5173
echo     Backend  : http://127.0.0.1:8000
echo.
echo   Comptes de demonstration (mot de passe : Snppk@2026)
echo     admin.snppk          Super Admin
echo     national.tchoua      National
echo     regional.centre      Regional (Centre)
echo     regional.littoral    Regional (Littoral)
echo     superviseur.yde1     Superviseur (Yaounde)
echo     superviseur.dla1     Superviseur (Douala)
echo     controleur.yde1      Controleur (Yaounde)
echo     controleur.dla1      Controleur (Douala)
echo.
echo   Pour arreter l'application : fermez les deux
echo   fenetres "SNPPK - Backend" et "SNPPK - Frontend".
echo ================================================
echo.
pause
