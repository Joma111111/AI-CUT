"""
打包脚本
功能：自动打包应用为可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_step(step: str):
    """打印步骤"""
    print(f"\n{'='*60}")
    print(f"  {step}")
    print('='*60)


def clean_build():
    """清理构建目录"""
    print_step("清理构建目录")
    
    dirs_to_clean = ['build', 'dist']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"删除: {dir_path}")
            shutil.rmtree(dir_path)
    
    print("✅ 清理完成")


def check_pyinstaller():
    """检查PyInstaller"""
    print_step("检查PyInstaller")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ PyInstaller版本: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("❌ PyInstaller未安装")
    print("正在安装PyInstaller...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True
        )
        print("✅ PyInstaller安装完成")
        return True
    except:
        print("❌ PyInstaller安装失败")
        return False


def build_executable():
    """构建可执行文件"""
    print_step("构建可执行文件")
    
    spec_file = Path("build.spec")
    
    if not spec_file.exists():
        print("❌ build.spec 不存在")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", str(spec_file)],
            check=True
        )
        print("✅ 构建完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 构建失败")
        return False


def copy_resources():
    """复制资源文件"""
    print_step("复制资源文件")
    
    dist_dir = Path("dist/AICraft")
    
    if not dist_dir.exists():
        print("❌ dist目录不存在")
        return False
    
    # 复制资源
    resources = [
        ("resources", "resources"),
        (".env.example", ".env.example"),
        ("README.md", "README.md"),
        ("docs", "docs"),
    ]
    
    for src, dst in resources:
        src_path = Path(src)
        dst_path = dist_dir / dst
        
        if src_path.exists():
            if src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            
            print(f"✅ 复制: {src} -> {dst}")
        else:
            print(f"⚠️  跳过: {src} (不存在)")
    
    print("✅ 资源复制完成")
    return True


def create_installer():
    """创建安装包"""
    print_step("创建安装包")
    
    system = sys.platform
    
    if system == "win32":
        return create_windows_installer()
    elif system == "darwin":
        return create_macos_installer()
    elif system.startswith("linux"):
        return create_linux_installer()
    else:
        print(f"⚠️  不支持的平台: {system}")
        return False


def create_windows_installer():
    """创建Windows安装包"""
    print("创建Windows安装包...")
    
    # 检查NSIS
    nsis_path = Path("C:/Program Files (x86)/NSIS/makensis.exe")
    
    if not nsis_path.exists():
        print("⚠️  NSIS未安装，跳过安装包创建")
        print("   下载地址: https://nsis.sourceforge.io/")
        return False
    
    # TODO: 创建NSIS脚本并编译
    print("⚠️  Windows安装包功能待实现")
    return False


def create_macos_installer():
    """创建macOS安装包"""
    print("创建macOS安装包...")
    
    # TODO: 创建DMG
    print("⚠️  macOS安装包功能待实现")
    return False


def create_linux_installer():
    """创建Linux安装包"""
    print("创建Linux安装包...")
    
    # TODO: 创建AppImage或DEB
    print("⚠️  Linux安装包功能待实现")
    return False


def create_archive():
    """创建压缩包"""
    print_step("创建压缩包")
    
    dist_dir = Path("dist/AICraft")
    
    if not dist_dir.exists():
        print("❌ dist目录不存在")
        return False
    
    import zipfile
    
    zip_name = "AICraft-portable.zip"
    zip_path = Path("dist") / zip_name
    
    print(f"创建压缩包: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in dist_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, arcname)
                print(f"  添加: {arcname}")
    
    print(f"✅ 压缩包创建完成: {zip_path}")
    print(f"   大小: {zip_path.stat().st_size / (1024*1024):.2f} MB")
    
    return True


def print_summary():
    """打印总结"""
    print_step("构建完成")
    
    dist_dir = Path("dist")
    
    if dist_dir.exists():
        print("\n输出文件:")
        for item in dist_dir.iterdir():
            if item.is_dir():
                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                print(f"  📁 {item.name}/ ({size / (1024*1024):.2f} MB)")
            else:
                size = item.stat().st_size
                print(f"  📦 {item.name} ({size / (1024*1024):.2f} MB)")
    
    print("\n下一步:")
    print("1. 测试可执行文件: dist/AICraft/AICraft.exe")
    print("2. 分发压缩包: dist/AICraft-portable.zip")
    print("3. 发布到GitHub Releases")


def main():
    """主函数"""
    print("\n🔨 AICraft 打包工具\n")
    
    steps = [
        ("清理构建目录", clean_build),
        ("检查PyInstaller", check_pyinstaller),
        ("构建可执行文件", build_executable),
        ("复制资源文件", copy_resources),
        ("创建压缩包", create_archive),
    ]
    
    for step_name, step_func in steps:
        try:
            result = step_func()
            if not result and step_name in ["检查PyInstaller", "构建可执行文件"]:
                print(f"\n❌ {step_name} 失败，终止构建")
                return 1
        except Exception as e:
            print(f"\n❌ {step_name} 出错: {str(e)}")
            return 1
    
    print_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
