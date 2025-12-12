"""
核心模块异常定义
"""


class AICraftCoreError(Exception):
    """核心模块基础异常"""
    pass


class VideoAnalysisError(AICraftCoreError):
    """视频分析异常"""
    pass


class SceneDetectionError(AICraftCoreError):
    """镜头检测异常"""
    pass


class KeyframeExtractionError(AICraftCoreError):
    """关键帧提取异常"""
    pass


class SubtitleExtractionError(AICraftCoreError):
    """字幕提取异常"""
    pass


class ScriptGenerationError(AICraftCoreError):
    """文案生成异常"""
    pass


class TTSError(AICraftCoreError):
    """语音合成异常"""
    pass


class VideoProcessingError(AICraftCoreError):
    """视频处理异常"""
    pass


class ProjectManagerError(AICraftCoreError):
    """项目管理异常"""
    pass
