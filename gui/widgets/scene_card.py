"""
镜头卡片组件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage
from typing import List, Dict
import cv2
from utils.logger import get_logger

logger = get_logger(__name__)


class SceneCard(QFrame):
    """镜头卡片"""
    
    clicked = pyqtSignal(str)  # scene_id
    
    def __init__(self, scene: Dict, keyframe_path: str = None, parent=None):
        super().__init__(parent)
        
        self.scene = scene
        self.scene_id = scene['id']
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._init_ui(keyframe_path)
    
    def _init_ui(self, keyframe_path: str):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 缩略图
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(160, 90)
        self.thumbnail_label.setStyleSheet("background-color: black;")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if keyframe_path:
            self.load_thumbnail(keyframe_path)
        
        layout.addWidget(self.thumbnail_label)
        
        # 镜头ID
        id_label = QLabel(self.scene['id'])
        id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(id_label)
        
        # 时间信息
        time_text = f"{self.scene['start_time']:.1f}s - {self.scene['end_time']:.1f}s"
        time_label = QLabel(time_text)
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(time_label)
        
        # 时长
        duration_text = f"时长: {self.scene['duration']:.1f}s"
        duration_label = QLabel(duration_text)
        duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(duration_label)
    
    def load_thumbnail(self, image_path: str):
        """加载缩略图"""
        try:
            # 使用OpenCV读取
            img = cv2.imread(image_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                height, width, channel = img.shape
                bytes_per_line = 3 * width
                q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(
                    160, 90,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.thumbnail_label.setPixmap(scaled_pixmap)
        except Exception as e:
            logger.error(f"加载缩略图失败: {str(e)}")
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.clicked.emit(self.scene_id)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        if selected:
            self.setStyleSheet("QFrame { border: 2px solid #4A90E2; }")
        else:
            self.setStyleSheet("")


class SceneListWidget(QScrollArea):
    """镜头列表组件"""
    
    scene_selected = pyqtSignal(str)  # scene_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scenes = []
        self.keyframes = []
        self.scene_cards = []
        self.selected_scene_id = None
        
        self._init_ui()
        logger.info("镜头列表初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 容器
        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setWidget(container)
    
    def set_scenes(self, scenes: List[Dict], keyframes: List[Dict] = None):
        """设置镜头列表"""
        self.scenes = scenes
        self.keyframes = keyframes or []
        
        # 清空现有卡片
        self.clear_cards()
        
        # 创建新卡片
        for scene in scenes:
            # 查找该镜头的第一个关键帧
            keyframe_path = None
            for kf in self.keyframes:
                if kf['scene_id'] == scene['id']:
                    keyframe_path = kf.get('image_path')
                    break
            
            # 创建卡片
            card = SceneCard(scene, keyframe_path)
            card.clicked.connect(self.on_card_clicked)
            
            self.scene_cards.append(card)
            self.container_layout.addWidget(card)
    
    def clear_cards(self):
        """清空所有卡片"""
        for card in self.scene_cards:
            self.container_layout.removeWidget(card)
            card.deleteLater()
        
        self.scene_cards.clear()
    
    def on_card_clicked(self, scene_id: str):
        """卡片点击事件"""
        # 更新选中状态
        for card in self.scene_cards:
            card.set_selected(card.scene_id == scene_id)
        
        self.selected_scene_id = scene_id
        self.scene_selected.emit(scene_id)
    
    def get_scenes(self) -> List[Dict]:
        """获取镜头列表"""
        return self.scenes
