"""
格式化工具
"""

from datetime import datetime, timedelta
from typing import Union


def format_time(seconds: float, format: str = "HH:MM:SS") -> str:
    """
    格式化时间
    
    Args:
        seconds: 秒数
        format: 格式 (HH:MM:SS, MM:SS, verbose)
        
    Returns:
        格式化的时间字符串
    """
    if format == "HH:MM:SS":
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    elif format == "MM:SS":
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    elif format == "verbose":
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if secs > 0 or not parts:
            parts.append(f"{secs}秒")
        
        return "".join(parts)
    
    else:
        raise ValueError(f"不支持的格式: {format}")


def format_size(bytes: int, precision: int = 2) -> str:
    """
    格式化文件大小
    
    Args:
        bytes: 字节数
        precision: 小数位数
        
    Returns:
        格式化的大小字符串
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    size = float(bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.{precision}f} {units[unit_index]}"


def format_number(number: Union[int, float], 
                 precision: int = 2,
                 thousand_sep: str = ",") -> str:
    """
    格式化数字
    
    Args:
        number: 数字
        precision: 小数位数
        thousand_sep: 千位分隔符
        
    Returns:
        格式化的数字字符串
    """
    if isinstance(number, int):
        # 整数
        return f"{number:,}".replace(",", thousand_sep)
    else:
        # 浮点数
        formatted = f"{number:,.{precision}f}"
        return formatted.replace(",", thousand_sep)


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        format: 格式字符串
        
    Returns:
        格式化的日期时间字符串
    """
    return dt.strftime(format)


def format_duration(start: datetime, end: datetime) -> str:
    """
    格式化时间段
    
    Args:
        start: 开始时间
        end: 结束时间
        
    Returns:
        格式化的时间段字符串
    """
    delta = end - start
    return format_time(delta.total_seconds(), format="verbose")


def format_percentage(value: float, total: float, precision: int = 1) -> str:
    """
    格式化百分比
    
    Args:
        value: 值
        total: 总数
        precision: 小数位数
        
    Returns:
        格式化的百分比字符串
    """
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.{precision}f}%"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的字符串
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_time(time_str: str) -> float:
    """
    解析时间字符串为秒数
    
    Args:
        time_str: 时间字符串 (HH:MM:SS 或 MM:SS)
        
    Returns:
        秒数
    """
    parts = time_str.split(':')
    
    if len(parts) == 3:
        # HH:MM:SS
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        # MM:SS
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:
        raise ValueError(f"无效的时间格式: {time_str}")
