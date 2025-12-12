"""
关键帧模型
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Keyframe:
    """关键帧数据模型"""
    
    scene_id: str
    keyframe_index: int
    time: float
    frame_number: int
    image_path: Optional[str] = None
    image_hash: Optional[str] = None
    quality_score: float = 0.0
    
    # 关联数据
    project_id: Optional[str] = None
    scene_index: Optional[int] = None
    
    # 元数据
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'scene_id': self.scene_id,
            'keyframe_index': self.keyframe_index,
            'time': self.time,
            'frame_number': self.frame_number,
            'image_path': self.image_path,
            'image_hash': self.image_hash,
            'quality_score': self.quality_score,
            'project_id': self.project_id,
            'scene_index': self.scene_index,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Keyframe':
        """从字典创建"""
        return cls(
            scene_id=data['scene_id'],
            keyframe_index=data['keyframe_index'],
            time=data['time'],
            frame_number=data['frame_number'],
            image_path=data.get('image_path'),
            image_hash=data.get('image_hash'),
            quality_score=data.get('quality_score', 0.0),
            project_id=data.get('project_id'),
            scene_index=data.get('scene_index'),
            metadata=data.get('metadata', {}),
        )
