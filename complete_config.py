"""
完善阿里云 TTS 配置
"""

print("完善配置文件...")

with open('config.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已有 TTS_VOICE 配置
if 'TTS_VOICE' not in content:
    # 找到 TTS_ENGINE 的位置，在其后添加 TTS_VOICE
    import re
    
    # 查找 TTS_ENGINE 所在行
    match = re.search(r'(TTS_ENGINE\s*=\s*["\'][^"\']+["\'])', content)
    
    if match:
        engine_line = match.group(1)
        # 在 TTS_ENGINE 后面添加 TTS_VOICE 配置
        new_config = f'''{engine_line}
TTS_VOICE = "xiaoyun"  # 阿里云默认音色（小云-温柔女声）

# 阿里云 TTS 可用音色
# 女声: xiaoyun, ruoxi, siqi, sijia, aiqi, aijia, aiyu, aiyue, xiaomei
# 男声: xiaogang, sicheng, aicheng
# 童声: aitong'''
        
        content = content.replace(engine_line, new_config)
        print("✅ 已添加 TTS_VOICE 配置")
    else:
        # 如果找不到 TTS_ENGINE，在文件末尾添加
        content += '\n\n# TTS 配置\n'
        content += 'TTS_VOICE = "xiaoyun"  # 阿里云默认音色\n'
        print("✅ 已在文件末尾添加 TTS_VOICE 配置")
else:
    print("✅ TTS_VOICE 配置已存在")

# 确保 TTS_ENGINE 是 aliyun
if 'TTS_ENGINE = "aliyun"' not in content:
    import re
    content = re.sub(
        r'TTS_ENGINE\s*=\s*["\'][^"\']+["\']',
        'TTS_ENGINE = "aliyun"',
        content
    )
    print("✅ 已设置 TTS_ENGINE = aliyun")

with open('config.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 60)
print("配置完成！")
print("=" * 60)

# 重新验证
print("\n验证配置...")
import sys
if 'config' in sys.modules:
    del sys.modules['config']

import config

print(f"✅ TTS 引擎: {config.TTS_ENGINE}")

if hasattr(config, 'TTS_VOICE'):
    print(f"✅ 默认音色: {config.TTS_VOICE}")
else:
    print("⚠️  TTS_VOICE 未找到，使用默认值 xiaoyun")

if hasattr(config, 'ALIYUN_ACCESS_KEY_ID'):
    print(f"✅ 阿里云 AccessKeyId: {config.ALIYUN_ACCESS_KEY_ID[:10]}...")
if hasattr(config, 'ALIYUN_ACCESS_KEY_SECRET'):
    print(f"✅ 阿里云 AccessKeySecret: {config.ALIYUN_ACCESS_KEY_SECRET[:10]}...")
if hasattr(config, 'ALIYUN_APP_KEY'):
    print(f"✅ 阿里云 AppKey: {config.ALIYUN_APP_KEY}")

print("\n" + "=" * 60)
print("🎉 配置完成！现在可以运行:")
print("  python main.py")
print("=" * 60)
