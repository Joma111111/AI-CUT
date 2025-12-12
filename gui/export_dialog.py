"""
导出对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QComboBox,
    QGroupBox, QFormLayout, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


class ExportDialog(QDialog):
    """导出对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.output_path = ""
        
        self._init_ui()
        logger.info("导出对话框初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("导出视频")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 输出路径
        path_group = QGroupBox("输出路径")
        path_layout = QHBoxLayout(path_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("选择输出路径...")
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_output)
        path_layout.addWidget(browse_btn)
        
        layout.addWidget(path_group)
        
        # 导出设置
        settings_group = QGroupBox("导出设置")
        settings_layout = QFormLayout(settings_group)
        
        # 格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MOV", "MKV"])
        settings_layout.addRow("格式:", self.format_combo)
        
        # 质量
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["高质量", "中等质量", "低质量"])
        self.quality_combo.setCurrentIndex(1)
        settings_layout.addRow("质量:", self.quality_combo)
        
        # 分辨率
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "原始分辨率",
            "1920x1080 (1080p)",
            "1280x720 (720p)",
            "854x480 (480p)"
        ])
        settings_layout.addRow("分辨率:", self.resolution_combo)
        
        # 帧率
        self.fps_spin = QSpinBox()
        self.fps_spin.setMinimum(15)
        self.fps_spin.setMaximum(60)
        self.fps_spin.setValue(30)
        self.fps_spin.setSuffix(" fps")
        settings_layout.addRow("帧率:", self.fps_spin)
        
        layout.addWidget(settings_group)
        
        # 音频设置
        audio_group = QGroupBox("音频设置")
        audio_layout = QFormLayout(audio_group)
        
        self.keep_original_audio = QCheckBox("保留原视频音频")
        audio_layout.addRow("", self.keep_original_audio)
        
        self.audio_volume_spin = QSpinBox()
        self.audio_volume_spin.setMinimum(0)
        self.audio_volume_spin.setMaximum(100)
        self.audio_volume_spin.setValue(30)
        self.audio_volume_spin.setSuffix(" %")
        audio_layout.addRow("原音音量:", self.audio_volume_spin)
        
        layout.addWidget(audio_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        export_btn = QPushButton("导出")
        export_btn.setDefault(True)
        export_btn.clicked.connect(self.accept_export)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
    
    def browse_output(self):
        """浏览输出路径"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择输出路径",
            "",
            "MP4文件 (*.mp4);;AVI文件 (*.avi);;MOV文件 (*.mov);;所有文件 (*.*)"
        )
        
        if file_path:
            self.output_path = file_path
            self.path_edit.setText(file_path)
    
    def accept_export(self):
        """确认导出"""
        if not self.output_path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "警告", "请选择输出路径")
            return
        
        self.accept()
    
    def get_settings(self) -> dict:
        """获取导出设置"""
        quality_map = {
            "高质量": "high",
            "中等质量": "medium",
            "低质量": "low"
        }
        
        return {
            'output_path': self.output_path,
            'format': self.format_combo.currentText().lower(),
            'quality': quality_map[self.quality_combo.currentText()],
            'resolution': self.resolution_combo.currentText(),
            'fps': self.fps_spin.value(),
            'keep_original_audio': self.keep_original_audio.isChecked(),
            'audio_volume': self.audio_volume_spin.value() / 100.0,
        }
