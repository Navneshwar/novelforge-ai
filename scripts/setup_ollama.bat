@echo off
echo ========================================
echo  NovelForge - Ollama Setup Script
echo ========================================
echo.

echo Checking if Ollama is installed...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not installed!
    echo Please download and install Ollama from: https://ollama.ai/download/windows
    echo.
    pause
    exit /b 1
)

echo [✓] Ollama is installed
echo.

echo Pulling recommended models...
echo.

echo [1/3] Pulling llama3.2:3b (small, fast model)...
ollama pull llama3.2:3b
if errorlevel 1 (
    echo [WARNING] Failed to pull llama3.2:3b
)

echo.
echo [2/3] Pulling all-minilm (lightweight embedding model)...
ollama pull all-minilm
if errorlevel 1 (
    echo [WARNING] Failed to pull all-minilm
)

echo.
echo [3/3] Pulling llama3.1:8b (optional, better quality)...
echo Do you want to pull llama3.1:8b? (Requires ~8GB RAM) [Y/N]
set /p pull_8b=
if /i "%pull_8b%"=="Y" (
    ollama pull llama3.1:8b
    if errorlevel 1 (
        echo [WARNING] Failed to pull llama3.1:8b
    )
)

echo.
echo ========================================
echo  Installed Models:
echo ========================================
ollama list

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To start Ollama server, run: ollama serve
echo.
pause