@echo off
chcp 936 >nul
echo ============================================
echo   ShowCut - Build Script
echo ============================================
echo.
echo [1/5] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found. Install Python 3.8+.
    pause
    exit /b 1
)
echo Python OK.
echo.
echo [2/5] Installing dependencies...
python -m pip install PyQt5 Pillow pyinstaller
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed.
echo.
echo [3/5] Generating icon...
if not exist icon.ico (
    python create_icon.py
)
echo.
echo [4/5] Building...
python -m PyInstaller --noconfirm --onefile --windowed --name ShowCut --icon=icon.ico --hidden-import=PyQt5 --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --hidden-import=settings_dialog main.py
if %errorlevel% neq 0 (
    echo Error: Build failed.
    pause
    exit /b 1
)
echo.
echo [5/5] Build complete!
echo.
echo Output: dist\ShowCut.exe
echo.
echo This is a portable version. Just double-click to run.
echo.
pause
