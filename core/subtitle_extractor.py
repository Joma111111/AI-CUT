"""
字幕提取器
功能：使用Whisper从视频中提取字幕
"""

import os
import ffmpeg
import requests
from typing import List, Dict, Optional
from pathlib import Path
from utils.logger import get_logger
from .exceptions import SubtitleExtractionError
import config

logger = get_logger(__name__)


class SubtitleExtractor:
    """字幕提取器"""
    
    def __init__(self, 
                 model_size: str = "base",
                 language: str = "zh",
                 use_gpu: bool = False,
                 use_online: bool = None):
        """
        初始化字幕提取器
        
        Args:
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
            language: 识别语言
            use_gpu: 是否使用GPU（设为False使用CPU）
            use_online: 是否使用在线API（None则使用config配置）
        """
        self.model_size = model_size
        self.language = language
        self.use_gpu = use_gpu
        self.use_online = use_online if use_online is not None else getattr(config, 'USE_ONLINE_WHISPER', False)
        self.model = None
        
        # ⚠️ 关键修改：不在这里导入 whisper
        # 只有在需要本地模型时才导入
        
        logger.info(f"字幕提取器初始化: model={model_size}, language={language}, use_gpu={use_gpu}, use_online={self.use_online}")
    
    def _load_model(self):
        """加载Whisper模型"""
        if self.model is None and not self.use_online:
            logger.info(f"加载Whisper模型: {self.model_size}")
            
            # ⚠️ 延迟导入：只有在这里才导入 whisper
            try:
                import whisper
            except ImportError as e:
                raise SubtitleExtractionError(f"Whisper 库未安装: {str(e)}")
            
            # 强制使用 CPU，避免 PyTorch CUDA/DLL 问题
            device = "cpu"
            
            self.model = whisper.load_model(self.model_size, device=device)
            logger.info(f"模型加载完成 (device={device})")
    
    def extract(self, video_path: str,
                output_format: str = "srt",
                progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        从视频中提取字幕
        
        Args:
            video_path: 视频路径
            output_format: 输出格式 (srt, vtt, txt, json)
            progress_callback: 进度回调
            
        Returns:
            字幕列表 [{'start': 0.0, 'end': 1.5, 'text': '你好'}]
            
        Raises:
            SubtitleExtractionError: 提取失败时抛出
        """
        logger.info(f"开始提取字幕: {video_path}")
        
        try:
            # 1. 提取音频
            if progress_callback:
                progress_callback(10)
            
            audio_path = self._extract_audio(video_path)
            
            if progress_callback:
                progress_callback(30)
            
            # 2. 根据配置选择在线或本地识别
            if self.use_online:
                logger.info("正在调用在线 Whisper API 转录音频...")
                subtitles = self._call_whisper_api(audio_path)
            else:
                logger.info("正在使用本地 Whisper 模型转录音频...")
                self._load_model()  # ⚠️ 只有走本地模式才会导入 whisper
                result = self.model.transcribe(
                    audio_path,
                    language=self.language,
                    task="transcribe",
                    verbose=False
                )
                subtitles = self._process_result(result)
            
            if progress_callback:
                progress_callback(90)
            
            # 3. 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"字幕提取完成: {len(subtitles)} 个片段")
            return subtitles
            
        except Exception as e:
            logger.error(f"字幕提取失败: {str(e)}", exc_info=True)
            raise SubtitleExtractionError(f"字幕提取失败: {str(e)}")
    
    def _call_whisper_api(self, audio_path: str) -> List[Dict]:
        """
        调用在线 Whisper API
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            字幕列表
        """
        try:
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(audio_path), f, 'audio/wav')
                }
                
                data = {
                    'model': getattr(config, 'WHISPER_MODEL', 'whisper-1'),
                    'language': self.language,
                    'response_format': 'verbose_json',
                    'timestamp_granularities': ['segment']
                }
                
                headers = {
                    'Authorization': f'Bearer {config.API_KEY}'
                }
                
                # 调用 API
                logger.info(f"调用 Whisper API: {config.API_BASE_URL}/audio/transcriptions")
                
                response = requests.post(
                    f"{config.API_BASE_URL}/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=300
                )
                
                response.raise_for_status()
                result = response.json()
            
            # 解析结果
            subtitles = []
            
            if 'segments' in result:
                for idx, segment in enumerate(result['segments']):
                    subtitles.append({
                        'id': idx,
                        'start': segment.get('start', 0),
                        'end': segment.get('end', 0),
                        'text': segment.get('text', '').strip(),
                        'confidence': segment.get('avg_logprob', 0),
                    })
            else:
                # 如果没有分段信息，创建单个字幕
                text = result.get('text', '')
                if text:
                    subtitles.append({
                        'id': 0,
                        'start': 0.0,
                        'end': 0.0,
                        'text': text.strip(),
                        'confidence': 0,
                    })
            
            return subtitles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Whisper API 调用失败: {str(e)}")
            raise SubtitleExtractionError(f"Whisper API 调用失败: {str(e)}")
        except Exception as e:
            logger.error(f"字幕解析失败: {str(e)}")
            raise SubtitleExtractionError(f"字幕解析失败: {str(e)}")
    
    def extract_segment(self,
                       video_path: str,
                       start_time: float,
                       end_time: float) -> str:
        """
        提取指定时间段的对白
        
        Args:
            video_path: 视频路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            
        Returns:
            对白文本
        """
        logger.info(f"提取片段对白: {start_time:.2f}s - {end_time:.2f}s")
        
        try:
            # 1. 提取该时间段的音频
            audio_path = self._extract_audio_segment(
                video_path, 
                start_time, 
                end_time
            )
            
            # 2. 根据配置选择在线或本地识别
            if self.use_online:
                subtitles = self._call_whisper_api(audio_path)
                text = " ".join([sub['text'] for sub in subtitles])
            else:
                self._load_model()  # ⚠️ 只有走本地模式才会导入 whisper
                result = self.model.transcribe(
                    audio_path,
                    language=self.language,
                    verbose=False
                )
                text = result.get('text', '').strip()
            
            # 3. 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            logger.info(f"片段对白提取完成: {len(text)} 字")
            return text
        
        except Exception as e:
            logger.warning(f"片段对白提取失败: {str(e)}")
            return ""
    
    def _extract_audio(self, video_path: str) -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频路径
            
        Returns:
            音频文件路径
        """
        logger.info("提取音频...")
        
        # 生成临时音频文件路径
        audio_path = str(Path(config.TEMP_DIR) / f"temp_audio_{os.getpid()}.wav")
        Path(config.TEMP_DIR).mkdir(parents=True, exist_ok=True)
        
        try:
            # 使用ffmpeg提取音频
            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"音频提取完成: {audio_path}")
            return audio_path
            
        except Exception as e:
            raise SubtitleExtractionError(f"音频提取失败: {str(e)}")
    
    def _extract_audio_segment(self,
                              video_path: str,
                              start_time: float,
                              end_time: float) -> str:
        """提取音频片段"""
        logger.info(f"提取音频片段: {start_time:.2f}s - {end_time:.2f}s")
        
        # 生成临时音频文件路径
        audio_path = str(Path(config.TEMP_DIR) / f"temp_audio_segment_{os.getpid()}.wav")
        Path(config.TEMP_DIR).mkdir(parents=True, exist_ok=True)
        
        try:
            duration = end_time - start_time
            
            # 使用ffmpeg提取音频片段
            (
                ffmpeg
                .input(video_path, ss=start_time, t=duration)
                .output(audio_path, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return audio_path
        
        except Exception as e:
            raise SubtitleExtractionError(f"音频片段提取失败: {str(e)}")
    
    def _process_result(self, result: Dict) -> List[Dict]:
        """
        处理Whisper识别结果
        
        Args:
            result: Whisper原始结果
            
        Returns:
            字幕列表 [{'start': 0.0, 'end': 1.5, 'text': '你好'}]
        """
        segments = []
        
        for segment in result['segments']:
            segments.append({
                'id': segment['id'],
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'confidence': segment.get('avg_logprob', 0),
            })
        
        return segments
    
    def export_srt(self, subtitles: List[Dict], output_path: str):
        """
        导出为SRT格式
        
        Args:
            subtitles: 字幕列表
            output_path: 输出路径
        """
        logger.info(f"导出SRT字幕: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for idx, segment in enumerate(subtitles, 1):
                # 序号
                f.write(f"{idx}\n")
                
                # 时间轴
                start_time = self._format_timestamp(segment['start'])
                end_time = self._format_timestamp(segment['end'])
                f.write(f"{start_time} --> {end_time}\n")
                
                # 文本
                f.write(f"{segment['text']}\n\n")
    
    def export_vtt(self, subtitles: List[Dict], output_path: str):
        """
        导出为VTT格式
        
        Args:
            subtitles: 字幕列表
            output_path: 输出路径
        """
        logger.info(f"导出VTT字幕: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for segment in subtitles:
                # 时间轴
                start_time = self._format_timestamp(segment['start'], vtt=True)
                end_time = self._format_timestamp(segment['end'], vtt=True)
                f.write(f"{start_time} --> {end_time}\n")
                
                # 文本
                f.write(f"{segment['text']}\n\n")
    
    def export_txt(self, subtitles: List[Dict], output_path: str):
        """
        导出为纯文本格式
        
        Args:
            subtitles: 字幕列表
            output_path: 输出路径
        """
        logger.info(f"导出TXT字幕: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            text = " ".join([seg['text'] for seg in subtitles])
            f.write(text)
    
    def _format_timestamp(self, seconds: float, vtt: bool = False) -> str:
        """
        格式化时间戳
        
        Args:
            seconds: 秒数
            vtt: 是否为VTT格式
            
        Returns:
            格式化的时间戳
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        if vtt:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def align_with_scenes(self, subtitles: List[Dict], 
                         scenes: List[Dict]) -> List[Dict]:
        """
        将字幕与镜头对齐
        
        Args:
            subtitles: 字幕列表
            scenes: 镜头列表
            
        Returns:
            每个镜头对应的字幕文本
        """
        logger.info("对齐字幕与镜头")
        
        aligned = []
        
        for scene in scenes:
            scene_text = []
            
            for segment in subtitles:
                # 检查字幕是否在镜头时间范围内
                if (segment['start'] >= scene['start_time'] and segment['start'] < scene['end_time']) or \
                   (segment['end'] > scene['start_time'] and segment['end'] <= scene['end_time']) or \
                   (segment['start'] <= scene['start_time'] and segment['end'] >= scene['end_time']):
                    scene_text.append(segment['text'])
            
            aligned.append({
                'scene_id': scene['id'],
                'text': ' '.join(scene_text),
                'segments': len(scene_text),
            })
        
        return aligned
