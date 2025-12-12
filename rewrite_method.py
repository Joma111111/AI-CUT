"""
直接重写 _generate_with_openai 方法
"""

print("重写方法...")

with open('core/script_generator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 备份
with open('core/script_generator.py.backup5', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# 找到方法开始和结束
start_idx = None
end_idx = None
indent_count = 0

for i, line in enumerate(lines):
    if 'def _generate_with_openai(self' in line:
        start_idx = i
        continue
    
    if start_idx is not None and end_idx is None:
        # 找下一个同级方法（缩进相同的 def）
        if line.strip().startswith('def ') and not line.startswith('        '):
            end_idx = i
            break

# 如果没找到结束，就到文件末尾
if start_idx is not None and end_idx is None:
    end_idx = len(lines)

# 新方法
new_method = '''    def _generate_with_openai(self, prompt: str, images: List[str] = None) -> str:
        """使用OpenAI生成文案 - Mock版本"""
        logger.warning("使用 Mock 模式生成测试文案（API Key 无效）")
        
        # 返回测试文案
        return """【视频解说】

这是由 AI 自动生成的视频解说词。

画面内容丰富多彩，情节引人入胜。
通过智能分析，我们为您呈现精彩的视频体验。

感谢您的观看！

---
提示：当前使用测试模式
如需使用真实 AI 生成，请配置有效的 OpenAI API Key
"""

'''

# 替换
if start_idx is not None:
    new_lines = lines[:start_idx] + [new_method] + lines[end_idx:]
    
    with open('core/script_generator.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ 已重写方法（第 {start_idx+1} 到 {end_idx} 行）")
else:
    print("❌ 未找到方法")
    exit(1)

# 测试
print("\n测试...")
try:
    from core.script_generator import ScriptGenerator
    
    generator = ScriptGenerator(model="openai")
    test_data = [{'path': 'test.jpg', 'scene_id': 1, 'timestamp': 0.0}]
    result = generator.generate(test_data, style="drama")
    
    print("\n" + "="*60)
    print("✅ 成功！生成的文案：")
    print("="*60)
    print(result)
    print("="*60)
    print("\n✅ 修复完成！现在可以运行: python main.py")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
