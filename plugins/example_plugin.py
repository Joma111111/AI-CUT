"""
示例插件
"""

from .base_plugin import VideoProcessPlugin


class WatermarkPlugin(VideoProcessPlugin):
    """水印插件示例"""
    
    def __init__(self):
        super().__init__()
        self.name = "WatermarkPlugin"
        self.version = "1.0.0"
        self.description = "为视频添加水印"
        self.author = "AICraft Team"
    
    def on_load(self):
        """加载时调用"""
        print(f"{self.name} 已加载")
    
    def on_unload(self):
        """卸载时调用"""
        print(f"{self.name} 已卸载")
    
    def process_video(self, video_path: str, **kwargs) -> str:
        """
        处理视频（添加水印）
        
        Args:
            video_path: 视频路径
            **kwargs: 其他参数
                - watermark_text: 水印文本
                - position: 位置 (top-left, top-right, bottom-left, bottom-right)
                - opacity: 透明度 (0-1)
            
        Returns:
            处理后的视频路径
        """
        watermark_text = kwargs.get('watermark_text', 'AICraft')
        position = kwargs.get('position', 'bottom-right')
        opacity = kwargs.get('opacity', 0.5)
        
        # TODO: 实现水印添加逻辑
        print(f"添加水印: {watermark_text} at {position}")
        
        return video_path
