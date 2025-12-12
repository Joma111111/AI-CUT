"""
文案编辑器
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QComboBox, QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class ScriptEditor(QWidget):
    """文案编辑器"""
    
    # 信号
    script_changed = pyqtSignal(str, str)  # scene_id, new_text
    generate_requested = pyqtSignal(dict)  # generation_params
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scripts = []
        self.current_scene_id = None
        
        self._init_ui()
        logger.info("文案编辑器初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        toolbar.addWidget(QLabel("当前镜头:"))
        self.scene_label = QLabel("-")
        toolbar.addWidget(self.scene_label)
        
        toolbar.addStretch()
        
        # AI生成按钮
        generate_btn = QPushButton("AI生成")
        generate_btn.clicked.connect(self.show_generate_dialog)
        toolbar.addWidget(generate_btn)
        
        # 优化按钮
        optimize_btn = QPushButton("优化文案")
        optimize_btn.clicked.connect(self.optimize_script)
        toolbar.addWidget(optimize_btn)
        
        layout.addLayout(toolbar)
        
        # 文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("在此编辑解说文案...")
        
        # 设置字体
        font = QFont("Microsoft YaHei", 12)
        self.text_edit.setFont(font)
        
        # 连接信号
        self.text_edit.textChanged.connect(self.on_text_changed)
        
        layout.addWidget(self.text_edit)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        self.word_count_label = QLabel("字数: 0")
        stats_layout.addWidget(self.word_count_label)
        
        stats_layout.addStretch()
        
        self.char_count_label = QLabel("字符数: 0")
        stats_layout.addWidget(self.char_count_label)
        
        layout.addLayout(stats_layout)
    
    def set_scripts(self, scripts: List[Dict]):
        """设置所有文案"""
        self.scripts = scripts
        
        if scripts:
            # 显示第一个
            self.set_current_script(scripts[0])
    
    def set_current_script(self, script: Dict):
        """设置当前文案"""
        self.current_scene_id = script['scene_id']
        self.scene_label.setText(script['scene_id'])
        
        # 阻止信号，避免触发textChanged
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(script['script'])
        self.text_edit.blockSignals(False)
        
        # 更新统计
        self.update_stats()
    
    def get_scripts(self) -> List[Dict]:
        """获取所有文案"""
        return self.scripts
    
    def get_current_text(self) -> str:
        """获取当前文本"""
        return self.text_edit.toPlainText()
    
    def on_text_changed(self):
        """文本改变事件"""
        if self.current_scene_id:
            new_text = self.get_current_text()
            
            # 更新scripts列表
            for script in self.scripts:
                if script['scene_id'] == self.current_scene_id:
                    script['script'] = new_text
                    script['word_count'] = len(new_text)
                    break
            
            # 发出信号
            self.script_changed.emit(self.current_scene_id, new_text)
            
            # 更新统计
            self.update_stats()
    
    def update_stats(self):
        """更新统计信息"""
        text = self.get_current_text()
        
        # 字数（中文字符）
        word_count = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        self.word_count_label.setText(f"字数: {word_count}")
        
        # 字符数（包括标点和空格）
        char_count = len(text)
        self.char_count_label.setText(f"字符数: {char_count}")
    
    def show_generate_dialog(self):
        """显示生成对话框"""
        # TODO: 实现生成参数对话框
        params = {
            'style': 'drama',
            'length': 500,
        }
        self.generate_requested.emit(params)
    
    def optimize_script(self):
        """优化文案"""
        # TODO: 调用AI优化
        pass
