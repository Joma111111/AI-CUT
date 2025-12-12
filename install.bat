@echo off
echo ========================================
echo   AICraft 安装脚本 (Windows)
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    echo 请访问 https://www.python.org/downloads/ 下载安装
    pause
    exit /b 1
)

echo [1/3] 检测到Python
python --version

echo.
echo [2/3] 安装依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [3/3] 配置环境...
if not exist .env (
    copy .env.example .env
    echo 已创建 .env 文件，请编辑填入API密钥
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 编辑 .env 文件，填入API密钥
echo 2. 运行程序: python main.py
echo.
pause
