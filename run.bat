@echo off
title AICraft - AI视频解说工具

REM 检查虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 运行程序
python main.py

if errorlevel 1 (
    echo.
    echo 程序异常退出
    pause
)
