@echo off
echo ========================================
echo  NovelForge - Start Backend Server
echo ========================================
echo.

cd %~dp0..\backend

echo Checking Python virtual environment...
if not exist "venv\" (
    echo [WARNING] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo Please make sure Python is installed and in PATH
        pause
        exit /b 1
    )
    echo [✓] Virtual environment created
)

echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [✓] Virtual environment activated

echo.
echo Checking dependencies...
python -c "import cognee" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dependencies not installed!
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [✓] Dependencies installed
)

echo.
echo Checking .env file...
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo Please edit .env to configure your settings
)

echo.
echo ========================================
echo  Starting Backend Server...
echo ========================================
echo.

python main.py

pause