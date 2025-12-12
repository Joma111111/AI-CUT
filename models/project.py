"""
项目模型
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Project:
    """项目数据模型"""
    
    id: str
    name: str
    description: str = ""
    video_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1
    status: str = "created"
    
    # 关联数据
    scenes: List['Scene'] = field(default_factory=list)
    keyframes: List['Keyframe'] = field(default_factory=list)
    scripts: List['Script'] = field(default_factory=list)
    audios: List['Audio'] = field(default_factory=list)
    
    # 元数据
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'video_path': self.video_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'version': self.version,
            'status': self.status,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        """从字典创建"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            video_path=data.get('video_path', ''),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            version=data.get('version', 1),
            status=data.get('status', 'created'),
            metadata=data.get('metadata', {}),
        )
    
    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now().isoformat()
        self.version += 1
