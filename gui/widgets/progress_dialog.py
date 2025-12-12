"""
进度对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
)
from PyQt6.QtCore import Qt
from utils.logger import get_logger

logger = get_logger(__name__)


class ProgressDialog(QDialog):
    """进度对话框"""
    
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self._init_ui(message)
        logger.info(f"进度对话框初始化: {title}")
    
    def _init_ui(self, message: str):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 消息
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
    
    def set_progress(self, value: int):
        """设置进度"""
        self.progress_bar.setValue(value)
        
        # 完成时自动关闭
        if value >= 100:
            self.accept()
    
    def set_message(self, message: str):
        """设置消息"""
        self.message_label.setText(message)
