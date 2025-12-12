"""
视频处理器
功能：视频合成、剪辑、转码等
"""

import os
import ffmpeg
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from utils.logger import get_logger
from .exceptions import VideoProcessingError
import config

logger = get_logger(__name__)


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """
        初始化视频处理器
        
        Args:
            ffmpeg_path: FFmpeg可执行文件路径
        """
        self.ffmpeg_path = ffmpeg_path or config.FFMPEG_PATH
        logger.info("视频处理器初始化完成")
    
    def compose(self,
               video_path: str,
               audio_segments: List[Dict],
               output_path: str,
               scenes: List[Dict],
               progress_callback: Optional[callable] = None) -> str:
        """
        合成最终视频（视频+解说音频）
        
        Args:
            video_path: 原视频路径
            audio_segments: 音频片段列表
            output_path: 输出路径
            scenes: 镜头列表
            progress_callback: 进度回调
            
        Returns:
            输出文件路径
            
        Raises:
            VideoProcessingError: 处理失败时抛出
        """
        logger.info(f"开始合成视频: {output_path}")
        
        try:
            # 创建临时目录
            temp_dir = Path(config.TEMP_DIR) / f"compose_{os.getpid()}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. 提取原视频音频（如果有）
            original_audio = None
            if self._has_audio(video_path):
                original_audio = str(temp_dir / "original_audio.aac")
                self._extract_audio(video_path, original_audio)
            
            # 2. 创建解说音频时间轴
            narration_audio = str(temp_dir / "narration.mp3")
            self._create_narration_timeline(audio_segments, scenes, narration_audio)
            
            # 3. 混合音频（原音+解说）
            if original_audio:
                mixed_audio = str(temp_dir / "mixed_audio.mp3")
                self._mix_audios(original_audio, narration_audio, mixed_audio)
            else:
                mixed_audio = narration_audio
            
            # 4. 合成最终视频
            self._merge_video_audio(video_path, mixed_audio, output_path)
            
            # 5. 清理临时文件
            self._cleanup_temp_files(temp_dir)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"视频合成完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"视频合成失败: {str(e)}", exc_info=True)
            raise VideoProcessingError(f"视频合成失败: {str(e)}")
    
    def _has_audio(self, video_path: str) -> bool:
        """检查视频是否有音频"""
        try:
            probe = ffmpeg.probe(video_path)
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            return len(audio_streams) > 0
        except:
            return False
    
    def _extract_audio(self, video_path: str, output_path: str):
        """提取视频音频"""
        logger.info("提取原视频音频")
        
        (
            ffmpeg
            .input(video_path)
            .output(output_path, acodec='aac', audio_bitrate='192k')
            .overwrite_output()
            .run(quiet=True)
        )
    
    def _create_narration_timeline(self,
                                  audio_segments: List[Dict],
                                  scenes: List[Dict],
                                  output_path: str):
        """创建解说音频时间轴"""
        logger.info("创建解说音频时间轴")
        
        from pydub import AudioSegment
        
        # 获取视频总时长
        total_duration = scenes[-1]['end_time'] if scenes else 0
        
        # 创建空白音频
        silence = AudioSegment.silent(duration=int(total_duration * 1000))
        
        # 将各段解说音频插入到对应时间点
        for segment in audio_segments:
            if not segment.get('audio_path'):
                continue
            
            # 找到对应的镜头
            scene = next((s for s in scenes if s['id'] == segment['scene_id']), None)
            if not scene:
                continue
            
            # 加载音频
            audio = AudioSegment.from_file(segment['audio_path'])
            
            # 插入到时间轴
            start_ms = int(scene['start_time'] * 1000)
            silence = silence.overlay(audio, position=start_ms)
        
        # 导出
        silence.export(output_path, format="mp3")
    
    def _mix_audios(self, audio1_path: str, audio2_path: str, 
                   output_path: str, ratio: float = 0.3):
        """
        混合两个音频
        
        Args:
            audio1_path: 音频1（原音）
            audio2_path: 音频2（解说）
            output_path: 输出路径
            ratio: 音频1的音量比例
        """
        logger.info("混合音频")
        
        (
            ffmpeg
            .filter([
                ffmpeg.input(audio1_path).audio,
                ffmpeg.input(audio2_path).audio
            ], 'amix', inputs=2, duration='longest', weights=f'{ratio} {1-ratio}')
            .output(output_path)
            .overwrite_output()
            .run(quiet=True)
        )
    
    def _merge_video_audio(self, video_path: str, audio_path: str, output_path: str):
        """合并视频和音频"""
        logger.info("合并视频和音频")
        
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)
        
        (
            ffmpeg
            .output(
                video.video,
                audio.audio,
                output_path,
                vcodec='copy',
                acodec='aac',
                audio_bitrate='192k'
            )
            .overwrite_output()
            .run(quiet=True)
        )
    
    def cut_video(self, 
                 video_path: str,
                 start_time: float,
                 end_time: float,
                 output_path: str) -> str:
        """
        剪切视频片段
        
        Args:
            video_path: 视频路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            output_path: 输出路径
            
        Returns:
            输出路径
        """
        logger.info(f"剪切视频: {start_time}s - {end_time}s")
        
        duration = end_time - start_time
        
        (
            ffmpeg
            .input(video_path, ss=start_time, t=duration)
            .output(output_path, vcodec='copy', acodec='copy')
            .overwrite_output()
            .run(quiet=True)
        )
        
        return output_path
    
    def concat_videos(self, 
                     video_paths: List[str],
                     output_path: str) -> str:
        """
        拼接多个视频
        
        Args:
            video_paths: 视频路径列表
            output_path: 输出路径
            
        Returns:
            输出路径
        """
        logger.info(f"拼接 {len(video_paths)} 个视频")
        
        # 创建concat文件
        concat_file = Path(config.TEMP_DIR) / f"concat_{os.getpid()}.txt"
        with open(concat_file, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{os.path.abspath(video_path)}'\n")
        
        # 拼接
        (
            ffmpeg
            .input(str(concat_file), format='concat', safe=0)
            .output(output_path, c='copy')
            .overwrite_output()
            .run(quiet=True)
        )
        
        # 清理
        concat_file.unlink()
        
        return output_path
    
    def add_subtitle(self,
                    video_path: str,
                    subtitle_path: str,
                    output_path: str,
                    font_size: int = 24,
                    font_color: str = 'white') -> str:
        """
        添加字幕
        
        Args:
            video_path: 视频路径
            subtitle_path: 字幕文件路径（SRT格式）
            output_path: 输出路径
            font_size: 字体大小
            font_color: 字体颜色
            
        Returns:
            输出路径
        """
        logger.info("添加字幕")
        
        (
            ffmpeg
            .input(video_path)
            .output(
                output_path,
                vf=f"subtitles={subtitle_path}:force_style='FontSize={font_size},PrimaryColour={font_color}'"
            )
            .overwrite_output()
            .run(quiet=True)
        )
        
        return output_path
    
    def convert_format(self,
                      input_path: str,
                      output_path: str,
                      format: str = 'mp4',
                      quality: str = 'high') -> str:
        """
        转换视频格式
        
        Args:
            input_path: 输入路径
            output_path: 输出路径
            format: 输出格式
            quality: 质量 (low, medium, high)
            
        Returns:
            输出路径
        """
        logger.info(f"转换视频格式: {format}, 质量: {quality}")
        
        # 质量参数
        quality_params = {
            'low': {'crf': 28, 'preset': 'fast'},
            'medium': {'crf': 23, 'preset': 'medium'},
            'high': {'crf': 18, 'preset': 'slow'},
        }
        
        params = quality_params.get(quality, quality_params['medium'])
        
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                vcodec='libx264',
                acodec='aac',
                **params
            )
            .overwrite_output()
            .run(quiet=True)
        )
        
        return output_path
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        获取视频信息
        
        Args:
            video_path: 视频路径
            
        Returns:
            视频信息字典
        """
        probe = ffmpeg.probe(video_path)
        
        video_stream = next(
            (s for s in probe['streams'] if s['codec_type'] == 'video'),
            None
        )
        
        audio_stream = next(
            (s for s in probe['streams'] if s['codec_type'] == 'audio'),
            None
        )
        
        return {
            'duration': float(probe['format']['duration']),
            'size': int(probe['format']['size']),
            'bit_rate': int(probe['format']['bit_rate']),
            'video': {
                'codec': video_stream['codec_name'] if video_stream else None,
                'width': video_stream['width'] if video_stream else None,
                'height': video_stream['height'] if video_stream else None,
                'fps': eval(video_stream['r_frame_rate']) if video_stream else None,
            },
            'audio': {
                'codec': audio_stream['codec_name'] if audio_stream else None,
                'sample_rate': audio_stream['sample_rate'] if audio_stream else None,
                'channels': audio_stream['channels'] if audio_stream else None,
            } if audio_stream else None,
        }
    
    def _cleanup_temp_files(self, temp_dir: Path):
        """清理临时文件"""
        try:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.info("临时文件清理完成")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")
