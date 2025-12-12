"""
精彩片段筛选器
从场景中筛选出精彩片段
"""

import json
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class HighlightSelector:
    """精彩片段筛选器"""
    
    def __init__(self):
        """初始化筛选器"""
        logger.info("精彩片段筛选器初始化完成")
    
    def select_highlights(
        self,
        scenes: List[Dict],
        subtitles: List[Dict],
        target_duration: float = 600
    ) -> List[Dict]:
        """
        从场景中筛选精彩片段
        
        Args:
            scenes: 场景列表
            subtitles: 字幕列表
            target_duration: 目标总时长（秒）
        
        Returns:
            筛选后的场景列表
        """
        logger.info(f"开始筛选精彩片段，目标时长: {target_duration}秒")
        logger.info(f"输入场景数: {len(scenes)}, 字幕数: {len(subtitles)}")
        
        if not scenes:
            logger.warning("场景列表为空，无法筛选")
            return []
        
        if not subtitles:
            logger.warning("字幕列表为空，将基于场景时长筛选")
        
        # 1. 为每个场景添加字幕信息和计算得分
        enriched_scenes = []
        
        for scene in scenes:
            try:
                scene_with_dialogue = self._add_dialogue_to_scene(scene, subtitles)
                scene_with_dialogue['highlight_score'] = self._calculate_highlight_score(
                    scene_with_dialogue
                )
                enriched_scenes.append(scene_with_dialogue)
            except Exception as e:
                logger.error(f"处理场景 {scene.get('id', 'unknown')} 失败: {str(e)}")
                continue
        
        if not enriched_scenes:
            logger.error("没有成功处理的场景")
            return []
        
        # 2. 按分数排序（从高到低）
        enriched_scenes.sort(key=lambda x: x['highlight_score'], reverse=True)
        
        logger.info(
            f"场景得分范围: {enriched_scenes[-1]['highlight_score']:.1f} ~ "
            f"{enriched_scenes[0]['highlight_score']:.1f}"
        )
        
        # 3. 贪心选择：选择分数最高的场景，直到达到目标时长
        selected_scenes = []
        total_duration = 0
        
        for scene in enriched_scenes:
            if total_duration + scene['duration'] <= target_duration:
                selected_scenes.append(scene)
                total_duration += scene['duration']
                
                logger.debug(
                    f"  选择场景 {scene['id']}: "
                    f"{scene['start_time']:.1f}s-{scene['end_time']:.1f}s, "
                    f"得分: {scene['highlight_score']:.1f}"
                )
            
            # 如果已经达到目标时长，停止选择
            if total_duration >= target_duration * 0.95:
                break
        
        # 4. 按时间顺序重新排序
        selected_scenes.sort(key=lambda x: x['start_time'])
        
        # 5. 重新分配场景ID
        for i, scene in enumerate(selected_scenes, start=1):
            scene['selected_id'] = i
        
        logger.info(
            f"✅ 筛选完成: 从 {len(scenes)} 个场景中选出 {len(selected_scenes)} 个，"
            f"总时长: {total_duration:.1f}秒 ({total_duration/60:.1f}分钟)"
        )
        
        return selected_scenes
    
    def _add_dialogue_to_scene(self, scene: Dict, subtitles: List[Dict]) -> Dict:
        """为场景添加字幕信息"""
        start = scene['start_time']
        end = scene['end_time']
        
        # 找到该场景时间范围内的所有字幕
        scene_subtitles = [
            sub for sub in subtitles
            if (sub['start'] >= start and sub['start'] < end) or
               (sub['end'] > start and sub['end'] <= end) or
               (sub['start'] <= start and sub['end'] >= end)
        ]
        
        # 合并字幕文本
        dialogue = ' '.join([sub['text'] for sub in scene_subtitles])
        
        # 创建新的场景字典（不修改原始数据）
        scene_with_dialogue = scene.copy()
        scene_with_dialogue['dialogue'] = dialogue
        scene_with_dialogue['subtitle_count'] = len(scene_subtitles)
        
        return scene_with_dialogue
    
    def _calculate_highlight_score(self, scene: Dict) -> float:
        """
        计算场景的精彩度得分（0-100分）
        
        评分标准：
        1. 对白密度 (40%) - 有对白的场景更精彩
        2. 对白数量 (30%) - 字幕条数多的场景更精彩
        3. 场景时长 (30%) - 时长适中的场景（5-15秒）
        """
        score = 0
        duration = scene['duration']
        
        # ========== 1. 对白密度得分 (0-40分) ==========
        dialogue = scene.get('dialogue', '')
        dialogue_len = len(dialogue)
        
        if dialogue_len > 0:
            # 对白密度 = 字数 / 时长（每秒字数）
            dialogue_density = dialogue_len / duration if duration > 0 else 0
            
            # 假设每秒8个字是满分（中文语速）
            dialogue_score = min(dialogue_density / 8 * 100, 100)
        else:
            dialogue_score = 0
        
        score += dialogue_score * 0.4
        
        # ========== 2. 对白数量得分 (0-30分) ==========
        subtitle_count = scene.get('subtitle_count', 0)
        
        if subtitle_count > 0:
            # 字幕条数越多，说明对话越密集
            subtitle_score = min(subtitle_count * 20, 100)
        else:
            subtitle_score = 0
        
        score += subtitle_score * 0.3
        
        # ========== 3. 场景时长得分 (0-30分) ==========
        # 理想时长：5-15秒
        if 5 <= duration <= 15:
            duration_score = 100
        elif duration < 5:
            # 太短，按比例扣分
            duration_score = duration / 5 * 100
        else:
            # 太长，按比例扣分（但不会太严格）
            duration_score = max(0, 100 - (duration - 15) * 3)
        
        score += duration_score * 0.3
        
        return round(score, 2)
    
    def save_selected_scenes(self, selected_scenes: List[Dict], output_path: str):
        """保存筛选结果"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(selected_scenes, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 筛选结果已保存: {output_path}")
        except Exception as e:
            logger.error(f"保存筛选结果失败: {str(e)}")
            raise
