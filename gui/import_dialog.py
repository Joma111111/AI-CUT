"""
导入对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QFileDialog,
    QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


class ImportDialog(QDialog):
    """导入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.video_path = ""
        self.project_name = ""
        self.description = ""
        
        self._init_ui()
        logger.info("导入对话框初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("导入视频")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 视频文件选择
        video_group = QGroupBox("视频文件")
        video_layout = QHBoxLayout(video_group)
        
        self.video_path_edit = QLineEdit()
        self.video_path_edit.setReadOnly(True)
        self.video_path_edit.setPlaceholderText("请选择视频文件...")
        video_layout.addWidget(self.video_path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_video)
        video_layout.addWidget(browse_btn)
        
        layout.addWidget(video_group)
        
        # 项目信息
        info_group = QGroupBox("项目信息")
        info_layout = QFormLayout(info_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入项目名称")
        info_layout.addRow("项目名称:", self.name_edit)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("输入项目描述（可选）")
        self.desc_edit.setMaximumHeight(80)
        info_layout.addRow("项目描述:", self.desc_edit)
        
        layout.addWidget(info_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept_import)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def browse_video(self):
        """浏览视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv);;所有文件 (*.*)"
        )
        
        if file_path:
            self.video_path = file_path
            self.video_path_edit.setText(file_path)
            
            # 自动填充项目名称
            if not self.name_edit.text():
                file_name = Path(file_path).stem
                self.name_edit.setText(file_name)
    
    def accept_import(self):
        """确认导入"""
        # 验证输入
        if not self.video_path:
            QMessageBox.warning(self, "警告", "请选择视频文件")
            return
        
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入项目名称")
            return
        
        self.project_name = self.name_edit.text().strip()
        self.description = self.desc_edit.toPlainText().strip()
        
        self.accept()
    
    def get_video_path(self) -> str:
        """获取视频路径"""
        return self.video_path
    
    def get_project_name(self) -> str:
        """获取项目名称"""
        return self.project_name
    
    def get_description(self) -> str:
        """获取项目描述"""
        return self.description
