"""
镜头编辑器
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from utils.logger import get_logger

logger = get_logger(__name__)


class SceneEditor(QWidget):
    """镜头编辑器"""
    
    # 信号
    scene_split = pyqtSignal(str, float)  # scene_id, split_time
    scene_merged = pyqtSignal(str, str)   # scene_id1, scene_id2
    scene_deleted = pyqtSignal(str)       # scene_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_scene = None
        
        self._init_ui()
        logger.info("镜头编辑器初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 镜头信息
        info_group = QGroupBox("镜头信息")
        info_layout = QVBoxLayout(info_group)
        
        self.scene_id_label = QLabel("ID: -")
        info_layout.addWidget(self.scene_id_label)
        
        self.duration_label = QLabel("时长: -")
        info_layout.addWidget(self.duration_label)
        
        self.time_range_label = QLabel("时间: -")
        info_layout.addWidget(self.time_range_label)
        
        layout.addWidget(info_group)
        
        # 分割控制
        split_group = QGroupBox("分割镜头")
        split_layout = QVBoxLayout(split_group)
        
        split_time_layout = QHBoxLayout()
        split_time_layout.addWidget(QLabel("分割位置:"))
        
        self.split_time_spin = QSpinBox()
        self.split_time_spin.setSuffix(" 秒")
        self.split_time_spin.setMinimum(0)
        self.split_time_spin.setMaximum(3600)
        split_time_layout.addWidget(self.split_time_spin)
        split_time_layout.addStretch()
        
        split_layout.addLayout(split_time_layout)
        
        split_btn = QPushButton("分割")
        split_btn.clicked.connect(self.split_scene)
        split_layout.addWidget(split_btn)
        
        layout.addWidget(split_group)
        
        # 合并控制
        merge_group = QGroupBox("合并镜头")
        merge_layout = QVBoxLayout(merge_group)
        
        merge_btn = QPushButton("与下一个镜头合并")
        merge_btn.clicked.connect(self.merge_scene)
        merge_layout.addWidget(merge_btn)
        
        layout.addWidget(merge_group)
        
        # 删除控制
        delete_btn = QPushButton("删除镜头")
        delete_btn.clicked.connect(self.delete_scene)
        delete_btn.setStyleSheet("QPushButton { color: red; }")
        layout.addWidget(delete_btn)
        
        layout.addStretch()
    
    def set_scene(self, scene: dict):
        """设置当前镜头"""
        self.current_scene = scene
        
        # 更新显示
        self.scene_id_label.setText(f"ID: {scene['id']}")
        self.duration_label.setText(f"时长: {scene['duration']:.2f} 秒")
        self.time_range_label.setText(
            f"时间: {scene['start_time']:.2f}s - {scene['end_time']:.2f}s"
        )
        
        # 设置分割时间范围
        self.split_time_spin.setMinimum(int(scene['start_time']))
        self.split_time_spin.setMaximum(int(scene['end_time']))
        self.split_time_spin.setValue(
            int((scene['start_time'] + scene['end_time']) / 2)
        )
    
    def split_scene(self):
        """分割镜头"""
        if not self.current_scene:
            return
        
        split_time = self.split_time_spin.value()
        self.scene_split.emit(self.current_scene['id'], float(split_time))
    
    def merge_scene(self):
        """合并镜头"""
        if not self.current_scene:
            return
        
        # 这里需要知道下一个镜头的ID，实际应该从父组件获取
        # 暂时发出信号，由父组件处理
        self.scene_merged.emit(self.current_scene['id'], "")
    
    def delete_scene(self):
        """删除镜头"""
        if not self.current_scene:
            return
        
        self.scene_deleted.emit(self.current_scene['id'])
