"""
镜头模型
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Scene:
    """镜头数据模型"""
    
    id: str
    index: int
    start_time: float
    end_time: float
    duration: float
    start_frame: int
    end_frame: int
    
    # 关联数据
    project_id: Optional[str] = None
    
    # 元数据
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'index': self.index,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
            'project_id': self.project_id,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Scene':
        """从字典创建"""
        return cls(
            id=data['id'],
            index=data['index'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            duration=data['duration'],
            start_frame=data['start_frame'],
            end_frame=data['end_frame'],
            project_id=data.get('project_id'),
            metadata=data.get('metadata', {}),
        )
