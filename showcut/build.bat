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
if exist create_icon.py (
    python create_icon.py
    if %errorlevel% neq 0 (
        echo Warning: Icon generation failed, continuing without icon.
    )
) else (
    echo Warning: create_icon.py not found, skipping icon generation.
)
echo.

echo [4/5] Building...
set "ICON_ARG="
if exist icon.ico (
    set "ICON_ARG=--icon=icon.ico"
    echo Using icon: icon.ico
) else (
    echo No icon file found, building without custom icon.
)

python -m PyInstaller --noconfirm --onefile --windowed --name ShowCut %ICON_ARG% --hidden-import=PyQt5 --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets main.py

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
