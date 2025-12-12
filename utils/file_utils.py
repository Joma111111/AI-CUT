"""
文件工具
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def ensure_dir(path: str) -> Path:
    """
    确保目录存在
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件大小（字节）
    """
    return os.path.getsize(file_path)


def get_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5, sha1, sha256)
        
    Returns:
        哈希值
    """
    if algorithm == 'md5':
        hasher = hashlib.md5()
    elif algorithm == 'sha1':
        hasher = hashlib.sha1()
    elif algorithm == 'sha256':
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """
    复制文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        overwrite: 是否覆盖已存在的文件
        
    Returns:
        是否成功
    """
    try:
        if os.path.exists(dst) and not overwrite:
            logger.warning(f"目标文件已存在: {dst}")
            return False
        
        # 确保目标目录存在
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            ensure_dir(dst_dir)
        
        shutil.copy2(src, dst)
        logger.info(f"文件复制成功: {src} -> {dst}")
        return True
        
    except Exception as e:
        logger.error(f"文件复制失败: {str(e)}")
        return False


def move_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """
    移动文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        overwrite: 是否覆盖已存在的文件
        
    Returns:
        是否成功
    """
    try:
        if os.path.exists(dst) and not overwrite:
            logger.warning(f"目标文件已存在: {dst}")
            return False
        
        # 确保目标目录存在
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            ensure_dir(dst_dir)
        
        shutil.move(src, dst)
        logger.info(f"文件移动成功: {src} -> {dst}")
        return True
        
    except Exception as e:
        logger.error(f"文件移动失败: {str(e)}")
        return False


def delete_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"文件删除成功: {file_path}")
            return True
        else:
            logger.warning(f"文件不存在: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}")
        return False


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        扩展名（不含点）
    """
    return Path(file_path).suffix.lstrip('.')


def change_file_extension(file_path: str, new_ext: str) -> str:
    """
    更改文件扩展名
    
    Args:
        file_path: 文件路径
        new_ext: 新扩展名
        
    Returns:
        新文件路径
    """
    path = Path(file_path)
    return str(path.with_suffix(f".{new_ext.lstrip('.')}"))


def list_files(directory: str, 
               pattern: str = "*",
               recursive: bool = False) -> list:
    """
    列出目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件模式
        recursive: 是否递归
        
    Returns:
        文件路径列表
    """
    dir_path = Path(directory)
    
    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))
    
    return [str(f) for f in files if f.is_file()]


def get_temp_file(prefix: str = "temp", suffix: str = "") -> str:
    """
    生成临时文件路径
    
    Args:
        prefix: 前缀
        suffix: 后缀
        
    Returns:
        临时文件路径
    """
    import tempfile
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(fd)
    return path


def clean_directory(directory: str, keep_dir: bool = True):
    """
    清空目录
    
    Args:
        directory: 目录路径
        keep_dir: 是否保留目录本身
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return
    
    if keep_dir:
        # 只删除内容
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    else:
        # 删除整个目录
        shutil.rmtree(dir_path)
    
    logger.info(f"目录清空完成: {directory}")
