"""
主窗口
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QMenu, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QDockWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from pathlib import Path

from .import_dialog import ImportDialog
from .scene_editor import SceneEditor
from .script_editor import ScriptEditor
from .voice_settings import VoiceSettings
from .export_dialog import ExportDialog
from .widgets.video_player import VideoPlayer
from .widgets.timeline import Timeline
from .widgets.scene_card import SceneListWidget
from .widgets.progress_dialog import ProgressDialog

from core.project_manager import ProjectManager
from core.video_analyzer import VideoAnalyzer
from core.scene_detector import SceneDetector
from core.keyframe_extractor import KeyframeExtractor
from core.script_generator import ScriptGenerator
from core.tts_engine import TTSEngine
from core.video_processor import VideoProcessor

from utils.logger import get_logger
import config

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """主窗口"""
    
    # 信号
    project_loaded = pyqtSignal(dict)
    project_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.project_manager = ProjectManager()
        self.current_project = None
        self.current_project_id = None
        
        self._init_ui()
        self._init_menu()
        self._init_toolbar()
        self._init_statusbar()
        self._connect_signals()
        
        logger.info("主窗口初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setGeometry(100, 100, 1280, 800)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 分割器（上下）
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 上半部分（视频预览 + 镜头列表）
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 视频播放器
        self.video_player = VideoPlayer()
        top_splitter.addWidget(self.video_player)
        
        # 镜头列表
        self.scene_list = SceneListWidget()
        top_splitter.addWidget(self.scene_list)
        
        # 设置比例
        top_splitter.setStretchFactor(0, 2)
        top_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(top_splitter)
        
        # 下半部分（文案编辑器）
        self.script_editor = ScriptEditor()
        main_splitter.addWidget(self.script_editor)
        
        # 设置比例
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(main_splitter)
        
        # 时间轴
        self.timeline = Timeline()
        main_layout.addWidget(self.timeline)
        
        # 镜头编辑器（停靠窗口）
        self.scene_editor_dock = QDockWidget("镜头编辑器", self)
        self.scene_editor = SceneEditor()
        self.scene_editor_dock.setWidget(self.scene_editor)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.scene_editor_dock)
        self.scene_editor_dock.hide()
        
        # 配音设置（停靠窗口）
        self.voice_settings_dock = QDockWidget("配音设置", self)
        self.voice_settings = VoiceSettings()
        self.voice_settings_dock.setWidget(self.voice_settings)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.voice_settings_dock)
        self.voice_settings_dock.hide()
        
        # 加载样式表
        self._load_stylesheet()
    
    def _init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开项目(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存项目(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("导入视频(&I)", self)
        import_action.triggered.connect(self.import_video)
        file_menu.addAction(import_action)
        
        export_action = QAction("导出视频(&E)", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_video)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        scene_editor_action = QAction("镜头编辑器", self)
        scene_editor_action.setCheckable(True)
        scene_editor_action.triggered.connect(
            lambda checked: self.scene_editor_dock.setVisible(checked)
        )
        view_menu.addAction(scene_editor_action)
        
        voice_settings_action = QAction("配音设置", self)
        voice_settings_action.setCheckable(True)
        voice_settings_action.triggered.connect(
            lambda checked: self.voice_settings_dock.setVisible(checked)
        )
        view_menu.addAction(voice_settings_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("全屏(&F)", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        
        analyze_action = QAction("分析视频", self)
        analyze_action.triggered.connect(self.analyze_video)
        tools_menu.addAction(analyze_action)
        
        # ✅ 修改：添加"生成剧本"菜单项
        generate_script_data_action = QAction("生成剧本", self)
        generate_script_data_action.triggered.connect(self.generate_script_data)
        tools_menu.addAction(generate_script_data_action)
        
        # ✅ 修改：原"生成文案"改为"生成解说"
        generate_commentary_action = QAction("生成解说", self)
        generate_commentary_action.triggered.connect(self.generate_commentary)
        tools_menu.addAction(generate_commentary_action)
        
        synthesize_voice_action = QAction("合成配音", self)
        synthesize_voice_action.triggered.connect(self.synthesize_voice)
        tools_menu.addAction(synthesize_voice_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        doc_action = QAction("用户手册", self)
        doc_action.triggered.connect(self.show_documentation)
        help_menu.addAction(doc_action)
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _init_toolbar(self):
        """初始化工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 新建
        new_btn = QAction("新建", self)
        new_btn.triggered.connect(self.new_project)
        toolbar.addAction(new_btn)
        
        # 打开
        open_btn = QAction("打开", self)
        open_btn.triggered.connect(self.open_project)
        toolbar.addAction(open_btn)
        
        # 保存
        save_btn = QAction("保存", self)
        save_btn.triggered.connect(self.save_project)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        # 导入
        import_btn = QAction("导入", self)
        import_btn.triggered.connect(self.import_video)
        toolbar.addAction(import_btn)
        
        # 导出
        export_btn = QAction("导出", self)
        export_btn.triggered.connect(self.export_video)
        toolbar.addAction(export_btn)
        
        toolbar.addSeparator()
        
        # 分析
        analyze_btn = QAction("分析", self)
        analyze_btn.triggered.connect(self.analyze_video)
        toolbar.addAction(analyze_btn)
        
        # ✅ 修改：原"生成"改为"生成剧本"
        generate_script_btn = QAction("生成剧本", self)
        generate_script_btn.triggered.connect(self.generate_script_data)
        toolbar.addAction(generate_script_btn)
        
        # ✅ 新增："生成解说"按钮
        generate_commentary_btn = QAction("生成解说", self)
        generate_commentary_btn.triggered.connect(self.generate_commentary)
        toolbar.addAction(generate_commentary_btn)
        
        # 合成
        synthesize_btn = QAction("合成", self)
        synthesize_btn.triggered.connect(self.synthesize_voice)
        toolbar.addAction(synthesize_btn)
    
    def _init_statusbar(self):
        """初始化状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("就绪")
    
    def _connect_signals(self):
        """连接信号"""
        self.scene_list.scene_selected.connect(self.on_scene_selected)
        self.timeline.position_changed.connect(self.video_player.seek)
        self.video_player.position_changed.connect(self.timeline.set_position)
    
    def _load_stylesheet(self):
        """加载样式表"""
        theme = config.UI_THEME
        style_file = Path("resources/styles") / f"{theme}_theme.qss"
        
        if style_file.exists():
            with open(style_file, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
    
    def new_project(self):
        """新建项目"""
        dialog = ImportDialog(self)
        if dialog.exec():
            video_path = dialog.get_video_path()
            project_name = dialog.get_project_name()
            description = dialog.get_description()
            
            try:
                # 创建项目
                project = self.project_manager.create_project(
                    name=project_name,
                    video_path=video_path,
                    description=description
                )
                
                self.current_project = project
                self.current_project_id = project['id']
                
                # 加载视频
                self.video_player.load_video(project['video_path'])
                
                # 更新标题
                self.setWindowTitle(f"{project_name} - {config.APP_NAME}")
                
                self.statusbar.showMessage(f"项目创建成功: {project_name}")
                
                # 自动分析视频
                QTimer.singleShot(500, self.analyze_video)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建项目失败: {str(e)}")
    
    def open_project(self):
        """打开项目"""
        # TODO: 实现项目选择对话框
        pass
    
    def save_project(self):
        """保存项目"""
        if not self.current_project_id:
            QMessageBox.warning(self, "警告", "没有打开的项目")
            return
        
        try:
            # 收集当前数据
            project_data = self.current_project.copy()
            project_data['scenes'] = self.scene_list.get_scenes()
            project_data['scripts'] = self.script_editor.get_scripts()
            
            # 保存
            self.project_manager.save_project(self.current_project_id, project_data)
            
            self.statusbar.showMessage("项目已保存")
            self.project_saved.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存项目失败: {str(e)}")
    
    def import_video(self):
        """导入视频"""
        self.new_project()
    
    def export_video(self):
        """导出视频"""
        if not self.current_project_id:
            QMessageBox.warning(self, "警告", "没有打开的项目")
            return
        
        dialog = ExportDialog(self)
        if dialog.exec():
            # TODO: 实现导出逻辑
            pass
    
    def analyze_video(self):
        """分析视频（第1步：检测镜头+提取关键帧）"""
        if not self.current_project:
            QMessageBox.warning(self, "警告", "没有打开的项目")
            return
        
        progress = ProgressDialog("分析视频", "正在分析视频，请稍候...", self)
        progress.show()
        
        try:
            video_path = self.current_project['video_path']
            
            # 检测镜头
            detector = SceneDetector()
            scenes = detector.detect(
                video_path,
                progress_callback=lambda p: progress.set_progress(int(p * 0.5))
            )
            
            # 提取关键帧
            project_dir = self.project_manager.get_project_path(
                self.current_project_id, "keyframes"
            )
            extractor = KeyframeExtractor()
            keyframes = extractor.extract(
                video_path,
                scenes,
                output_dir=str(project_dir),
                progress_callback=lambda p: progress.set_progress(50 + int(p * 0.5))
            )
            
            # 更新UI
            self.scene_list.set_scenes(scenes, keyframes)
            self.timeline.set_scenes(scenes)
            
            # 保存到项目
            self.current_project['scenes'] = scenes
            self.current_project['keyframes'] = keyframes
            
            progress.close()
            self.statusbar.showMessage(f"分析完成: {len(scenes)} 个镜头")
            
            # ✅ 自动进入下一步：生成剧本
            reply = QMessageBox.question(
                self,
                "继续操作",
                "视频分析完成！是否继续生成剧本（识别画面+提取对白）？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QTimer.singleShot(500, self.generate_script_data)
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "错误", f"视频分析失败: {str(e)}")
    
    def generate_script_data(self):
        """生成剧本（第2步：Gemini识别画面+提取对白）"""
        if not self.current_project or not self.current_project.get('scenes'):
            QMessageBox.warning(self, "警告", "请先分析视频")
            return
        
        progress = ProgressDialog("生成剧本", "正在识别画面和提取对白，请稍候...", self)
        progress.show()
        
        try:
            from core.script_analyzer import ScriptAnalyzer
            from core.highlight_selector import HighlightSelector
            import json
            
            scenes = self.current_project['scenes']
            keyframes = self.current_project['keyframes']
            video_path = self.current_project['video_path']
            
            # ========== 步骤1：提取字幕 ==========
            logger.info("步骤1: 提取字幕...")
            progress.set_message("步骤1/4: 提取字幕...")
            
            from core.subtitle_extractor import SubtitleExtractor
            
            subtitle_extractor = SubtitleExtractor(
                model_size=config.WHISPER_MODEL_SIZE,
                use_online=config.USE_ONLINE_WHISPER
            )
            
            all_subtitles = subtitle_extractor.extract(
                video_path,
                progress_callback=lambda p: progress.set_progress(int(p * 0.3))
            )
            
            logger.info(f"✅ 字幕提取完成: {len(all_subtitles)} 条")
            
            # ========== 步骤2：筛选精彩片段 ==========
            logger.info("步骤2: 筛选精彩片段...")
            progress.set_message("步骤2/4: 筛选精彩片段...")
            progress.set_progress(30)
            
            selector = HighlightSelector()
            target_duration = getattr(config, 'TARGET_DURATION', 600)
            
            selected_scenes = selector.select_highlights(
                scenes=scenes,
                subtitles=all_subtitles,
                target_duration=target_duration
            )
            
            total_duration = sum(s['duration'] for s in selected_scenes)
            logger.info(
                f"✅ 筛选完成: 从 {len(scenes)} 个场景中选出 {len(selected_scenes)} 个，"
                f"总时长: {total_duration:.1f}秒"
            )
            
            # 保存筛选结果
            selected_scenes_file = self.project_manager.get_project_path(
                self.current_project_id, "selected_scenes.json"
            )
            selector.save_selected_scenes(selected_scenes, str(selected_scenes_file))
            
            # ========== 步骤3：提取筛选后场景的关键帧 ==========
            logger.info("步骤3: 提取筛选后场景的关键帧...")
            progress.set_message("步骤3/4: 提取关键帧...")
            progress.set_progress(40)
            
            from core.keyframe_extractor import KeyframeExtractor
            
            keyframes_dir = self.project_manager.get_project_path(
                self.current_project_id, "keyframes"
            )
            
            extractor = KeyframeExtractor()
            selected_keyframes = extractor.extract(
                video_path,
                selected_scenes,
                output_dir=str(keyframes_dir),
                prefix='selected_'
            )
            
            logger.info(f"✅ 提取了 {len(selected_keyframes)} 个关键帧")
            
            # ========== 步骤4：画面识别和生成剧本 ==========
            logger.info("步骤4: 画面识别和生成剧本...")
            progress.set_message("步骤4/4: 画面识别...")
            progress.set_progress(50)
            
            # 输出路径
            output_path = self.project_manager.get_project_path(
                self.current_project_id, "script_data.json"
            )
            
            # 生成剧本
            analyzer = ScriptAnalyzer()
            script_data = analyzer.analyze_scenes(
                selected_scenes,
                selected_keyframes,
                video_path,
                str(output_path),
                progress_callback=lambda p: progress.set_progress(50 + int(p * 0.5))
            )
            
            # 保存到项目
            self.current_project['script_data'] = script_data
            self.current_project['selected_scenes'] = selected_scenes
            self.current_project['selected_keyframes'] = selected_keyframes
            self.current_project['all_subtitles'] = all_subtitles
            
            progress.close()
            self.statusbar.showMessage(f"剧本生成完成: {len(script_data)} 个镜头")
            
            # 询问是否继续生成解说
            reply = QMessageBox.question(
                self,
                "继续操作",
                f"剧本生成完成！\n"
                f"- 筛选场景: {len(selected_scenes)} 个\n"
                f"- 总时长: {total_duration/60:.1f} 分钟\n\n"
                f"是否继续生成解说文案？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QTimer.singleShot(500, self.generate_commentary)
            
        except Exception as e:
            progress.close()
            logger.error(f"剧本生成失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"剧本生成失败: {str(e)}")
    
    def generate_commentary(self):
        """生成解说文案（第3步：根据剧本生成解说）"""
        if not self.current_project or not self.current_project.get('script_data'):
            QMessageBox.warning(self, "警告", "请先生成剧本")
            return
        
        progress = ProgressDialog("生成解说", "AI正在生成解说文案，请稍候...", self)
        progress.show()
        
        try:
            script_data = self.current_project['script_data']
            
            # ✅ 传递完整剧本数据
            generator = ScriptGenerator()
            scripts = generator.generate(
                script_data,  # ← 传剧本数据，不是关键帧
                style="drama",
                length=500,
                progress_callback=lambda p: progress.set_progress(int(p))
            )
            
            # 更新编辑器
            self.script_editor.set_scripts(scripts)
            
            # 保存到项目
            self.current_project['scripts'] = scripts
            
            progress.close()
            self.statusbar.showMessage(f"解说文案生成完成: {len(scripts)} 段")
            
            # ✅ 询问是否继续合成配音
            reply = QMessageBox.question(
                self,
                "继续操作",
                "解说文案生成完成！是否继续合成配音？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QTimer.singleShot(500, self.synthesize_voice)
            
        except Exception as e:
            progress.close()
            logger.error(f"解说生成失败: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"解说生成失败: {str(e)}")
    
    def generate_script(self):
        """生成文案（入口方法，保持兼容性）"""
        # 检查是否已有剧本数据
        if self.current_project and self.current_project.get('script_data'):
            # 如果已有剧本，直接生成解说
            self.generate_commentary()
        else:
            # 如果没有剧本，先生成剧本
            self.generate_script_data()
    
    def synthesize_voice(self):
        """合成配音"""
        scripts = self.script_editor.get_scripts()
        
        if not scripts:
            QMessageBox.warning(self, "警告", "没有文案可合成")
            return
        
        progress = ProgressDialog("合成配音", "正在合成配音，请稍候...", self)
        progress.show()
        
        try:
            # 获取配音设置
            voice = self.voice_settings.get_selected_voice()
            
            # 合成
            project_dir = self.project_manager.get_project_path(
                self.current_project_id, "audios"
            )
            tts = TTSEngine()
            audios = tts.batch_synthesize(
                scripts,
                output_dir=str(project_dir),
                voice=voice,
                progress_callback=lambda p: progress.set_progress(int(p))
            )
            
            # 保存到项目
            self.current_project['audios'] = audios
            
            progress.close()
            self.statusbar.showMessage(f"配音合成完成: {len(audios)} 段")
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "错误", f"配音合成失败: {str(e)}")
    
    def on_scene_selected(self, scene_id: str):
        """镜头选中事件"""
        scenes = self.current_project.get('scenes', [])
        scene = next((s for s in scenes if s['id'] == scene_id), None)
        
        if scene:
            # 跳转到镜头开始位置
            self.video_player.seek(scene['start_time'])
            
            # 更新编辑器
            scripts = self.current_project.get('scripts', [])
            script = next((s for s in scripts if s['scene_id'] == scene_id), None)
            if script:
                self.script_editor.set_current_script(script)
    
    def toggle_fullscreen(self):
        """切换全屏"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_documentation(self):
        """显示文档"""
        QMessageBox.information(
            self,
            "用户手册",
            "用户手册功能开发中..."
        )
    
    def show_about(self):
        """显示关于"""
        QMessageBox.about(
            self,
            f"关于 {config.APP_NAME}",
            f"""
            <h3>{config.APP_NAME}</h3>
            <p>版本: {config.APP_VERSION}</p>
            <p>基于AI的智能视频解说工具</p>
            <p>Copyright © 2025 {config.APP_AUTHOR}</p>
            """
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 检查是否有未保存的更改
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出吗？未保存的更改将丢失。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
