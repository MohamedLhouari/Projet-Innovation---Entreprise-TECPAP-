@echo off
REM Script de lancement de l'Agent IA de Decision OEE - TECPAP

echo ============================================================
echo Agent IA de Decision pour l'Amelioration de l'OEE - TECPAP
echo ============================================================
echo.

REM Verification de Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    echo Veuillez installer Python 3.8 ou superieur
    pause
    exit /b 1
)

echo [1/3] Verification de Python... OK
echo.

REM Installation des dependances si necessaire
echo [2/3] Verification des dependances...
pip show flask >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installation des dependances en cours...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERREUR: Echec de l'installation des dependances
        pause
        exit /b 1
    )
) else (
    echo Dependances deja installees
)
echo.

echo [3/3] Demarrage de l'application...
echo.
echo ============================================================
echo L'application sera accessible sur: http://localhost:5000
echo ============================================================
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

REM Lancement de l'application
python app.py

pause
