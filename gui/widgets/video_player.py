"""
视频播放器组件
"""

import cv2
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QStyle
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon
from utils.logger import get_logger

logger = get_logger(__name__)


class VideoPlayer(QWidget):
    """视频播放器"""
    
    # 信号
    position_changed = pyqtSignal(float)  # 播放位置改变（秒）
    state_changed = pyqtSignal(str)       # 播放状态改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.duration = 0
        
        # 定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        self._init_ui()
        logger.info("视频播放器初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 视频显示区域
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setMinimumSize(640, 360)
        layout.addWidget(self.video_label)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        # 播放/暂停按钮
        self.play_btn = QPushButton()
        self.play_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.play_btn.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        )
        self.stop_btn.clicked.connect(self.stop)
        control_layout.addWidget(self.stop_btn)
        
        # 时间显示
        self.time_label = QLabel("00:00 / 00:00")
        control_layout.addWidget(self.time_label)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.sliderMoved.connect(self.seek_by_slider)
        control_layout.addWidget(self.progress_slider)
        
        # 音量按钮
        self.volume_btn = QPushButton()
        self.volume_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        )
        control_layout.addWidget(self.volume_btn)
        
        # 全屏按钮
        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
        )
        control_layout.addWidget(self.fullscreen_btn)
        
        layout.addLayout(control_layout)
    
    def load_video(self, video_path: str):
        """
        加载视频
        
        Args:
            video_path: 视频文件路径
        """
        logger.info(f"加载视频: {video_path}")
        
        # 释放之前的视频
        if self.cap:
            self.cap.release()
        
        # 打开新视频
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            logger.error(f"无法打开视频: {video_path}")
            return
        
        # 获取视频信息
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        # 设置进度条范围
        self.progress_slider.setMaximum(self.total_frames)
        
        # 显示第一帧
        self.current_frame = 0
        self.display_frame(0)
        
        # 更新时间显示
        self.update_time_label()
        
        logger.info(f"视频加载完成: {self.duration:.2f}秒, {self.fps:.2f}fps")
    
    def toggle_play(self):
        """切换播放/暂停"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """播放"""
        if not self.cap:
            return
        
        self.is_playing = True
        interval = int(1000 / self.fps) if self.fps > 0 else 33
        self.timer.start(interval)
        
        # 更新按钮图标
        self.play_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        )
        
        self.state_changed.emit("playing")
        logger.debug("开始播放")
    
    def pause(self):
        """暂停"""
        self.is_playing = False
        self.timer.stop()
        
        # 更新按钮图标
        self.play_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        
        self.state_changed.emit("paused")
        logger.debug("暂停播放")
    
    def stop(self):
        """停止"""
        self.pause()
        self.seek(0)
        self.state_changed.emit("stopped")
        logger.debug("停止播放")
    
    def seek(self, time_sec: float):
        """
        跳转到指定时间
        
        Args:
            time_sec: 时间（秒）
        """
        if not self.cap:
            return
        
        frame_number = int(time_sec * self.fps)
        frame_number = max(0, min(frame_number, self.total_frames - 1))
        
        self.current_frame = frame_number
        self.display_frame(frame_number)
        
        # 更新进度条
        self.progress_slider.blockSignals(True)
        self.progress_slider.setValue(frame_number)
        self.progress_slider.blockSignals(False)
        
        # 更新时间显示
        self.update_time_label()
        
        # 发出信号
        self.position_changed.emit(time_sec)
    
    def seek_by_slider(self, frame_number: int):
        """通过进度条跳转"""
        time_sec = frame_number / self.fps if self.fps > 0 else 0
        self.seek(time_sec)
    
    def update_frame(self):
        """更新帧（定时器调用）"""
        if not self.cap or not self.is_playing:
            return
        
        self.current_frame += 1
        
        # 检查是否到达结尾
        if self.current_frame >= self.total_frames:
            self.stop()
            return
        
        # 显示当前帧
        self.display_frame(self.current_frame)
        
        # 更新进度条
        self.progress_slider.blockSignals(True)
        self.progress_slider.setValue(self.current_frame)
        self.progress_slider.blockSignals(False)
        
        # 更新时间显示
        self.update_time_label()
        
        # 发出信号
        time_sec = self.current_frame / self.fps if self.fps > 0 else 0
        self.position_changed.emit(time_sec)
    
    def display_frame(self, frame_number: int):
        """
        显示指定帧
        
        Args:
            frame_number: 帧号
        """
        if not self.cap:
            return
        
        # 设置帧位置
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # 读取帧
        ret, frame = self.cap.read()
        
        if not ret:
            return
        
        # 转换颜色空间
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 转换为QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # 缩放以适应显示区域
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 显示
        self.video_label.setPixmap(scaled_pixmap)
    
    def update_time_label(self):
        """更新时间显示"""
        current_sec = self.current_frame / self.fps if self.fps > 0 else 0
        total_sec = self.duration
        
        current_time = self.format_time(current_sec)
        total_time = self.format_time(total_sec)
        
        self.time_label.setText(f"{current_time} / {total_time}")
    
    def format_time(self, seconds: float) -> str:
        """
        格式化时间
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串 (MM:SS)
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def get_current_time(self) -> float:
        """获取当前播放时间（秒）"""
        return self.current_frame / self.fps if self.fps > 0 else 0
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.cap:
            self.cap.release()
        event.accept()
