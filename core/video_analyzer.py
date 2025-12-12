"""
视频分析器
功能：提取视频信息、元数据、质量分析等
"""

import os
import cv2
import ffmpeg
from typing import Dict, Optional, Tuple
from pathlib import Path
from utils.logger import get_logger
from .exceptions import VideoAnalysisError

logger = get_logger(__name__)


class VideoAnalyzer:
    """视频分析器"""
    
    def __init__(self, cache_enabled: bool = True):
        """
        初始化视频分析器
        
        Args:
            cache_enabled: 是否启用缓存
        """
        self.cache_enabled = cache_enabled
        self._cache = {}
        logger.info("视频分析器初始化完成")
    
    def analyze(self, video_path: str) -> Dict:
        """
        分析视频，提取所有信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            包含视频信息的字典
            
        Raises:
            VideoAnalysisError: 分析失败时抛出
        """
        logger.info(f"开始分析视频: {video_path}")
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            raise VideoAnalysisError(f"视频文件不存在: {video_path}")
        
        # 检查缓存
        if self.cache_enabled and video_path in self._cache:
            logger.info("使用缓存的分析结果")
            return self._cache[video_path]
        
        try:
            # 基础信息
            basic_info = self._get_basic_info(video_path)
            
            # 编码信息
            codec_info = self._get_codec_info(video_path)
            
            # 质量信息
            quality_info = self._get_quality_info(video_path)
            
            # 音频信息
            audio_info = self._get_audio_info(video_path)
            
            # 合并所有信息
            result = {
                **basic_info,
                **codec_info,
                **quality_info,
                **audio_info,
                'file_path': video_path,
                'file_name': os.path.basename(video_path),
                'file_size': os.path.getsize(video_path),
            }
            
            # 缓存结果
            if self.cache_enabled:
                self._cache[video_path] = result
            
            logger.info(f"视频分析完成: {result['duration']:.2f}秒, {result['width']}x{result['height']}")
            return result
            
        except Exception as e:
            logger.error(f"视频分析失败: {str(e)}", exc_info=True)
            raise VideoAnalysisError(f"视频分析失败: {str(e)}")
    
    def _get_basic_info(self, video_path: str) -> Dict:
        """获取基础信息"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise VideoAnalysisError("无法打开视频文件")
        
        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'aspect_ratio': f"{width}:{height}",
            }
        finally:
            cap.release()
    
    def _get_codec_info(self, video_path: str) -> Dict:
        """获取编码信息"""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                return {}
            
            return {
                'video_codec': video_stream.get('codec_name', 'unknown'),
                'video_codec_long': video_stream.get('codec_long_name', 'unknown'),
                'pixel_format': video_stream.get('pix_fmt', 'unknown'),
                'bit_rate': int(video_stream.get('bit_rate', 0)),
                'profile': video_stream.get('profile', 'unknown'),
            }
        except Exception as e:
            logger.warning(f"获取编码信息失败: {str(e)}")
            return {}
    
    def _get_quality_info(self, video_path: str) -> Dict:
        """获取质量信息"""
        cap = cv2.VideoCapture(video_path)
        
        try:
            # 读取几帧进行质量评估
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_count = min(10, frame_count)
            sample_indices = [int(i * frame_count / sample_count) for i in range(sample_count)]
            
            brightness_values = []
            contrast_values = []
            sharpness_values = []
            
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # 转换为灰度图
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 亮度
                brightness = gray.mean()
                brightness_values.append(brightness)
                
                # 对比度
                contrast = gray.std()
                contrast_values.append(contrast)
                
                # 清晰度（拉普拉斯方差）
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                sharpness = laplacian.var()
                sharpness_values.append(sharpness)
            
            return {
                'avg_brightness': sum(brightness_values) / len(brightness_values) if brightness_values else 0,
                'avg_contrast': sum(contrast_values) / len(contrast_values) if contrast_values else 0,
                'avg_sharpness': sum(sharpness_values) / len(sharpness_values) if sharpness_values else 0,
                'quality_score': self._calculate_quality_score(brightness_values, contrast_values, sharpness_values),
            }
        finally:
            cap.release()
    
    def _get_audio_info(self, video_path: str) -> Dict:
        """获取音频信息"""
        try:
            probe = ffmpeg.probe(video_path)
            audio_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'audio'),
                None
            )
            
            if not audio_stream:
                return {
                    'has_audio': False,
                }
            
            return {
                'has_audio': True,
                'audio_codec': audio_stream.get('codec_name', 'unknown'),
                'audio_channels': audio_stream.get('channels', 0),
                'audio_sample_rate': int(audio_stream.get('sample_rate', 0)),
                'audio_bit_rate': int(audio_stream.get('bit_rate', 0)),
            }
        except Exception as e:
            logger.warning(f"获取音频信息失败: {str(e)}")
            return {'has_audio': False}
    
    def _calculate_quality_score(self, brightness, contrast, sharpness) -> float:
        """
        计算视频质量评分（0-100）
        
        Args:
            brightness: 亮度值列表
            contrast: 对比度值列表
            sharpness: 清晰度值列表
            
        Returns:
            质量评分
        """
        if not brightness or not contrast or not sharpness:
            return 0.0
        
        # 归一化
        avg_brightness = sum(brightness) / len(brightness)
        avg_contrast = sum(contrast) / len(contrast)
        avg_sharpness = sum(sharpness) / len(sharpness)
        
        # 亮度评分（理想值127.5）
        brightness_score = 100 - abs(avg_brightness - 127.5) / 127.5 * 100
        
        # 对比度评分（越高越好，但有上限）
        contrast_score = min(avg_contrast / 80 * 100, 100)
        
        # 清晰度评分（越高越好，但有上限）
        sharpness_score = min(avg_sharpness / 1000 * 100, 100)
        
        # 综合评分
        total_score = (brightness_score * 0.3 + contrast_score * 0.3 + sharpness_score * 0.4)
        
        return round(total_score, 2)
    
    def get_frame_at_time(self, video_path: str, time_sec: float) -> Optional[cv2.Mat]:
        """
        获取指定时间的帧
        
        Args:
            video_path: 视频路径
            time_sec: 时间（秒）
            
        Returns:
            帧图像，失败返回None
        """
        cap = cv2.VideoCapture(video_path)
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(time_sec * fps)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            return frame if ret else None
        finally:
            cap.release()
    
    def get_thumbnail(self, video_path: str, time_sec: float = 0, 
                     size: Tuple[int, int] = (320, 180)) -> Optional[cv2.Mat]:
        """
        获取视频缩略图
        
        Args:
            video_path: 视频路径
            time_sec: 时间（秒）
            size: 缩略图大小
            
        Returns:
            缩略图，失败返回None
        """
        frame = self.get_frame_at_time(video_path, time_sec)
        
        if frame is None:
            return None
        
        # 调整大小
        thumbnail = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
        return thumbnail
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("缓存已清除")
