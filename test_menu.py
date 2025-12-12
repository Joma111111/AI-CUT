"""
TTS 测试菜单
"""

import subprocess
import sys

def show_menu():
    print("\n" + "=" * 60)
    print("TTS 测试工具")
    print("=" * 60)
    print("1. 快速测试 (5秒)")
    print("2. 完整测试 (20秒)")
    print("3. 批量测试 (30秒)")
    print("4. 查看配置")
    print("5. 切换到阿里云 TTS")
    print("0. 退出")
    print("=" * 60)

def view_config():
    """查看配置"""
    try:
        import config
        print("\n当前配置:")
        print(f"  TTS_ENGINE: {config.TTS_ENGINE}")
        if hasattr(config, 'TTS_VOICE'):
            print(f"  TTS_VOICE: {config.TTS_VOICE}")
        if config.TTS_ENGINE == "aliyun":
            print(f"  ALIYUN_APP_KEY: {config.ALIYUN_APP_KEY[:10]}...")
    except Exception as e:
        print(f"错误: {e}")

def main():
    while True:
        show_menu()
        choice = input("\n请选择 (0-5): ").strip()
        
        if choice == "1":
            subprocess.run([sys.executable, "test_tts.py", "--mode", "quick"])
        elif choice == "2":
            subprocess.run([sys.executable, "test_tts.py", "--mode", "full"])
        elif choice == "3":
            subprocess.run([sys.executable, "test_tts.py", "--mode", "batch"])
        elif choice == "4":
            view_config()
        elif choice == "5":
            subprocess.run([sys.executable, "complete_config.py"])
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效选择，请重试")
        
        input("\n按 Enter 继续...")

if __name__ == "__main__":
    main()
