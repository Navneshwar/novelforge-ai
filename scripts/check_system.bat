@echo off
echo ========================================
echo  NovelForge - System Check
echo ========================================
echo.

echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Python not found!
    echo Please install Python 3.10+ from: https://www.python.org/downloads/windows/
) else (
    for /f "delims=" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
    echo [✓] %PY_VER%
)

echo.
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Node.js not found!
    echo Please install Node.js 18+ from: https://nodejs.org/
) else (
    for /f "delims=" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
    echo [✓] Node.js %NODE_VER%
)

echo.
echo [3/6] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Ollama not found!
    echo Please install Ollama from: https://ollama.ai/download/windows
) else (
    for /f "delims=" %%i in ('ollama --version 2^>^&1') do set OLLAMA_VER=%%i
    echo [✓] Ollama %OLLAMA_VER%
)

echo.
echo [4/6] Checking Ollama models...
echo Available models:
ollama list 2>nul
if errorlevel 1 (
    echo [✗] No models found or Ollama not running
)

echo.
echo [5/6] Checking RAM...
for /f "skip=1 tokens=2" %%i in ('wmic os get TotalVisibleMemorySize /value') do (
    set /a RAM_GB=%%i / 1048576
)
echo Available RAM: %RAM_GB% GB

if %RAM_GB% LSS 8 (
    echo [WARNING] Low RAM detected. Use smaller models (llama3.2:3b, all-minilm)
) else if %RAM_GB% LSS 16 (
    echo [OK] You can run mid-sized models (llama3.1:8b, nomic-embed-text)
) else (
    echo [✓] You can run larger models (llama3.1:70b)
)

echo.
echo [6/6] Checking disk space...
for /f "skip=1 tokens=3" %%i in ('wmic logicaldisk where "DeviceID='C:'" get FreeSpace /value') do (
    set /a FREE_GB=%%i / 1073741824
)
echo Free disk space: %FREE_GB% GB

if %FREE_GB% LSS 10 (
    echo [WARNING] Low disk space. Need at least 10GB free
) else (
    echo [✓] Good disk space
)

echo.
echo ========================================
echo  Check Complete!
echo ========================================
pause