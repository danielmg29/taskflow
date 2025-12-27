@echo off
REM Docker development helper script for Windows

if "%1"=="start" (
    echo Starting TaskFlow development environment...
    docker-compose up -d
    echo Services started!
    goto :eof
)

if "%1"=="stop" (
    echo Stopping TaskFlow...
    docker-compose down
    goto :eof
)

if "%1"=="logs" (
    docker-compose logs -f %2
    goto :eof
)

if "%1"=="shell" (
    docker-compose exec backend bash
    goto :eof
)

if "%1"=="migrate" (
    echo Running migrations...
    docker-compose exec backend python manage.py makemigrations
    docker-compose exec backend python manage.py migrate
    goto :eof
)

echo TaskFlow Docker Helper
echo.
echo Usage: scripts\docker-dev.bat [command]
echo.
echo Commands:
echo   start    - Start all services
echo   stop     - Stop all services
echo   logs     - View logs
echo   shell    - Open bash in backend
echo   migrate  - Run migrations