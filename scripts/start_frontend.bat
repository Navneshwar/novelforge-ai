@echo off
echo ========================================
echo  NovelForge - Start Frontend Server
echo ========================================
echo.

cd %~dp0..\frontend

echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please download and install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)
echo [✓] Node.js is installed

echo.
echo Checking npm dependencies...
if not exist "node_modules\" (
    echo [WARNING] Dependencies not installed!
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [✓] Dependencies installed
)

echo.
echo ========================================
echo  Starting Frontend Server...
echo ========================================
echo.

call npm run dev

pause