"""
配音设置
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSlider, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.tts_engine import TTSEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class VoiceSettings(QWidget):
    """配音设置"""
    
    # 信号
    settings_changed = pyqtSignal(dict)
    preview_requested = pyqtSignal(str, dict)  # text, settings
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tts_engine = TTSEngine()
        
        self._init_ui()
        logger.info("配音设置初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 音色选择
        voice_group = QGroupBox("音色")
        voice_layout = QVBoxLayout(voice_group)
        
        self.voice_combo = QComboBox()
        self._load_voices()
        voice_layout.addWidget(self.voice_combo)
        
        layout.addWidget(voice_group)
        
        # 语速
        rate_group = QGroupBox("语速")
        rate_layout = QVBoxLayout(rate_group)
        
        rate_value_layout = QHBoxLayout()
        rate_value_layout.addWidget(QLabel("0.5x"))
        rate_value_layout.addStretch()
        self.rate_value_label = QLabel("1.0x")
        rate_value_layout.addWidget(self.rate_value_label)
        rate_value_layout.addStretch()
        rate_value_layout.addWidget(QLabel("2.0x"))
        rate_layout.addLayout(rate_value_layout)
        
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(100)
        self.rate_slider.valueChanged.connect(self.on_rate_changed)
        rate_layout.addWidget(self.rate_slider)
        
        layout.addWidget(rate_group)
        
        # 音调
        pitch_group = QGroupBox("音调")
        pitch_layout = QVBoxLayout(pitch_group)
        
        pitch_value_layout = QHBoxLayout()
        pitch_value_layout.addWidget(QLabel("低"))
        pitch_value_layout.addStretch()
        self.pitch_value_label = QLabel("正常")
        pitch_value_layout.addWidget(self.pitch_value_label)
        pitch_value_layout.addStretch()
        pitch_value_layout.addWidget(QLabel("高"))
        pitch_layout.addLayout(pitch_value_layout)
        
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setMinimum(50)
        self.pitch_slider.setMaximum(200)
        self.pitch_slider.setValue(100)
        self.pitch_slider.valueChanged.connect(self.on_pitch_changed)
        pitch_layout.addWidget(self.pitch_slider)
        
        layout.addWidget(pitch_group)
        
        # 音量
        volume_group = QGroupBox("音量")
        volume_layout = QVBoxLayout(volume_group)
        
        volume_value_layout = QHBoxLayout()
        volume_value_layout.addWidget(QLabel("0%"))
        volume_value_layout.addStretch()
        self.volume_value_label = QLabel("100%")
        volume_value_layout.addWidget(self.volume_value_label)
        volume_value_layout.addStretch()
        volume_value_layout.addWidget(QLabel("200%"))
        volume_layout.addLayout(volume_value_layout)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(200)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        
        layout.addWidget(volume_group)
        
        # 预览按钮
        preview_btn = QPushButton("试听")
        preview_btn.clicked.connect(self.preview)
        layout.addWidget(preview_btn)
        
        layout.addStretch()
    
    def _load_voices(self):
        """加载可用音色"""
        voices = self.tts_engine.available_voices
        
        for voice_id, voice_info in voices.items():
            display_name = f"{voice_info['name']} ({voice_info['description']})"
            self.voice_combo.addItem(display_name, voice_id)
    
    def on_rate_changed(self, value: int):
        """语速改变"""
        rate = value / 100.0
        self.rate_value_label.setText(f"{rate:.1f}x")
        self.emit_settings()
    
    def on_pitch_changed(self, value: int):
        """音调改变"""
        pitch = value / 100.0
        if pitch < 0.8:
            text = "很低"
        elif pitch < 0.9:
            text = "低"
        elif pitch < 1.1:
            text = "正常"
        elif pitch < 1.2:
            text = "高"
        else:
            text = "很高"
        self.pitch_value_label.setText(text)
        self.emit_settings()
    
    def on_volume_changed(self, value: int):
        """音量改变"""
        self.volume_value_label.setText(f"{value}%")
        self.emit_settings()
    
    def emit_settings(self):
        """发出设置改变信号"""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
    
    def get_settings(self) -> dict:
        """获取当前设置"""
        return {
            'voice': self.voice_combo.currentData(),
            'rate': self.rate_slider.value() / 100.0,
            'pitch': self.pitch_slider.value() / 100.0,
            'volume': self.volume_slider.value() / 100.0,
        }
    
    def get_selected_voice(self) -> str:
        """获取选中的音色"""
        return self.voice_combo.currentData()
    
    def preview(self):
        """预览试听"""
        text = "这是一段测试文案，用于试听配音效果。"
        settings = self.get_settings()
        self.preview_requested.emit(text, settings)
