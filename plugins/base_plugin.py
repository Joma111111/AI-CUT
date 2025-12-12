"""
插件基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self):
        """初始化插件"""
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
        self.enabled = True
        
        logger.info(f"插件初始化: {self.name}")
    
    @abstractmethod
    def on_load(self):
        """插件加载时调用"""
        pass
    
    @abstractmethod
    def on_unload(self):
        """插件卸载时调用"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息
        
        Returns:
            插件信息字典
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': self.enabled,
        }
    
    def enable(self):
        """启用插件"""
        self.enabled = True
        logger.info(f"插件已启用: {self.name}")
    
    def disable(self):
        """禁用插件"""
        self.enabled = False
        logger.info(f"插件已禁用: {self.name}")


class VideoProcessPlugin(BasePlugin):
    """视频处理插件基类"""
    
    @abstractmethod
    def process_video(self, video_path: str, **kwargs) -> str:
        """
        处理视频
        
        Args:
            video_path: 视频路径
            **kwargs: 其他参数
            
        Returns:
            处理后的视频路径
        """
        pass


class ScriptGeneratorPlugin(BasePlugin):
    """文案生成插件基类"""
    
    @abstractmethod
    def generate_script(self, keyframes: list, **kwargs) -> list:
        """
        生成文案
        
        Args:
            keyframes: 关键帧列表
            **kwargs: 其他参数
            
        Returns:
            文案列表
        """
        pass


class TTSPlugin(BasePlugin):
    """TTS插件基类"""
    
    @abstractmethod
    def synthesize(self, text: str, **kwargs) -> str:
        """
        合成语音
        
        Args:
            text: 文本
            **kwargs: 其他参数
            
        Returns:
            音频文件路径
        """
        pass


class ExportPlugin(BasePlugin):
    """导出插件基类"""
    
    @abstractmethod
    def export(self, project_data: dict, output_path: str, **kwargs):
        """
        导出项目
        
        Args:
            project_data: 项目数据
            output_path: 输出路径
            **kwargs: 其他参数
        """
        pass
