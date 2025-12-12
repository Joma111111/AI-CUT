"""
多模态特征融合器
整合视觉、OCR、语音、人脸等多模态信息
"""

import os
from typing import List, Dict
import json


class MultimodalFusion:
    """多模态特征融合器"""
    
    def fuse_multimodal_data(
        self,
        scenes: List[Dict],
        vision_results: List[Dict],
        ocr_results: List[Dict],
        face_results: List[Dict],
        subtitles: List[Dict]
    ) -> List[Dict]:
        """
        融合多模态数据
        
        Args:
            scenes: 场景列表（来自PySceneDetect）
            vision_results: 视觉分析结果（来自CLIP/BLIP-2）
            ocr_results: OCR识别结果
            face_results: 人脸识别结果
            subtitles: 字幕/对白
        
        Returns:
            融合后的场景数据
            [
                {
                    'id': 1,
                    'start_time': 10.0,
                    'end_time': 17.0,
                    'duration': 7.0,
                    
                    # 视觉信息
                    'visual': {
                        'clip_labels': ['logo', 'clouds'],
                        'blip2_caption': 'A Legendary logo in the clouds',
                        'motion_score': 0.3
                    },
                    
                    # OCR信息
                    'ocr': {
                        'texts': ['LEGENDARY PICTURES']
                    },
                    
                    # 人脸信息
                    'faces': [],
                    
                    # 对白信息
                    'dialogue': '',
                    
                    # 综合得分（用于筛选精彩片段）
                    'highlight_score': 45.0
                }
            ]
        """
        fused_scenes = []
        
        for scene in scenes:
            start = scene['start_time']
            end = scene['end_time']
            
            # 找到该场景时间范围内的所有信息
            scene_vision = self._get_data_in_range(vision_results, start, end)
            scene_ocr = self._get_data_in_range(ocr_results, start, end)
            scene_faces = self._get_data_in_range(face_results, start, end)
            scene_dialogue = self._get_dialogue_in_range(subtitles, start, end)
            
            # 融合数据
            fused_scene = {
                **scene,
                'visual': self._merge_vision_data(scene_vision),
                'ocr': self._merge_ocr_data(scene_ocr),
                'faces': self._merge_face_data(scene_faces),
                'dialogue': scene_dialogue,
            }
            
            # 计算综合得分
            fused_scene['highlight_score'] = self._calculate_highlight_score(fused_scene)
            
            fused_scenes.append(fused_scene)
        
        return fused_scenes
    
    def _get_data_in_range(
        self,
        data_list: List[Dict],
        start: float,
        end: float
    ) -> List[Dict]:
        """获取时间范围内的数据"""
        return [
            item for item in data_list
            if start <= item['timestamp'] <= end
        ]
    
    def _get_dialogue_in_range(
        self,
        subtitles: List[Dict],
        start: float,
        end: float
    ) -> str:
        """获取时间范围内的对白"""
        dialogues = []
        
        for sub in subtitles:
            if sub['start'] >= start and sub['end'] <= end:
                dialogues.append(sub['text'])
        
        return ' '.join(dialogues)
    
    def _merge_vision_data(self, vision_data: List[Dict]) -> Dict:
        """合并视觉数据"""
        if not vision_data:
            return {}
        
        # 取最具代表性的一帧（通常是中间帧）
        mid_frame = vision_data[len(vision_data) // 2]
        
        return {
            'clip_labels': mid_frame.get('clip_labels', []),
            'blip2_caption': mid_frame.get('blip2_caption', ''),
            'motion_score': mid_frame.get('motion_score', 0.0)
        }
    
    def _merge_ocr_data(self, ocr_data: List[Dict]) -> Dict:
        """合并OCR数据"""
        all_texts = []
        
        for item in ocr_data:
            for text_info in item.get('texts', []):
                all_texts.append(text_info['text'])
        
        # 去重
        unique_texts = list(set(all_texts))
        
        return {'texts': unique_texts}
    
    def _merge_face_data(self, face_data: List[Dict]) -> List[Dict]:
        """合并人脸数据"""
        all_faces = []
        
        for item in face_data:
            all_faces.extend(item.get('faces', []))
        
        return all_faces
    
    def _calculate_highlight_score(self, scene: Dict) -> float:
        """
        计算场景的精彩度得分
        
        评分标准：
        1. 对白密度 (30%)
        2. 画面动作 (25%)
        3. 人物出现 (20%)
        4. 特殊元素 (15%) - 如文字、Logo
        5. 场景时长 (10%)
        """
        score = 0
        
        # 1. 对白密度
        dialogue_len = len(scene.get('dialogue', ''))
        dialogue_score = min(dialogue_len / scene['duration'] / 10 * 100, 100)
        score += dialogue_score * 0.3
        
        # 2. 画面动作
        motion_score = scene.get('visual', {}).get('motion_score', 0) * 100
        score += motion_score * 0.25
        
        # 3. 人物出现
        face_count = len(scene.get('faces', []))
        face_score = min(face_count * 30, 100)
        score += face_score * 0.2
        
        # 4. 特殊元素
        ocr_count = len(scene.get('ocr', {}).get('texts', []))
        special_score = min(ocr_count * 20, 100)
        score += special_score * 0.15
        
        # 5. 场景时长
        duration = scene['duration']
        if 5 <= duration <= 15:
            duration_score = 100
        elif duration < 5:
            duration_score = duration / 5 * 100
        else:
            duration_score = max(0, 100 - (duration - 15) * 5)
        score += duration_score * 0.1
        
        return score
