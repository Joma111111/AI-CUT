"""
日志工具
"""

import sys
from pathlib import Path
from loguru import logger
import config


def setup_logger():
    """设置日志系统"""
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        format=config.LOG_FORMAT,
        level=config.LOG_LEVEL,
        colorize=True
    )
    
    # 文件输出
    log_dir = Path(config.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        config.LOG_FILE,
        format=config.LOG_FORMAT,
        level=config.LOG_LEVEL,
        rotation=f"{config.LOG_MAX_SIZE} MB",
        retention=config.LOG_BACKUP_COUNT,
        compression="zip",
        encoding="utf-8"
    )
    
    logger.info("日志系统初始化完成")


def get_logger(name: str = None):
    """
    获取日志记录器
    
    Args:
        name: 模块名称
        
    Returns:
        日志记录器
    """
    if name:
        return logger.bind(name=name)
    return logger


# 初始化日志系统
setup_logger()
