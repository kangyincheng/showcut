@echo off
chcp 65001 >nul
echo ============================================
echo   ShowCut - 截图工具 打包脚本
echo ============================================
echo.

echo [1/4] 检查 Python 环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.8 或更高版本。
    pause
    exit /b 1
)
echo Python 环境正常。
echo.

echo [2/4] 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖包安装失败。
    pause
    exit /b 1
)
echo 依赖包安装完成。
echo.

echo [3/4] 开始打包...
pyinstaller --noconfirm --onefile --windowed --name "ShowCut" ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    main.py

if %errorlevel% neq 0 (
    echo 错误: 打包失败。
    pause
    exit /b 1
)
echo.

echo [4/4] 打包完成！
echo.
echo 可执行文件位于: dist\ShowCut.exe
echo.
echo 注意: 这是免安装版本，直接双击 ShowCut.exe 即可运行。
echo.
pause
