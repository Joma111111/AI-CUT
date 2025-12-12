"""
更新脚本
功能：检查和安装更新
"""

import sys
import json
import requests
import subprocess
from pathlib import Path
from packaging import version
import config


def check_update():
    """检查更新"""
    print("检查更新...")
    
    try:
        # 从GitHub获取最新版本
        response = requests.get(
            "https://api.github.com/repos/yourusername/aicraft-client/releases/latest",
            timeout=10
        )
        response.raise_for_status()
        
        latest_release = response.json()
        latest_version = latest_release['tag_name'].lstrip('v')
        current_version = config.APP_VERSION
        
        print(f"当前版本: {current_version}")
        print(f"最新版本: {latest_version}")
        
        if version.parse(latest_version) > version.parse(current_version):
            print(f"\n🎉 发现新版本: {latest_version}")
            print(f"\n更新内容:")
            print(latest_release['body'])
            
            return {
                'has_update': True,
                'version': latest_version,
                'download_url': latest_release['assets'][0]['browser_download_url'] if latest_release['assets'] else None,
                'release_notes': latest_release['body']
            }
        else:
            print("\n✅ 已是最新版本")
            return {'has_update': False}
    
    except Exception as e:
        print(f"❌ 检查更新失败: {str(e)}")
        return None


def download_update(download_url: str, output_path: str):
    """下载更新"""
    print(f"\n下载更新: {download_url}")
    
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\r进度: {progress:.1f}%", end='')
        
        print("\n✅ 下载完成")
        return True
    
    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        return False


def install_update(package_path: str):
    """安装更新"""
    print("\n安装更新...")
    
    # TODO: 实现更新安装逻辑
    # 1. 备份当前版本
    # 2. 解压新版本
    # 3. 替换文件
    # 4. 重启应用
    
    print("⚠️  自动更新功能待实现")
    print("请手动下载并安装新版本")
    
    return False


def main():
    """主函数"""
    print("\n🔄 AICraft 更新工具\n")
    
    # 检查更新
    update_info = check_update()
    
    if not update_info:
        return 1
    
    if not update_info['has_update']:
        return 0
    
    # 询问是否更新
    response = input("\n是否下载更新? (y/n): ")
    
    if response.lower() != 'y':
        print("取消更新")
        return 0
    
    # 下载更新
    download_url = update_info['download_url']
    
    if not download_url:
        print("❌ 无法获取下载链接")
        return 1
    
    output_path = f"AICraft-{update_info['version']}.zip"
    
    if download_update(download_url, output_path):
        print(f"\n✅ 更新包已下载: {output_path}")
        print("请手动解压并安装")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
