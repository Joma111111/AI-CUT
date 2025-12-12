复制
# 🎯 核心功能模块

## 📋 模块概述

核心功能模块包含所有视频处理、AI生成、语音合成等核心业务逻辑。

---

## 📁 模块列表

### 1. video_analyzer.py
**视频分析器**
- 视频信息提取
- 元数据读取
- 视频质量分析
- 编码格式检测

### 2. scene_detector.py
**镜头检测器**
- 基于内容的镜头分割
- 阈值检测
- 自适应检测
- 镜头边界优化

### 3. keyframe_extractor.py
**关键帧提取器**
- 智能关键帧选择
- 多种提取算法
- 图像质量评估
- 去重和优化

### 4. subtitle_extractor.py
**字幕提取器**
- Whisper语音识别
- 多语言支持
- 时间轴对齐
- 字幕格式转换

### 5. script_generator.py
**文案生成器**
- Gemini/GPT集成
- 多风格支持
- 上下文理解
- 文案优化

### 6. tts_engine.py
**语音合成引擎**
- 多引擎支持
- 音色管理
- 参数调节
- 批量合成

### 7. video_processor.py
**视频处理器**
- FFmpeg封装
- 视频合成
- 音频混合
- 格式转换

### 8. project_manager.py
**项目管理器**
- 项目创建和保存
- 数据持久化
- 云端同步
- 版本管理

---

## 🔧 使用示例

### 完整工作流程

```python
from core.video_analyzer import VideoAnalyzer
from core.scene_detector import SceneDetector
from core.keyframe_extractor import KeyframeExtractor
from core.script_generator import ScriptGenerator
from core.tts_engine import TTSEngine
from core.video_processor import VideoProcessor

# 1. 分析视频
analyzer = VideoAnalyzer()
video_info = analyzer.analyze("input.mp4")

# 2. 检测镜头
detector = SceneDetector()
scenes = detector.detect("input.mp4")

# 3. 提取关键帧
extractor = KeyframeExtractor()
keyframes = extractor.extract("input.mp4", scenes)

# 4. 生成文案
generator = ScriptGenerator()
scripts = generator.generate(keyframes, style="drama")

# 5. 合成语音
tts = TTSEngine()
audios = tts.batch_synthesize(scripts)

# 6. 合成视频
processor = VideoProcessor()
output = processor.compose("input.mp4", audios, "output.mp4")
📊 性能优化
多线程处理
复制
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_scene, scene) for scene in scenes]
    results = [f.result() for f in futures]
GPU加速
复制
# 使用CUDA加速
detector = SceneDetector(use_gpu=True)
extractor = KeyframeExtractor(use_gpu=True)
缓存机制
复制
# 启用缓存
analyzer = VideoAnalyzer(cache_enabled=True)
🐛 错误处理
所有模块都实现了统一的错误处理：

复制
from core.exceptions import (
    VideoAnalysisError,
    SceneDetectionError,
    KeyframeExtractionError,
    ScriptGenerationError,
    TTSError,
    VideoProcessingError
)

try:
    scenes = detector.detect("video.mp4")
except SceneDetectionError as e:
    print(f"镜头检测失败: {e}")
📝 日志
所有模块都使用统一的日志系统：

复制
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("开始处理视频")
logger.error("处理失败", exc_info=True)
最后更新: 2025-01-10

复制

---

### `aicraft_client/core/__init__.py`

```python
"""
核心功能模块
"""

from .video_analyzer import VideoAnalyzer
from .scene_detector import SceneDetector
from .keyframe_extractor import KeyframeExtractor
from .subtitle_extractor import SubtitleExtractor
from .script_generator import ScriptGenerator
from .tts_engine import TTSEngine
from .video_processor import VideoProcessor
from .project_manager import ProjectManager

__all__ = [
    'VideoAnalyzer',
    'SceneDetector',
    'KeyframeExtractor',
    'SubtitleExtractor',
    'ScriptGenerator',
    'TTSEngine',
    'VideoProcessor',
    'ProjectManager',
]