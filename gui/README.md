# 🎨 GUI界面模块

## 📋 模块概述

GUI界面模块基于PyQt6构建，提供完整的可视化操作界面。

---

## 📁 模块列表

### 1. main_window.py
**主窗口**
- 菜单栏和工具栏
- 视频预览区域
- 镜头列表
- 文案编辑器
- 状态栏

### 2. import_dialog.py
**导入对话框**
- 视频文件选择
- 项目信息输入
- 导入设置

### 3. scene_editor.py
**镜头编辑器**
- 镜头分割调整
- 关键帧查看
- 时间轴编辑

### 4. script_editor.py
**文案编辑器**
- 富文本编辑
- AI生成
- 文案优化

### 5. voice_settings.py
**配音设置**
- 音色选择
- 参数调节
- 预览试听

### 6. export_dialog.py
**导出对话框**
- 格式选择
- 质量设置
- 导出进度

### 7. widgets/
**自定义组件**
- video_player.py - 视频播放器
- timeline.py - 时间轴
- scene_card.py - 镜头卡片
- progress_dialog.py - 进度对话框

---

## 🎨 界面设计

### 布局结构
┌─────────────────────────────────────────┐
│  菜单栏                                  │
├─────────────────────────────────────────┤
│  工具栏                                  │
├──────────────────┬──────────────────────┤
│                  │                      │
│  视频预览区      │   镜头列表           │
│                  │                      │
│                  │                      │
├──────────────────┴──────────────────────┤
│  文案编辑器                              │
├─────────────────────────────────────────┤
│  时间轴                                  │
├─────────────────────────────────────────┤
│  状态栏                                  │
└─────────────────────────────────────────┘

复制

### 主题风格
- 支持明暗两种主题
- 自定义配色方案
- 响应式布局

---

## 🔧 使用示例

### 启动主窗口
```python
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
import sys

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
打开导入对话框
复制
from gui.import_dialog import ImportDialog

dialog = ImportDialog(parent=window)
if dialog.exec():
    video_path = dialog.get_video_path()
    project_name = dialog.get_project_name()
🎯 快捷键
Ctrl+N - 新建项目
Ctrl+O - 打开项目
Ctrl+S - 保存项目
Ctrl+E - 导出视频
Space - 播放/暂停
Ctrl+Z - 撤销
Ctrl+Y - 重做
F11 - 全屏
最后更新: 2025-01-10

复制

---

### `aicraft_client/gui/__init__.py`

```python
"""
GUI界面模块
"""

from .main_window import MainWindow
from .import_dialog import ImportDialog
from .scene_editor import SceneEditor
from .script_editor import ScriptEditor
from .voice_settings import VoiceSettings
from .export_dialog import ExportDialog

__all__ = [
    'MainWindow',
    'ImportDialog',
    'SceneEditor',
    'ScriptEditor',
    'VoiceSettings',
    'ExportDialog',