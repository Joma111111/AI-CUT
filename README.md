# 🎬 悟剪 AIcraft - 客户端应用

## 📋 项目概述

悟剪 AIcraft 客户端是一款基于AI的智能视频解说工具，支持自动视频分析、AI文案生成、智能配音等功能。

**核心功能**：
- 🎥 智能视频分析（镜头分割、关键帧提取）
- 🤖 AI文案生成（Gemini/GPT支持）
- 🎙️ 智能语音合成（多引擎支持）
- 📝 字幕提取（Whisper）
- 🎨 可视化编辑界面（PyQt6）
- ☁️ 云端同步（项目备份）
- 🔐 许可证管理

---

## 🏗️ 项目结构

aicraft_client/
├── README.md                      # 项目说明
├── requirements.txt               # Python依赖
├── main.py                        # 应用入口
├── config.py                      # 配置管理
├── core/                          # 核心功能模块
│   ├── README.md                  # 核心模块说明
│   ├── init.py
│   ├── video_analyzer.py          # 视频分析
│   ├── scene_detector.py          # 镜头检测
│   ├── keyframe_extractor.py      # 关键帧提取
│   ├── subtitle_extractor.py      # 字幕提取
│   ├── script_generator.py        # 文案生成
│   ├── tts_engine.py              # 语音合成
│   ├── video_processor.py         # 视频处理
│   └── project_manager.py         # 项目管理
├── gui/                           # GUI界面
│   ├── README.md                  # GUI模块说明
│   ├── init.py
│   ├── main_window.py             # 主窗口
│   ├── import_dialog.py           # 导入对话框
│   ├── scene_editor.py            # 镜头编辑器
│   ├── script_editor.py           # 文案编辑器
│   ├── voice_settings.py          # 配音设置
│   ├── export_dialog.py           # 导出对话框
│   └── widgets/                   # 自定义组件
│       ├── init.py
│       ├── video_player.py        # 视频播放器
│       ├── timeline.py            # 时间轴
│       ├── scene_card.py          # 镜头卡片
│       └── progress_dialog.py     # 进度对话框
├── resources/                     # 资源文件
│   ├── README.md                  # 资源说明
│   ├── icons/                     # 图标
│   ├── styles/                    # 样式表
│   │   └── dark_theme.qss
│   └── templates/                 # 模板
│       └── script_template.txt
├── utils/                         # 工具函数
│   ├── init.py
│   ├── logger.py                  # 日志工具
│   ├── file_utils.py              # 文件工具
│   ├── format_utils.py            # 格式化工具
│   └── device_utils.py            # 设备工具
├── models/                        # 数据模型
│   ├── init.py
│   ├── project.py                 # 项目模型
│   ├── scene.py                   # 镜头模型
│   └── script.py                  # 文案模型
├── database/                      # 本地数据库
│   ├── init.py
│   ├── db_manager.py              # 数据库管理
│   └── aicraft_local.db           # SQLite数据库
├── build/                         # 打包配置
│   ├── README.md                  # 打包说明
│   ├── aicraft.spec               # PyInstaller配置
│   ├── build.py                   # 构建脚本
│   └── icon.ico                   # 应用图标
├── tests/                         # 测试
│   ├── test_video_analyzer.py
│   ├── test_scene_detector.py
│   └── test_script_generator.py
└── docs/                          # 文档
├── USER_GUIDE.md              # 用户指南
├── DEVELOPER_GUIDE.md         # 开发指南
└── API_REFERENCE.md           # API参考

复制

---

## 🚀 快速开始

### 1. 环境要求

- **Python**: 3.8+
- **操作系统**: Windows 10/11, macOS 10.15+, Linux
- **硬件**:
  - CPU: Intel i5 或更高
  - 内存: 8GB+
  - 显卡: 支持CUDA的NVIDIA显卡（可选，用于加速）
  - 硬盘: 10GB+ 可用空间

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/aicraft/aicraft-client.git
cd aicraft_client

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
3. 配置
复制配置文件并修改：

复制
cp config.example.py config.py
编辑 config.py，配置API密钥：

复制
# Gemini API配置
GEMINI_API_KEY = "your-gemini-api-key"

# OpenAI API配置
OPENAI_API_KEY = "your-openai-api-key"

# 服务端API配置
SERVER_API_URL = "http://localhost:8000"
4. 运行
复制
python main.py
📚 核心功能模块
1. 视频分析模块
功能：

视频信息提取（时长、分辨率、帧率等）
镜头自动分割（基于场景变化检测）
关键帧智能提取（多种算法支持）
视频质量分析
使用示例：

复制
from core.video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer()
video_info = analyzer.analyze("video.mp4")
scenes = analyzer.detect_scenes("video.mp4")
keyframes = analyzer.extract_keyframes("video.mp4", scenes)
2. AI文案生成模块
功能：

基于关键帧的文案生成
多种解说风格（剧情、搞笑、悬疑等）
支持Gemini和GPT模型
文案优化和润色
使用示例：

复制
from core.script_generator import ScriptGenerator

generator = ScriptGenerator(api_key="your-key")
script = generator.generate(
    keyframes=keyframes,
    style="drama",
    length=500
)
3. 语音合成模块
功能：

多引擎支持（IndexTTS、Edge TTS等）
多种音色选择
语速、音调调节
批量合成
使用示例：

复制
from core.tts_engine import TTSEngine

tts = TTSEngine(engine="indextts")
audio_path = tts.synthesize(
    text="这是一段解说文案",
    voice="zh-CN-XiaoxiaoNeural",
    rate=1.0
)
4. 字幕提取模块
功能：

基于Whisper的语音识别
多语言支持
时间轴自动对齐
字幕格式转换
使用示例：

