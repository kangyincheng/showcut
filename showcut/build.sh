#!/bin/bash

echo "============================================"
echo "  ShowCut - 截图工具 打包脚本 (Linux测试)"
echo "============================================"
echo ""

echo "[1/4] 检查 Python 环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到 Python3，请先安装 Python 3.8 或更高版本。"
    exit 1
fi
echo "Python 环境正常。"
echo ""

echo "[2/4] 安装依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 依赖包安装失败。"
    exit 1
fi
echo "依赖包安装完成。"
echo ""

echo "[3/4] 开始打包..."
pyinstaller --noconfirm --onefile --windowed --name "ShowCut" \
    --hidden-import=PyQt5 \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    main.py

if [ $? -ne 0 ]; then
    echo "错误: 打包失败。"
    exit 1
fi
echo ""

echo "[4/4] 打包完成！"
echo ""
echo "可执行文件位于: dist/ShowCut"
echo ""
