"""
时间轴组件
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class Timeline(QWidget):
    """时间轴"""
    
    # 信号
    position_changed = pyqtSignal(float)  # 位置改变（秒）
    scene_clicked = pyqtSignal(str)       # 镜头点击
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scenes = []
        self.duration = 0
        self.current_position = 0
        self.zoom_level = 1.0
        
        self.setMinimumHeight(80)
        self.setMouseTracking(True)
        
        logger.info("时间轴初始化完成")
    
    def set_scenes(self, scenes: List[Dict]):
        """设置镜头列表"""
        self.scenes = scenes
        
        if scenes:
            self.duration = scenes[-1]['end_time']
        
        self.update()
    
    def set_position(self, time_sec: float):
        """设置当前位置"""
        self.current_position = time_sec
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), QColor(40, 40, 40))
        
        if not self.scenes or self.duration == 0:
            return
        
        # 计算缩放
        width = self.width()
        height = self.height()
        pixels_per_second = (width - 20) / self.duration * self.zoom_level
        
        # 绘制镜头
        y_offset = 10
        scene_height = height - 40
        
        for scene in self.scenes:
            start_x = 10 + scene['start_time'] * pixels_per_second
            end_x = 10 + scene['end_time'] * pixels_per_second
            scene_width = end_x - start_x
            
            # 镜头矩形
            rect = QRectF(start_x, y_offset, scene_width, scene_height)
            
            # 填充颜色（交替）
            if scene['index'] % 2 == 0:
                color = QColor(70, 130, 180)
            else:
                color = QColor(100, 150, 200)
            
            painter.fillRect(rect, color)
            
            # 边框
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawRect(rect)
            
            # 镜头ID（如果空间足够）
            if scene_width > 50:
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, scene['id'])
        
        # 绘制时间刻度
        self.draw_time_scale(painter, pixels_per_second)
        
        # 绘制播放位置指示器
        position_x = 10 + self.current_position * pixels_per_second
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawLine(int(position_x), 0, int(position_x), height)
    
    def draw_time_scale(self, painter: QPainter, pixels_per_second: float):
        """绘制时间刻度"""
        height = self.height()
        scale_y = height - 20
        
        # 计算刻度间隔
        if pixels_per_second > 100:
            interval = 1  # 1秒
        elif pixels_per_second > 50:
            interval = 2  # 2秒
        elif pixels_per_second > 20:
            interval = 5  # 5秒
        else:
            interval = 10  # 10秒
        
        painter.setPen(QColor(200, 200, 200))
        
        time = 0
        while time <= self.duration:
            x = 10 + time * pixels_per_second
            
            # 刻度线
            painter.drawLine(int(x), scale_y, int(x), scale_y + 5)
            
            # 时间文本
            time_text = self.format_time(time)
            painter.drawText(int(x - 20), scale_y + 15, time_text)
            
            time += interval
    
    def format_time(self, seconds: float) -> str:
        """格式化时间"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if not self.scenes or self.duration == 0:
            return
        
        x = event.position().x()
        width = self.width()
        pixels_per_second = (width - 20) / self.duration * self.zoom_level
        
        # 计算点击的时间位置
        time_sec = (x - 10) / pixels_per_second
        time_sec = max(0, min(time_sec, self.duration))
        
        # 查找点击的镜头
        for scene in self.scenes:
            if scene['start_time'] <= time_sec <= scene['end_time']:
                self.scene_clicked.emit(scene['id'])
                break
        
        # 发出位置改变信号
        self.position_changed.emit(time_sec)
    
    def wheelEvent(self, event):
        """鼠标滚轮事件（缩放）"""
        delta = event.angleDelta().y()
        
        if delta > 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level /= 1.1
        
        # 限制缩放范围
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0))
        
        self.update()
