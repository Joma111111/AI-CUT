"""
音频模型
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass
class Audio:
    """音频数据模型"""
    
    scene_id: str
    audio_path: str
    duration: float = 0.0
    voice: str = ""
    
    # 关联数据
    project_id: Optional[str] = None
    
    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 元数据
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'scene_id': self.scene_id,
            'audio_path': self.audio_path,
            'duration': self.duration,
            'voice': self.voice,
            'project_id': self.project_id,
            'created_at': self.created_at,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Audio':
        """从字典创建"""
        return cls(
            scene_id=data['scene_id'],
            audio_path=data['audio_path'],
            duration=data.get('duration', 0.0),
            voice=data.get('voice', ''),
            project_id=data.get('project_id'),
            created_at=data.get('created_at', datetime.now().isoformat()),
            metadata=data.get('metadata', {}),
        )
