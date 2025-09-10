#!/bin/bash

# Edenx打印机SDK演示程序启动脚本
# 作者: RBQ
# 创建时间: 2025

# 检查Python版本
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]; then
    echo "错误: 需要Python $REQUIRED_VERSION，当前版本为 $PYTHON_VERSION"
    exit 1
fi

# 检查PyQt5是否已安装
python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "错误: 未找到PyQt5库，请运行以下命令安装："
    echo "pip3 install PyQt5"
    exit 1
fi

# 检查mxSdk文件夹是否存在
if [ ! -d "mxSdk" ]; then
    echo "错误: 未找到mxSdk文件夹，请确保已解压mxsdk-macos-arm64.zip"
    exit 1
fi

# 运行演示程序
echo "启动Edenx打印机SDK演示程序..."
python3 printer_demo.py