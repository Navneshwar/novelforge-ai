@echo off
echo ========================================
echo  NovelForge - Start All Services
echo ========================================
echo.

echo This will start:
echo   1. Ollama Server (LLM runtime)
echo   2. Backend Server (FastAPI)
echo   3. Frontend Server (React/Vite)
echo.

echo Starting Ollama server in a new window...
start "Ollama Server" cmd /c "ollama serve"

echo.
echo Waiting for Ollama to initialize...
timeout /t 3 /nobreak >nul

echo.
echo Starting Backend server in a new window...
start "NovelForge Backend" cmd /c "%~dp0start_backend.bat"

echo.
echo Starting Frontend server in a new window...
start "NovelForge Frontend" cmd /c "%~dp0start_frontend.bat"

echo.
echo ========================================
echo  All services started!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Check the individual windows for logs.
echo.
pause