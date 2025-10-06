@echo off
REM Look@Me CMS - Docker Startup Script for Windows
REM ===============================================

echo.
echo ============================================
echo    Look@Me CMS - Docker Startup
echo ============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop non e' in esecuzione!
    echo.
    echo Soluzione:
    echo 1. Apri Docker Desktop dal menu Start
    echo 2. Aspetta che l'icona della balena sia attiva
    echo 3. Riprova questo script
    echo.
    pause
    exit /b 1
)

echo [OK] Docker Desktop e' attivo
echo.

REM Stop existing containers
echo Arresto eventuali container esistenti...
docker-compose down >nul 2>&1
echo.

REM Build and start containers
echo Avvio dei servizi...
echo Questo potrebbe richiedere qualche minuto alla prima esecuzione...
echo.

docker-compose up -d --build

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Errore durante l'avvio!
    echo Controlla i log con: docker-compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo Attendo che i servizi siano pronti...
timeout /t 10 /nobreak >nul

REM Check services
echo.
echo Verifica stato servizi:
echo.

REM Check Backend
curl -f http://localhost:8001/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend: ONLINE - http://localhost:8001
) else (
    echo [?] Backend: In avvio o errore - Controlla i logs
)

REM Check Frontend
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend: ONLINE - http://localhost:3000
) else (
    echo [?] Frontend: In avvio o errore - Controlla i logs
)

REM Check MongoDB
docker exec lookatme-mongodb mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MongoDB: ONLINE
) else (
    echo [?] MongoDB: In avvio o errore
)

echo.
echo ============================================
echo    Look@Me CMS e' pronto!
echo ============================================
echo.
echo Accedi all'applicazione:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8001
echo   API Docs:  http://localhost:8001/docs
echo.
echo Comandi utili:
echo   Visualizza logs:  docker-compose logs -f
echo   Ferma servizi:    docker-compose down
echo   Riavvia:          docker-compose restart
echo.
echo Per maggiori informazioni: WINDOWS_SETUP.md
echo.

REM Ask if user wants to open browser
set /p OPENB="Vuoi aprire il browser? (s/n): "
if /i "%OPENB%"=="s" (
    start http://localhost:3000
    echo.
    echo Browser aperto! Buon lavoro!
)

echo.
pause
