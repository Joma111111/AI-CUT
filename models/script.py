"""
文案模型
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass
class Script:
    """文案数据模型"""
    
    scene_id: str
    script: str
    word_count: int = 0
    
    # 关联数据
    project_id: Optional[str] = None
    
    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 元数据
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.word_count == 0:
            self.word_count = len(self.script)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'scene_id': self.scene_id,
            'script': self.script,
            'word_count': self.word_count,
            'project_id': self.project_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Script':
        """从字典创建"""
        return cls(
            scene_id=data['scene_id'],
            script=data['script'],
            word_count=data.get('word_count', len(data['script'])),
            project_id=data.get('project_id'),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            metadata=data.get('metadata', {}),
        )
    
    def update(self, new_script: str):
        """更新文案"""
        self.script = new_script
        self.word_count = len(new_script)
        self.updated_at = datetime.now().isoformat()
