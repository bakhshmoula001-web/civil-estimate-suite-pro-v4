@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo Civil Estimate Suite Pro v4.0
echo FINAL EXE BUILD - CALCULATOR FORMS INCLUDED
echo ==================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Project virtual environment not found.
    pause
    exit /b 1
)

echo PyInstaller version:
venv\Scripts\python.exe -m PyInstaller --version
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed in venv.
    pause
    exit /b 1
)

echo.
echo Removing old build...
if exist "build" rmdir /s /q "build"
if exist "dist\Civil Estimate Suite Pro 4.0" rmdir /s /q "dist\Civil Estimate Suite Pro 4.0"

echo.
echo Building EXE with all calculator forms...
venv\Scripts\python.exe -m PyInstaller --clean --noconfirm "Civil Estimate Suite Pro 4.0.spec"

if errorlevel 1 (
    echo.
    echo BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo BUILD SUCCESSFUL
echo ==================================================
echo.
echo EXE:
echo dist\Civil Estimate Suite Pro 4.0\Civil Estimate Suite Pro 4.0.exe
echo.
echo Included calculator forms:
echo   PCC
echo   RCC
echo   Brickwork
echo   Plaster
echo   Excavation
echo   Steel
echo   Slab Steel
echo   Column Steel
echo   Beam Steel
echo   Footing
echo   Staircase
echo.
pause
endlocal
