@echo off
echo ========================================
echo  NovelForge - Stop All Services
echo ========================================
echo.

echo Stopping all Node.js processes...
taskkill /F /IM node.exe 2>nul
if errorlevel 1 (
    echo No Node.js processes found
) else (
    echo [✓] Node.js processes stopped
)

echo.
echo Stopping all Python processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq NovelForge*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
if errorlevel 1 (
    echo No Python processes found
) else (
    echo [✓] Python processes stopped
)

echo.
echo Stopping Ollama...
taskkill /F /IM ollama.exe 2>nul
if errorlevel 1 (
    echo Ollama not running or already stopped
) else (
    echo [✓] Ollama stopped
)

echo.
echo ========================================
echo  All services stopped!
echo ========================================
pause