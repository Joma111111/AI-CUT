#!/bin/bash

echo "========================================"
echo "  AICraft 安装脚本 (Linux/macOS)"
echo "========================================"
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python3未安装"
    echo "请使用包管理器安装Python3"
    exit 1
fi

echo "[1/3] 检测到Python"
python3 --version

echo
echo "[2/3] 安装依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo
echo "[3/3] 配置环境..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建 .env 文件，请编辑填入API密钥"
fi

echo
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo
echo "下一步:"
echo "1. 编辑 .env 文件，填入API密钥"
echo "2. 运行程序: python3 main.py"
echo
