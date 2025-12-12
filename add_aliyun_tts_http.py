"""
实现阿里云 TTS (HTTP API 方式)
"""

print("实现阿里云 TTS (HTTP API)...")

# 读取 tts_engine.py
with open('core/tts_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 确保导入了必要的库
if 'import json' not in content:
    content = content.replace('import config', 'import config\nimport json\nimport hmac\nimport hashlib\nimport uuid\nfrom datetime import datetime\nfrom urllib.parse import quote')

# 找到 synthesize 方法，添加 aliyun 分支
old_code = '''            if self.engine == "edge":
                return self._synthesize_edge(text, output_path, voice, rate, pitch, volume)
            elif self.engine == "azure":'''

new_code = '''            if self.engine == "edge":
                return self._synthesize_edge(text, output_path, voice, rate, pitch, volume)
            elif self.engine == "aliyun":
                return self._synthesize_aliyun(text, output_path, voice, rate, pitch, volume)
            elif self.engine == "azure":'''

content = content.replace(old_code, new_code)

# 添加阿里云 TTS 方法（在 _synthesize_edge 后面）
aliyun_method = '''
    def _synthesize_aliyun(self, text: str, output_path: str,
                          voice: str, rate: float, pitch: float, volume: float) -> str:
        """使用阿里云 TTS 合成 (HTTP API)"""
        import requests
        
        try:
            # 阿里云 TTS API 端点
            url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts"
            
            # 参数
            voice_name = voice or getattr(config, 'ALIYUN_VOICE', 'xiaoyun')
            speech_rate = int((rate - 1) * 500)  # -500 到 500
            pitch_rate = int((pitch - 1) * 500)
            volume_val = int(volume * 100)  # 0 到 100
            
            # 请求参数
            params = {
                'appkey': config.ALIYUN_APP_KEY,
                'token': self._get_aliyun_token(),
                'text': text,
                'voice': voice_name,
                'format': 'mp3',
                'sample_rate': 16000,
                'speech_rate': speech_rate,
                'pitch_rate': pitch_rate,
                'volume': volume_val,
            }
            
            logger.info(f"调用阿里云 TTS: voice={voice_name}, rate={rate}, pitch={pitch}, volume={volume}")
            
            # 发送请求
            response = requests.post(url, data=params, timeout=30)
            
            if response.status_code == 200:
                # 检查响应类型
                content_type = response.headers.get('Content-Type', '')
                
                if 'audio' in content_type:
                    # 保存音频
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    logger.info(f"阿里云 TTS 合成完成: {output_path}")
                    return output_path
                else:
                    # 可能是错误信息
                    error_msg = response.text
                    logger.error(f"阿里云 TTS 返回错误: {error_msg}")
                    raise TTSError(f"阿里云 TTS 错误: {error_msg}")
            else:
                logger.error(f"阿里云 TTS 请求失败: {response.status_code} - {response.text}")
                raise TTSError(f"阿里云 TTS 请求失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"阿里云 TTS 调用失败: {e}", exc_info=True)
            raise TTSError(f"阿里云 TTS 失败: {str(e)}")
    
    def _get_aliyun_token(self) -> str:
        """获取阿里云 Token"""
        import requests
        
        try:
            # Token API 端点
            url = "https://nls-meta.cn-shanghai.aliyuncs.com/token"
            
            # 使用 AccessKey 获取 Token
            params = {
                'AccessKeyId': config.ALIYUN_ACCESS_KEY_ID,
                'Action': 'CreateToken',
                'Version': '2019-02-28',
                'Format': 'JSON',
                'RegionId': 'cn-shanghai',
                'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'SignatureMethod': 'HMAC-SHA1',
                'SignatureVersion': '1.0',
                'SignatureNonce': str(uuid.uuid4()),
            }
            
            # 构建签名字符串
            sorted_params = sorted(params.items())
            query_string = '&'.join([f"{quote(k, safe='')}={quote(str(v), safe='')}" for k, v in sorted_params])
            string_to_sign = f"POST&%2F&{quote(query_string, safe='')}"
            
            # 计算签名
            key = (config.ALIYUN_ACCESS_KEY_SECRET + '&').encode('utf-8')
            signature = hmac.new(key, string_to_sign.encode('utf-8'), hashlib.sha1).digest()
            signature_b64 = __import__('base64').b64encode(signature).decode('utf-8')
            
            params['Signature'] = signature_b64
            
            # 发送请求
            response = requests.post(url, data=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'Token' in result and 'Id' in result['Token']:
                    token = result['Token']['Id']
                    logger.info("阿里云 Token 获取成功")
                    return token
                else:
                    logger.error(f"Token 响应格式错误: {result}")
                    raise TTSError("Token 响应格式错误")
            else:
                logger.error(f"Token 获取失败: {response.status_code} - {response.text}")
                raise TTSError(f"Token 获取失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Token 获取异常: {e}", exc_info=True)
            raise TTSError(f"Token 获取失败: {str(e)}")

'''

# 在 _synthesize_edge 方法后插入
insert_pos = content.find('    def _synthesize_azure(self')
if insert_pos > 0:
    content = content[:insert_pos] + aliyun_method + '\n' + content[insert_pos:]
else:
    # 如果找不到 azure 方法，就加在文件末尾
    content += aliyun_method

# 写回
with open('core/tts_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 阿里云 TTS 实现完成 (HTTP API)")
print("\n下一步：")
print("1. 编辑 config.py，填入阿里云密钥")
print("2. 运行测试")
