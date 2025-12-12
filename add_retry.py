"""
添加重试机制和超时设置
"""

print("添加重试和超时机制...")

# 读取文件
with open('core/script_generator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 在文件开头添加 import
import_idx = None
for i, line in enumerate(lines):
    if line.startswith('import config'):
        import_idx = i + 1
        break

if import_idx:
    lines.insert(import_idx, 'import time\n')

# 找到 _generate_with_openai 方法
start_idx = None
for i, line in enumerate(lines):
    if 'def _generate_with_openai(self' in line:
        start_idx = i
        break

# 替换方法
new_method = '''    def _generate_with_openai(self, prompt: str, images: List[str] = None) -> str:
        """使用OpenAI生成文案（带重试）"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                messages = [{"role": "user", "content": prompt}]
                
                # 如果有图片，添加图片内容（仅支持 vision 模型）
                if images and len(images) > 0 and 'vision' in self.model.lower():
                    content = [{"type": "text", "text": prompt}]
                    for img_path in images[:3]:  # 最多3张图
                        try:
                            import base64
                            with open(img_path, 'rb') as f:
                                img_data = base64.b64encode(f.read()).decode()
                            content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                            })
                        except Exception as e:
                            logger.warning(f"图片加载失败: {img_path}, {e}")
                    
                    messages = [{"role": "user", "content": content}]
                
                # 使用配置的模型
                model_name = getattr(config, 'OPENAI_MODEL', 'gpt-4o-mini')
                logger.info(f"调用 OpenAI API: {model_name} (尝试 {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=getattr(config, 'OPENAI_TEMPERATURE', 0.7),
                    max_tokens=getattr(config, 'OPENAI_MAX_TOKENS', 2048),
                    timeout=60.0  # 60秒超时
                )
                
                script = response.choices[0].message.content.strip()
                logger.info(f"OpenAI 生成成功，长度: {len(script)}")
                return script
                
            except Exception as e:
                logger.warning(f"OpenAI API 调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    logger.error(f"OpenAI API 调用失败，已达最大重试次数")
                    raise ScriptGenerationError(f"OpenAI生成失败: {str(e)}")

'''

# 找到方法结束位置
end_idx = start_idx + 1
indent_count = 0
for i in range(start_idx + 1, len(lines)):
    line = lines[i]
    if line.strip() and not line.startswith(' ' * 4):
        end_idx = i
        break
    if 'def ' in line and not line.startswith(' ' * 8):
        end_idx = i
        break

# 替换
new_lines = lines[:start_idx] + [new_method] + lines[end_idx:]

# 写回
with open('core/script_generator.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 已添加重试和超时机制")

# 测试
print("\n" + "="*60)
print("测试重试机制...")
print("="*60)

try:
    from core.script_generator import ScriptGenerator
    
    generator = ScriptGenerator(model="openai")
    test_data = [{'path': 'test.jpg', 'scene_id': 1, 'timestamp': 0.0}]
    
    print("\n正在生成文案（带重试）...")
    result = generator.generate(test_data, style="drama", length="short")
    
    print("\n" + "="*60)
    print("✅ 文案生成成功！")
    print("="*60)
    print(result[0]['script'][:200] + "...")
    print("="*60)
    
    print("\n✅ 功能完整！特性：")
    print("   • 自动重试 3 次")
    print("   • 60 秒超时")
    print("   • 指数退避策略")
    print("\n现在可以运行: python main.py")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
