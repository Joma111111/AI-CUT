"""
安装脚本
功能：自动安装依赖和配置环境
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """打印横幅"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║        🎬 AICraft 安装向导            ║
    ║                                       ║
    ║    AI视频解说工具 - 自动安装程序      ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """检查Python版本"""
    print("\n[1/8] 检查Python版本...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python版本过低，需要Python 3.9+")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_pip():
    """检查pip"""
    print("\n[2/8] 检查pip...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ pip已安装: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("❌ pip未安装")
    return False


def upgrade_pip():
    """升级pip"""
    print("\n[3/8] 升级pip...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True
        )
        print("✅ pip升级完成")
        return True
    except:
        print("⚠️  pip升级失败，继续安装...")
        return False


def install_dependencies():
    """安装依赖"""
    print("\n[4/8] 安装依赖包...")
    print("   这可能需要几分钟时间，请耐心等待...")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt 不存在")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False


def check_ffmpeg():
    """检查FFmpeg"""
    print("\n[5/8] 检查FFmpeg...")
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg已安装: {version_line}")
            return True
    except:
        pass
    
    print("⚠️  FFmpeg未安装")
    print("   请访问 https://ffmpeg.org/download.html 下载安装")
    print("   或使用包管理器安装:")
    
    system = platform.system()
    if system == "Windows":
        print("   - 使用 Chocolatey: choco install ffmpeg")
        print("   - 使用 Scoop: scoop install ffmpeg")
    elif system == "Darwin":
        print("   - 使用 Homebrew: brew install ffmpeg")
    elif system == "Linux":
        print("   - Ubuntu/Debian: sudo apt install ffmpeg")
        print("   - CentOS/RHEL: sudo yum install ffmpeg")
    
    return False


def setup_config():
    """设置配置"""
    print("\n[6/8] 配置环境变量...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env 文件已存在")
        return True
    
    if not env_example.exists():
        print("⚠️  .env.example 不存在，跳过配置")
        return True
    
    # 复制示例文件
    import shutil
    shutil.copy(env_example, env_file)
    
    print("✅ 已创建 .env 文件")
    print("   请编辑 .env 文件，填入你的API密钥")
    
    return True


def create_directories():
    """创建必要的目录"""
    print("\n[7/8] 创建目录结构...")
    
    directories = [
        "projects",
        "data",
        "logs",
        "temp",
        "output",
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录创建完成")
    return True


def test_import():
    """测试导入"""
    print("\n[8/8] 测试模块导入...")
    
    modules = [
        "PyQt6",
        "cv2",
        "openai",
        "google.generativeai",
        "edge_tts",
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  以下模块导入失败: {', '.join(failed)}")
        print("   请检查依赖安装是否完整")
        return False
    
    print("\n✅ 所有模块导入成功")
    return True


def print_summary(success: bool):
    """打印总结"""
    print("\n" + "="*50)
    
    if success:
        print("\n🎉 安装完成！\n")
        print("下一步:")
        print("1. 编辑 .env 文件，填入API密钥")
        print("2. 运行程序: python main.py")
        print("3. 查看文档: docs/user_guide.md")
        print("\n祝你使用愉快！")
    else:
        print("\n❌ 安装过程中出现错误\n")
        print("请检查上述错误信息，解决问题后重新运行安装脚本")
        print("\n如需帮助，请访问:")
        print("- GitHub Issues: https://github.com/yourusername/aicraft-client/issues")
        print("- 文档: https://yourwebsite.com/docs")
    
    print("\n" + "="*50)


def main():
    """主函数"""
    print_banner()
    
    steps = [
        ("检查Python版本", check_python_version),
        ("检查pip", check_pip),
        ("升级pip", upgrade_pip),
        ("安装依赖", install_dependencies),
        ("检查FFmpeg", check_ffmpeg),
        ("配置环境", setup_config),
        ("创建目录", create_directories),
        ("测试导入", test_import),
    ]
    
    success = True
    
    for step_name, step_func in steps:
        try:
            result = step_func()
            if not result and step_name in ["检查Python版本", "检查pip", "安装依赖"]:
                success = False
                break
        except Exception as e:
            print(f"❌ {step_name} 失败: {str(e)}")
            success = False
            break
    
    print_summary(success)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
