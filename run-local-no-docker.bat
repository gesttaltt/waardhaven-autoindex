@echo off
echo Starting Waardhaven AutoIndex (No Docker)...
echo.
echo IMPORTANT: This requires PostgreSQL and Redis to be installed and running locally.
echo.

REM Check if PostgreSQL is running (Windows Service)
sc query "postgresql-x64-15" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: PostgreSQL service not found or not running.
    echo Please ensure PostgreSQL is installed and running.
    echo.
)

REM Start API in a new window
echo Starting FastAPI backend...
start "Waardhaven API" cmd /k "cd apps\api && set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/waardhaven_db && set REDIS_URL=redis://localhost:6379/0 && set SECRET_KEY=local-dev-secret && set ADMIN_TOKEN=local-admin-token && set FRONTEND_URL=http://localhost:3000 && set SKIP_STARTUP_REFRESH=true && set TWELVEDATA_API_KEY=e9b09b7610734d2699dc083f4ef5336d && uvicorn app.main:app --reload --port 8000"

REM Wait a bit for API to start
timeout /t 5 /nobreak >nul

REM Start Frontend in a new window
echo Starting Next.js frontend...
start "Waardhaven Web" cmd /k "cd apps\web && set NEXT_PUBLIC_API_URL=http://localhost:8000 && npm run dev"

echo.
echo ========================================
echo Services are starting in separate windows!
echo ========================================
echo.
echo Access the application at:
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
echo To stop: Close the command windows
echo.
pause