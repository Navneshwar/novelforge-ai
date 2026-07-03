@echo off
echo ========================================
echo  NovelForge - Clean Cache
echo ========================================
echo.

cd %~dp0..\backend

echo Cleaning Python cache...
del /s /q __pycache__ 2>nul
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo [✓] Python cache cleaned

echo.
echo Cleaning Cognee data...
if exist "data\cognee.db" (
    echo Removing Cognee database...
    del data\cognee.db 2>nul
    echo [✓] Cognee database removed
)

if exist "data\vectors" (
    echo Removing vector store...
    rmdir /s /q data\vectors 2>nul
    echo [✓] Vector store removed
)

if exist "data\graph" (
    echo Removing graph store...
    rmdir /s /q data\graph 2>nul
    echo [✓] Graph store removed
)

echo.
cd %~dp0..\frontend

echo Cleaning Node.js cache...
if exist "node_modules\.cache" (
    rmdir /s /q node_modules\.cache 2>nul
    echo [✓] Node cache cleaned
)

if exist ".vite" (
    rmdir /s /q .vite 2>nul
    echo [✓] Vite cache cleaned
)

if exist "dist" (
    rmdir /s /q dist 2>nul
    echo [✓] Build output cleaned
)

echo.
echo ========================================
echo  Cache cleaned!
echo ========================================
echo.
echo Note: This removes Cognee memory data.
echo You will need to re-add your story content.
echo.
pause
