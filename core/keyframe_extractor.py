"""
关键帧提取器
功能：从视频镜头中智能提取关键帧
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import hashlib
from utils.logger import get_logger
from .exceptions import KeyframeExtractionError
import config

logger = get_logger(__name__)


class KeyframeExtractor:
    """关键帧提取器"""
    
    def __init__(self, 
                 mode: str = "medium",
                 max_frames_per_scene: int = 3,
                 use_gpu: bool = False):
        """
        初始化关键帧提取器
        
        Args:
            mode: 提取模式 (low, medium, high, custom)
            max_frames_per_scene: 每个镜头最大关键帧数
            use_gpu: 是否使用GPU加速
        """
        self.mode = mode
        self.max_frames_per_scene = max_frames_per_scene
        self.use_gpu = use_gpu
        
        # 根据模式设置参数
        self.mode_configs = {
            'low': {'interval': 3.0, 'quality_threshold': 0.3},
            'medium': {'interval': 2.0, 'quality_threshold': 0.5},
            'high': {'interval': 1.0, 'quality_threshold': 0.7},
        }
        
        logger.info(f"关键帧提取器初始化: mode={mode}, max_frames={max_frames_per_scene}")
    
    def extract(self, video_path: str, 
                scenes: List[Dict],
                output_dir: Optional[str] = None,
                prefix: str = '',
                progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        提取关键帧
        
        Args:
            video_path: 视频路径
            scenes: 镜头列表
            output_dir: 输出目录（如果需要保存图片）
            prefix: 文件名前缀
            progress_callback: 进度回调
            
        Returns:
            关键帧列表，每个包含scene_id, time, frame_number, image_path等
            
        Raises:
            KeyframeExtractionError: 提取失败时抛出
        """
        logger.info(f"开始提取关键帧: {len(scenes)} 个镜头")
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise KeyframeExtractionError("无法打开视频文件")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            all_keyframes = []
            
            # 创建输出目录
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            for i, scene in enumerate(scenes):
                # 提取该镜头的关键帧
                keyframes = self._extract_from_scene(
                    cap, scene, fps, output_dir, prefix
                )
                all_keyframes.extend(keyframes)
                
                if progress_callback:
                    progress = (i + 1) / len(scenes) * 100
                    progress_callback(progress)
            
            cap.release()
            
            logger.info(f"关键帧提取完成: 共 {len(all_keyframes)} 帧")
            return all_keyframes
            
        except Exception as e:
            logger.error(f"关键帧提取失败: {str(e)}", exc_info=True)
            raise KeyframeExtractionError(f"关键帧提取失败: {str(e)}")
    
    def _extract_from_scene(self, cap: cv2.VideoCapture, 
                           scene: Dict, fps: float,
                           output_dir: Optional[str],
                           prefix: str = '') -> List[Dict]:
        """从单个镜头中提取关键帧"""
        
        # ✅ 兼容两种ID格式
        scene_id = scene.get('selected_id') or scene.get('id')
        scene_index = scene.get('index', scene_id)
        
        start_frame = scene['start_frame']
        end_frame = scene['end_frame']
        duration = scene['duration']
        
        # 根据模式确定采样策略
        if self.mode in self.mode_configs:
            config_params = self.mode_configs[self.mode]
            interval = config_params['interval']
            quality_threshold = config_params['quality_threshold']
        else:
            # 自定义模式
            interval = 2.0
            quality_threshold = 0.5
        
        # 计算采样点
        sample_times = []
        current_time = 0
        while current_time < duration and len(sample_times) < self.max_frames_per_scene:
            sample_times.append(scene['start_time'] + current_time)
            current_time += interval
        
        # 如果采样点太少，至少取首尾和中间
        if len(sample_times) < self.max_frames_per_scene:
            sample_times = [
                scene['start_time'],
                scene['start_time'] + duration / 2,
                scene['end_time'] - 0.1
            ][:self.max_frames_per_scene]
        
        # 提取帧并评估质量
        candidates = []
        for time_sec in sample_times:
            frame_number = int(time_sec * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # 评估帧质量
            quality_score = self._evaluate_frame_quality(frame)
            
            candidates.append({
                'time': time_sec,
                'frame_number': frame_number,
                'frame': frame,
                'quality_score': quality_score,
            })
        
        # 按质量排序并选择最好的
        candidates.sort(key=lambda x: x['quality_score'], reverse=True)
        selected = candidates[:self.max_frames_per_scene]
        
        # 按时间排序
        selected.sort(key=lambda x: x['time'])
        
        # 保存并生成结果
        keyframes = []
        for idx, candidate in enumerate(selected):
            keyframe = {
                'scene_id': scene_id,
                'scene_index': scene_index,
                'keyframe_index': idx,
                'time': candidate['time'],
                'frame_number': candidate['frame_number'],
                'quality_score': candidate['quality_score'],
            }
            
            # 保存图片
            if output_dir:
                filename = f"{prefix}{scene_id}_keyframe_{idx+1:02d}.jpg"
                image_path = Path(output_dir) / filename
                cv2.imwrite(str(image_path), candidate['frame'])
                keyframe['image_path'] = str(image_path)
            
            # 生成图片哈希（用于去重）
            keyframe['image_hash'] = self._calculate_image_hash(candidate['frame'])
            
            keyframes.append(keyframe)
        
        return keyframes
    
    def _evaluate_frame_quality(self, frame: np.ndarray) -> float:
        """
        评估帧的质量
        
        Args:
            frame: 图像帧
            
        Returns:
            质量评分 (0-1)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. 清晰度（拉普拉斯方差）
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        sharpness_score = min(sharpness / 1000, 1.0)
        
        # 2. 对比度
        contrast = gray.std()
        contrast_score = min(contrast / 80, 1.0)
        
        # 3. 亮度（接近127.5最好）
        brightness = gray.mean()
        brightness_score = 1.0 - abs(brightness - 127.5) / 127.5
        
        # 4. 色彩丰富度
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1].mean()
        color_score = saturation / 255.0
        
        # 综合评分
        total_score = (
            sharpness_score * 0.4 +
            contrast_score * 0.3 +
            brightness_score * 0.2 +
            color_score * 0.1
        )
        
        return round(total_score, 3)
    
    def _calculate_image_hash(self, frame: np.ndarray) -> str:
        """
        计算图像哈希（用于去重）
        
        Args:
            frame: 图像帧
            
        Returns:
            哈希值
        """
        # 缩小图像
        small = cv2.resize(frame, (8, 8), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        
        # 计算平均值
        avg = gray.mean()
        
        # 生成哈希
        hash_str = ''.join(['1' if pixel > avg else '0' for pixel in gray.flatten()])
        
        # 转换为十六进制
        hash_int = int(hash_str, 2)
        return format(hash_int, '016x')
    
    def remove_duplicates(self, keyframes: List[Dict], 
                         similarity_threshold: float = 0.9) -> List[Dict]:
        """
        去除重复的关键帧
        
        Args:
            keyframes: 关键帧列表
            similarity_threshold: 相似度阈值
            
        Returns:
            去重后的关键帧列表
        """
        if not keyframes:
            return keyframes
        
        unique_frames = []
        seen_hashes = set()
        
        for kf in keyframes:
            hash_val = kf.get('image_hash')
            
            if not hash_val or hash_val not in seen_hashes:
                unique_frames.append(kf)
                if hash_val:
                    seen_hashes.add(hash_val)
        
        logger.info(f"去重完成: {len(keyframes)} -> {len(unique_frames)}")
        return unique_frames
    
    def extract_custom(self, video_path: str, 
                      time_points: List[float],
                      output_dir: Optional[str] = None) -> List[Dict]:
        """
        在指定时间点提取关键帧
        
        Args:
            video_path: 视频路径
            time_points: 时间点列表（秒）
            output_dir: 输出目录
            
        Returns:
            关键帧列表
        """
        logger.info(f"在 {len(time_points)} 个指定时间点提取关键帧")
        
        cap = cv2.VideoCapture(video_path)
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            keyframes = []
            
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            for idx, time_sec in enumerate(time_points):
                frame_number = int(time_sec * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"无法读取时间点 {time_sec} 的帧")
                    continue
                
                keyframe = {
                    'keyframe_index': idx,
                    'time': time_sec,
                    'frame_number': frame_number,
                    'quality_score': self._evaluate_frame_quality(frame),
                    'image_hash': self._calculate_image_hash(frame),
                }
                
                # 保存图片
                if output_dir:
                    filename = f"keyframe_{idx+1:03d}.jpg"
                    image_path = Path(output_dir) / filename
                    cv2.imwrite(str(image_path), frame)
                    keyframe['image_path'] = str(image_path)
                
                keyframes.append(keyframe)
            
            return keyframes
            
        finally:
            cap.release()
