#!/bin/bash

# 检查虚拟环境
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

# 运行程序
python3 main.py
