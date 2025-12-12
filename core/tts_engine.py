"""
语音合成引擎
功能：支持多种TTS引擎的语音合成
"""

import os
import asyncio
import edge_tts
from typing import Dict, List, Optional
from pathlib import Path
from pydub import AudioSegment
from utils.logger import get_logger
from .exceptions import TTSError
import config
import json
import hmac
import hashlib
import uuid
from datetime import datetime
from urllib.parse import quote

logger = get_logger(__name__)


class TTSEngine:
    """语音合成引擎"""
    
    def __init__(self, 
                 engine: str = "edge",
                 voice: Optional[str] = None):
        """
        初始化TTS引擎
        
        Args:
            engine: 引擎类型 (edge, azure, local)
            voice: 默认音色
        """
        self.engine = engine
        self.voice = voice or config.TTS_DEFAULT_VOICE
        
        # 可用音色列表
        self.available_voices = self._load_available_voices()
        
        logger.info(f"TTS引擎初始化: engine={engine}, voice={self.voice}")
    
    def _load_available_voices(self) -> Dict[str, Dict]:
        """加载可用音色列表"""
        # Edge TTS 中文音色
        voices = {
            'zh-CN-XiaoxiaoNeural': {
                'name': '晓晓',
                'gender': 'Female',
                'language': 'zh-CN',
                'description': '温柔甜美的女声',
            },
            'zh-CN-YunxiNeural': {
                'name': '云希',
                'gender': 'Male',
                'language': 'zh-CN',
                'description': '沉稳大气的男声',
            },
            'zh-CN-YunyangNeural': {
                'name': '云扬',
                'gender': 'Male',
                'language': 'zh-CN',
                'description': '年轻活力的男声',
            },
            'zh-CN-XiaoyiNeural': {
                'name': '晓伊',
                'gender': 'Female',
                'language': 'zh-CN',
                'description': '知性优雅的女声',
            },
            'zh-CN-YunjianNeural': {
                'name': '云健',
                'gender': 'Male',
                'language': 'zh-CN',
                'description': '成熟稳重的男声',
            },
            'zh-CN-XiaochenNeural': {
                'name': '晓辰',
                'gender': 'Female',
                'language': 'zh-CN',
                'description': '亲切自然的女声',
            },
        }
        
        return voices
    
    def synthesize(self, 
                  text: str,
                  output_path: str,
                  voice: Optional[str] = None,
                  rate: float = 1.0,
                  pitch: float = 1.0,
                  volume: float = 1.0) -> str:
        """
        合成语音
        
        Args:
            text: 文本内容
            output_path: 输出路径
            voice: 音色（None则使用默认）
            rate: 语速 (0.5-2.0)
            pitch: 音调 (0.5-2.0)
            volume: 音量 (0.0-1.0)
            
        Returns:
            输出文件路径
            
        Raises:
            TTSError: 合成失败时抛出
        """
        logger.info(f"开始合成语音: {len(text)} 字")
        
        voice = voice or self.voice
        
        try:
            if self.engine == "edge":
                return self._synthesize_edge(text, output_path, voice, rate, pitch, volume)
            elif self.engine == "aliyun":
                return self._synthesize_aliyun(text, output_path, voice, rate, pitch, volume)
            elif self.engine == "azure":
                return self._synthesize_azure(text, output_path, voice, rate, pitch, volume)
            elif self.engine == "local":
                return self._synthesize_local(text, output_path, voice, rate, pitch, volume)
            else:
                raise TTSError(f"不支持的引擎: {self.engine}")
                
        except Exception as e:
            logger.error(f"语音合成失败: {str(e)}", exc_info=True)
            raise TTSError(f"语音合成失败: {str(e)}")
    
    def _synthesize_edge(self, text: str, output_path: str,
                        voice: str, rate: float, pitch: float, volume: float) -> str:
        """使用Edge TTS合成"""
        
        # 格式化参数
        rate_str = f"{int((rate - 1) * 100):+d}%"
        pitch_str = f"{int((pitch - 1) * 50):+d}Hz"
        volume_str = f"{int((volume - 1) * 100):+d}%"
        
        async def _synthesize():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate_str,
                pitch=pitch_str,
                volume=volume_str
            )
            await communicate.save(output_path)
        
        # 运行异步任务
        asyncio.run(_synthesize())
        
        logger.info(f"Edge TTS合成完成: {output_path}")
        return output_path
    

    def _synthesize_aliyun(self, text: str, output_path: str,
                          voice: str, rate: float, pitch: float, volume: float) -> str:
        """使用阿里云 TTS 合成 (HTTP GET 方法)"""
        import requests
        from urllib.parse import quote
        
        try:
            # 获取 Token
            token = self._get_aliyun_token()
            
            # 参数处理
            voice_name = voice or getattr(config, 'ALIYUN_VOICE', 'xiaoyun')
            # 如果是 Edge TTS 音色，转换为阿里云音色
            if 'Neural' in voice_name or 'zh-CN' in voice_name:
                voice_name = 'xiaoyun'
            
            speech_rate = int((rate - 1) * 500)  # -500 到 500
            pitch_rate = int((pitch - 1) * 500)
            volume_val = int(volume * 100)  # 0 到 100
            
            # 文本需要 UTF-8 + urlencode 编码
            text_encoded = quote(text, safe='')
            
            # 构建 GET 请求 URL
            url = f"https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts"
            url += f"?appkey={config.ALIYUN_APP_KEY}"
            url += f"&token={token}"
            url += f"&text={text_encoded}"
            url += f"&format=mp3"
            url += f"&sample_rate=16000"
            url += f"&voice={voice_name}"
            url += f"&volume={volume_val}"
            url += f"&speech_rate={speech_rate}"
            url += f"&pitch_rate={pitch_rate}"
            
            logger.info(f"调用阿里云 TTS: voice={voice_name}, rate={speech_rate}, pitch={pitch_rate}, volume={volume_val}")
            
            # 发送 GET 请求
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # 检查响应类型
                content_type = response.headers.get('Content-Type', '')
                
                if 'audio' in content_type:
                    # 保存音频
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    logger.info(f"阿里云 TTS 合成完成: {output_path} ({len(response.content)} bytes)")
                    return output_path
                else:
                    # 错误响应
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', response.text)
                    except:
                        error_msg = response.text
                    
                    logger.error(f"阿里云 TTS 返回错误: {error_msg}")
                    raise TTSError(f"阿里云 TTS 错误: {error_msg}")
            else:
                logger.error(f"阿里云 TTS 请求失败: HTTP {response.status_code}")
                raise TTSError(f"阿里云 TTS 请求失败: HTTP {response.status_code}")
                
        except TTSError:
            raise
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


    def _synthesize_azure(self, text: str, output_path: str,
                         voice: str, rate: float, pitch: float, volume: float) -> str:
        """使用Azure TTS合成"""
        # TODO: 实现Azure TTS
        raise NotImplementedError("Azure TTS暂未实现")
    
    def _synthesize_local(self, text: str, output_path: str,
                         voice: str, rate: float, pitch: float, volume: float) -> str:
        """使用本地TTS合成"""
        # TODO: 实现本地TTS
        raise NotImplementedError("本地TTS暂未实现")
    
    def batch_synthesize(self, 
                        scripts: List[Dict],
                        output_dir: str,
                        voice: Optional[str] = None,
                        progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        批量合成语音（带限流和重试）
        
        Args:
            scripts: 文案列表
            output_dir: 输出目录
            voice: 音色
            progress_callback: 进度回调
            
        Returns:
            音频文件列表
        """
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        logger.info(f"批量合成语音: {len(scripts)} 个文案")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        results = []
        total = len(scripts)
        
        # 根据引擎类型决定并发策略
        if self.engine == "edge":
            # Edge TTS 需要限流，顺序执行
            max_workers = 1
            delay_between_requests = 1.5  # 每个请求间隔1.5秒
            max_retries = 3
            logger.info("使用 Edge TTS，启用限流模式（顺序执行）")
        else:
            # 阿里云可以并发
            max_workers = 5
            delay_between_requests = 0.1
            max_retries = 2
            logger.info(f"使用 {self.engine} TTS，启用并发模式（{max_workers} 线程）")
        
        def synthesize_one(script: Dict, idx: int) -> Dict:
            """合成单个音频（带重试）"""
            scene_id = script['scene_id']
            text = script['script']
            output_path = os.path.join(output_dir, f"{scene_id}_audio.mp3")
            
            # Edge TTS 限流：添加延迟
            if self.engine == "edge" and idx > 0:
                time.sleep(delay_between_requests)
            
            # 重试逻辑
            last_error = None
            for attempt in range(max_retries):
                try:
                    # 合成语音
                    self.synthesize(text, output_path, voice)
                    
                    # 验证文件
                    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                        raise TTSError("文件生成失败或为空")
                    
                    # 获取音频时长
                    audio = AudioSegment.from_file(output_path)
                    duration = len(audio) / 1000.0
                    
                    logger.info(f"✅ 合成成功 [{idx+1}/{total}] {scene_id} ({duration:.1f}s)")
                    
                    return {
                        'scene_id': scene_id,
                        'audio_path': output_path,
                        'duration': duration,
                        'text': text,
                        'success': True
                    }
                    
                except Exception as e:
                    last_error = str(e)
                    
                    if attempt < max_retries - 1:
                        # 指数退避
                        wait_time = (2 ** attempt) * delay_between_requests
                        logger.warning(f"⚠️  合成失败 {scene_id} (尝试 {attempt + 1}/{max_retries}): {e}，{wait_time:.1f}秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ 合成失败 {scene_id} (已重试 {max_retries} 次): {e}")
            
            # 所有重试都失败
            return {
                'scene_id': scene_id,
                'audio_path': None,
                'error': last_error,
                'success': False
            }
        
        # 执行合成
        if max_workers == 1:
            # 顺序执行（Edge TTS）
            for idx, script in enumerate(scripts):
                result = synthesize_one(script, idx)
                results.append(result)
                
                if progress_callback:
                    progress = (idx + 1) / total * 100
                    progress_callback(progress)
        else:
            # 并发执行（阿里云等）
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_idx = {
                    executor.submit(synthesize_one, script, idx): idx
                    for idx, script in enumerate(scripts)
                }
                
                # 收集结果
                completed = 0
                for future in as_completed(future_to_idx):
                    result = future.result()
                    results.append(result)
                    
                    completed += 1
                    if progress_callback:
                        progress = completed / total * 100
                        progress_callback(progress)
        
        # 统计结果
        success_count = len([r for r in results if r.get('success', False)])
        failed_count = total - success_count
        
        logger.info(f"批量合成完成: ✅ {success_count} 个成功, ❌ {failed_count} 个失败")
        
        return results
    
    def adjust_audio(self, 
                    input_path: str,
                    output_path: str,
                    speed: float = 1.0,
                    volume: float = 1.0) -> str:
        """
        调整音频参数
        
        Args:
            input_path: 输入路径
            output_path: 输出路径
            speed: 速度倍率
            volume: 音量倍率
            
        Returns:
            输出路径
        """
        logger.info(f"调整音频: speed={speed}, volume={volume}")
        
        audio = AudioSegment.from_file(input_path)
        
        # 调整速度
        if speed != 1.0:
            # 改变播放速度但不改变音调
            audio = audio._spawn(
                audio.raw_data,
                overrides={
                    "frame_rate": int(audio.frame_rate * speed)
                }
            ).set_frame_rate(audio.frame_rate)
        
        # 调整音量
        if volume != 1.0:
            change_in_dBFS = 20 * (volume - 1)
            audio = audio + change_in_dBFS
        
        # 导出
        audio.export(output_path, format="mp3")
        
        logger.info(f"音频调整完成: {output_path}")
        return output_path
    
    def merge_audios(self, 
                    audio_paths: List[str],
                    output_path: str,
                    crossfade: int = 0) -> str:
        """
        合并多个音频文件
        
        Args:
            audio_paths: 音频文件路径列表
            output_path: 输出路径
            crossfade: 交叉淡入淡出时长（毫秒）
            
        Returns:
            输出路径
        """
        logger.info(f"合并 {len(audio_paths)} 个音频文件")
        
        if not audio_paths:
            raise TTSError("没有音频文件可合并")
        
        # 加载第一个音频
        combined = AudioSegment.from_file(audio_paths[0])
        
        # 依次合并其他音频
        for audio_path in audio_paths[1:]:
            audio = AudioSegment.from_file(audio_path)
            
            if crossfade > 0:
                combined = combined.append(audio, crossfade=crossfade)
            else:
                combined = combined + audio
        
        # 导出
        combined.export(output_path, format="mp3")
        
        logger.info(f"音频合并完成: {output_path}")
        return output_path
    
    def add_background_music(self,
                           voice_path: str,
                           music_path: str,
                           output_path: str,
                           music_volume: float = 0.3) -> str:
        """
        添加背景音乐
        
        Args:
            voice_path: 语音文件路径
            music_path: 音乐文件路径
            output_path: 输出路径
            music_volume: 音乐音量（0-1）
            
        Returns:
            输出路径
        """
        logger.info("添加背景音乐")
        
        # 加载音频
        voice = AudioSegment.from_file(voice_path)
        music = AudioSegment.from_file(music_path)
        
        # 调整音乐音量
        music = music - (20 * (1 - music_volume))
        
        # 循环音乐以匹配语音长度
        if len(music) < len(voice):
            loops = (len(voice) // len(music)) + 1
            music = music * loops
        
        # 截取音乐
        music = music[:len(voice)]
        
        # 混合
        combined = voice.overlay(music)
        
        # 导出
        combined.export(output_path, format="mp3")
        
        logger.info(f"背景音乐添加完成: {output_path}")
        return output_path
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频时长
        
        Args:
            audio_path: 音频路径
            
        Returns:
            时长（秒）
        """
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
