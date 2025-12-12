"""
主程序入口
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow
from utils.logger import get_logger
import config

logger = get_logger(__name__)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info(f"{config.APP_NAME} v{config.APP_VERSION} 启动")
    logger.info("=" * 60)
    
    # 设置高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName(config.APP_AUTHOR)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("主窗口已显示")
    
    # 运行应用
    exit_code = app.exec()
    
    logger.info(f"应用退出，代码: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