复制
from core.subtitle_extractor import SubtitleExtractor

extractor = SubtitleExtractor()
subtitles = extractor.extract("video.mp4", language="zh")
🎨 GUI界面
主窗口
菜单栏: 文件、编辑、视图、工具、帮助
工具栏: 常用功能快捷按钮
视频预览: 实时视频播放和预览
镜头列表: 显示所有镜头和关键帧
文案编辑器: 编辑和优化解说文案
时间轴: 可视化时间轴编辑
工作流程
导入视频 → 自动分析
调整镜头 → 手动微调分割点
生成文案 → AI自动生成或手动编写
配音合成 → 选择音色和参数
预览效果 → 实时预览
导出视频 → 生成最终作品
🔧 配置说明
config.py
复制
# ============================================
# 应用配置
# ============================================

# 应用信息
APP_NAME = "悟剪 AIcraft"
APP_VERSION = "1.0.0"

# 服务端API
SERVER_API_URL = "http://localhost:8000"
SERVER_API_PREFIX = "/api/v1"

# Gemini API
GEMINI_API_KEY = "your-gemini-api-key"
GEMINI_MODEL = "gemini-pro-vision"

# OpenAI API
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_MODEL = "gpt-4-vision-preview"

# TTS配置
TTS_ENGINE = "indextts"  # indextts, edge, azure
TTS_DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

# 视频分析配置
SCENE_DETECTION_THRESHOLD = 30.0  # 镜头检测阈值
KEYFRAME_MODE = "medium"  # low, medium, high
MAX_KEYFRAMES_PER_SCENE = 3

# 本地数据库
LOCAL_DB_PATH = "database/aicraft_local.db"

# 临时文件目录
TEMP_DIR = "temp"
CACHE_DIR = "cache"

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "logs/aicraft.log"

# 许可证配置
LICENSE_CHECK_INTERVAL = 3600  # 1小时检查一次
📦 打包发布
Windows
复制
# 安装打包工具
pip install pyinstaller

# 打包
python build/build.py --platform windows

# 输出目录
dist/AICraft-1.0.0-Windows.exe
macOS
复制
# 打包
python build/build.py --platform macos

# 输出目录
dist/AICraft-1.0.0-macOS.dmg
Linux
复制
# 打包
python build/build.py --platform linux

# 输出目录
dist/AICraft-1.0.0-Linux.AppImage
🐛 调试
开启调试模式
在 config.py 中设置：

复制
DEBUG = True
LOG_LEVEL = "DEBUG"
查看日志
复制
tail -f logs/aicraft.log
常见问题
Q: 视频分析失败？
A: 检查FFmpeg是否正确安装，运行 ffmpeg -version

Q: AI生成失败？
A: 检查API密钥是否正确，网络是否正常

Q: TTS合成失败？
A: 检查TTS引擎配置和网络连接

🔒 许可证
本软件采用商业许可证，需要激活码才能使用完整功能。

试用版
免费使用3次
功能完整
正式版
无限次使用
优先技术支持
免费更新
激活方法
打开软件
点击"激活许可证"
输入激活码
完成激活
📞 技术支持
官网: https://aicraft.com
文档: https://docs.aicraft.com
邮箱: support@aicraft.com
QQ群: 123456789
🤝 贡献
欢迎提交Issue和Pull Request！

开发规范
遵循PEP 8代码规范
添加必要的注释和文档
编写单元测试
提交前运行测试
📄 许可证
商业许可证 - 详见 LICENSE 文件

🎉 致谢
感谢以下开源项目：

PyQt6
OpenCV
FFmpeg
Whisper
Gemini API
OpenAI API
最后更新: 2025-01-10

版本: 1.0.0

作者: AIcraft Team

复制

---

### `aicraft_client/requirements.txt`

```txt
# ============================================
# 悟剪 AIcraft 客户端 - Python依赖列表
# ============================================

# -------------------- 核心框架 --------------------
PyQt6==6.6.1
PyQt6-Qt6==6.6.1
PyQt6-sip==13.6.0

# -------------------- 视频处理 --------------------
opencv-python==4.9.0.80
opencv-contrib-python==4.9.0.80
ffmpeg-python==0.2.0
moviepy==1.0.3
scenedetect==0.6.3

# -------------------- AI模型 --------------------
google-generativeai==0.3.2
openai==1.6.1
anthropic==0.8.1

# -------------------- 语音处理 --------------------
openai-whisper==20231117
edge-tts==6.1.10
pyttsx3==2.90
soundfile==0.12.1
pydub==0.25.1

# -------------------- 图像处理 --------------------
Pillow==10.1.0
numpy==1.24.3
scikit-image==0.22.0

# -------------------- 网络请求 --------------------
requests==2.31.0
httpx==0.25.2
aiohttp==3.9.1

# -------------------- 数据处理 --------------------
pandas==2.1.4
pydantic==2.5.3

# -------------------- 数据库 --------------------
SQLAlchemy==2.0.23

# -------------------- 工具库 --------------------
python-dotenv==1.0.0
PyYAML==6.0.1
toml==0.10.2

# -------------------- 日志 --------------------
loguru==0.7.2

# -------------------- 进度条 --------------------
tqdm==4.66.1

# -------------------- 加密 --------------------
cryptography==41.0.7

# -------------------- 系统工具 --------------------
psutil==5.9.6
pyinstaller==6.3.0

# -------------------- 测试 --------------------
pytest==7.4.3
pytest-qt==4.2.0
pytest-cov==4.1.0

# -------------------- 代码质量 --------------------
black==23.12.1
flake8==7.0.0
mypy==1.7.1

# -------------------- 其他 --------------------
colorama==0.4.6
click==8.1.7