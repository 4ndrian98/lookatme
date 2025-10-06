@echo off
REM Look@Me CMS - Docker Stop Script for Windows
REM ============================================

echo.
echo ============================================
echo    Look@Me CMS - Arresto Servizi
echo ============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker Desktop non sembra essere in esecuzione
    echo I container potrebbero essere gia' fermi
    echo.
)

echo Arresto dei servizi...
echo.

docker-compose down

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo    Tutti i servizi sono stati arrestati
    echo ============================================
    echo.
    echo [INFO] I dati MongoDB sono stati preservati
    echo        nel volume 'mongodb_data'
    echo.
    echo Per riavviare:
    echo   - Doppio click su: start-docker.bat
    echo   - Oppure comando: docker-compose up -d
    echo.
    echo Per eliminare anche i dati:
    echo   docker-compose down -v
    echo.
) else (
    echo.
    echo [ERROR] Errore durante l'arresto
    echo Prova manualmente: docker-compose down
    echo.
)

pause
