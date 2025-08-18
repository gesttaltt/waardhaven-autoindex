@echo off
REM Setup pre-commit hooks for the waardhaven-autoindex project

echo Setting up pre-commit hooks...

REM Navigate to project root
cd /d "%~dp0..\..\..\"

REM Install pre-commit (if not already installed)
where pre-commit >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ pre-commit is already installed
) else (
    echo Installing pre-commit...
    pip install pre-commit
)

REM Install the pre-commit hooks
echo Installing pre-commit hooks...
pre-commit install

REM Run pre-commit on all files to ensure everything is working
echo Running pre-commit on all files...
pre-commit run --all-files

echo ✓ Pre-commit hooks setup complete!
echo.
echo Usage:
echo   Run manually: pre-commit run --all-files
echo   Auto-format Python: cd apps/api ^&^& black .
echo   Auto-format Frontend: cd apps/web ^&^& npm run format