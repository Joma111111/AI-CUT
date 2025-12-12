import os
from pathlib import Path

print("=" * 60)
print("搜索所有导入 whisper 的文件")
print("=" * 60)

found = False

for py_file in Path('.').rglob('*.py'):
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if 'import whisper' in line and not line.strip().startswith('#'):
                    print(f"\n⚠️ 文件: {py_file}")
                    print(f"   行号: {line_num}")
                    print(f"   内容: {line.strip()}")
                    found = True
    except Exception as e:
        pass

if not found:
    print("\n✅ 没有找到导入 whisper 的文件")

print("=" * 60)
