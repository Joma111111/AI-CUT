"""
剧本分析器
功能：识别画面 + 提取对白 → 生成完整剧本
"""

import os
import json
import base64
import requests
from typing import List, Dict, Optional
from utils.logger import get_logger
from .exceptions import ScriptGenerationError
from .subtitle_extractor import SubtitleExtractor
import config

logger = get_logger(__name__)


class ScriptAnalyzer:
    """剧本分析器"""
    
    def __init__(self, whisper_model: str = "base"):
        """
        初始化剧本分析器
        
        Args:
            whisper_model: Whisper 模型名称 (tiny, base, small, medium, large)
        """
        self.whisper_model = whisper_model
        self.subtitle_extractor = SubtitleExtractor(
            model_size=whisper_model,
            use_online=getattr(config, 'USE_ONLINE_WHISPER', False)
        )
        
        logger.info(f"剧本分析器初始化完成 (Whisper: {whisper_model})")
    
    def analyze_scenes(self, 
                      scenes: List[Dict],
                      keyframes: List[Dict],
                      video_path: str,
                      output_path: str,
                      progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        分析所有镜头，生成完整剧本
        
        Args:
            scenes: 镜头列表（可能是筛选后的）
            keyframes: 关键帧列表
            video_path: 视频路径
            output_path: 输出路径（JSON）
            progress_callback: 进度回调
            
        Returns:
            剧本列表（每个镜头的画面描述+对白+时间戳）
        """
        logger.info(f"开始生成剧本: {len(scenes)} 个镜头")
        
        script_data = []
        
        # 1. 提取整个视频的字幕
        logger.info("正在提取视频字幕...")
        try:
            if progress_callback:
                progress_callback(10)
            
            all_subtitles = self.subtitle_extractor.extract(
                video_path, 
                progress_callback=lambda p: progress_callback(10 + p * 0.3) if progress_callback else None
            )
            
            logger.info(f"字幕提取完成: {len(all_subtitles)} 条")
            
            if progress_callback:
                progress_callback(40)
        
        except Exception as e:
            logger.error(f"字幕提取失败: {e}")
            all_subtitles = []
        
        # 2. 分析每个镜头
        for idx, scene in enumerate(scenes):
            # ✅ 兼容两种ID格式
            scene_id = scene.get('selected_id') or scene.get('id')
            
            # 找到该镜头的关键帧
            scene_keyframes = [
                kf for kf in keyframes 
                if kf.get('scene_id') == scene_id or kf.get('scene_id') == scene.get('id')
            ]
            
            # ✅ 如果没有找到，尝试按索引匹配
            if not scene_keyframes and idx < len(keyframes):
                scene_keyframes = [keyframes[idx]]
            
            if not scene_keyframes:
                logger.warning(f"镜头 {scene_id} 没有关键帧，跳过")
                continue
            
            # 分析该镜头
            try:
                scene_script = self._analyze_single_scene(
                    scene, 
                    scene_keyframes,
                    video_path,
                    all_subtitles
                )
                
                script_data.append(scene_script)
                
                logger.info(f"✅ 镜头 {scene_id} 分析完成")
                
            except Exception as e:
                logger.error(f"❌ 镜头 {scene_id} 分析失败: {str(e)}")
                continue
            
            if progress_callback:
                progress = 40 + (idx + 1) / len(scenes) * 60
                progress_callback(progress)
        
        # 3. 保存剧本
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"剧本生成完成: {output_path}")
        return script_data
    
    def _analyze_single_scene(self,
                             scene: Dict,
                             keyframes: List[Dict],
                             video_path: str,
                             all_subtitles: List[Dict]) -> Dict:
        """分析单个镜头"""
        
        # ✅ 兼容两种ID格式
        scene_id = scene.get('selected_id') or scene.get('id')
        
        # 1. 使用 Gemini 识别画面
        visual_description = self._analyze_visual_with_gemini(scene, keyframes)
        
        # 2. 提取该时间段的对白
        dialogue = self._extract_dialogue_from_subtitles(
            all_subtitles,
            scene['start_time'],
            scene['end_time']
        )
        
        return {
            'scene_id': scene_id,
            'start_time': scene['start_time'],
            'end_time': scene['end_time'],
            'duration': scene['duration'],
            'visual_description': visual_description,
            'dialogue': dialogue,
            'keyframes': [kf['image_path'] for kf in keyframes]
        }
    
    def _analyze_visual_with_gemini(self, scene: Dict, keyframes: List[Dict]) -> str:
        """使用 Gemini 2.5 识别画面"""
        
        if not keyframes:
            return "无画面描述"
        
        # 取第一个关键帧（代表性最强）
        keyframe_path = keyframes[0]['image_path']
        
        try:
            # 读取图片并转为 base64
            with open(keyframe_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 调用 Gemini API
            logger.info(f"调用 Gemini API 识别画面: {keyframe_path}")
            
            response = requests.post(
                f"{config.API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": getattr(config, 'VISION_MODEL', 'gemini-2.5-flash-lite'),
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "请用一句话描述这个画面中的主要内容，包括：人物、动作、场景、氛围。要简洁准确。"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 150
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            description = result['choices'][0]['message']['content'].strip()
            logger.info(f"画面识别完成: {description[:50]}...")
            
            return description
        
        except Exception as e:
            logger.error(f"画面识别失败: {str(e)}")
            # 降级方案：使用简单描述
            scene_id = scene.get('selected_id') or scene.get('id')
            duration = scene['duration']
            frame_count = len(keyframes)
            return f"镜头 {scene_id}：时长 {duration:.1f} 秒，{frame_count} 个关键帧"
    
    def _extract_dialogue_from_subtitles(self,
                                        all_subtitles: List[Dict],
                                        start_time: float,
                                        end_time: float) -> str:
        """从完整字幕中提取该时间段的对白"""
        
        # 筛选该时间段的字幕
        scene_subtitles = [
            sub for sub in all_subtitles
            if (sub['start'] >= start_time and sub['start'] < end_time) or
               (sub['end'] > start_time and sub['end'] <= end_time) or
               (sub['start'] <= start_time and sub['end'] >= end_time)
        ]
        
        if not scene_subtitles:
            return ""
        
        # 合并对白
        dialogue = " ".join([sub['text'] for sub in scene_subtitles])
        return dialogue.strip()
