"""
设备工具
"""

import platform
import psutil
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def get_cpu_info() -> Dict:
    """
    获取CPU信息
    
    Returns:
        CPU信息字典
    """
    return {
        'processor': platform.processor(),
        'architecture': platform.machine(),
        'cores_physical': psutil.cpu_count(logical=False),
        'cores_logical': psutil.cpu_count(logical=True),
        'frequency_current': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        'frequency_max': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
        'usage_percent': psutil.cpu_percent(interval=1),
    }


def get_gpu_info() -> Optional[Dict]:
    """
    获取GPU信息
    
    Returns:
        GPU信息字典，如果没有GPU则返回None
    """
    try:
        import torch
        
        if not torch.cuda.is_available():
            return None
        
        gpu_count = torch.cuda.device_count()
        gpus = []
        
        for i in range(gpu_count):
            gpu = {
                'index': i,
                'name': torch.cuda.get_device_name(i),
                'memory_total': torch.cuda.get_device_properties(i).total_memory,
                'memory_allocated': torch.cuda.memory_allocated(i),
                'memory_cached': torch.cuda.memory_reserved(i),
            }
            gpus.append(gpu)
        
        return {
            'available': True,
            'count': gpu_count,
            'devices': gpus,
            'cuda_version': torch.version.cuda,
        }
        
    except ImportError:
        logger.warning("PyTorch未安装，无法获取GPU信息")
        return None
    except Exception as e:
        logger.error(f"获取GPU信息失败: {str(e)}")
        return None


def get_memory_info() -> Dict:
    """
    获取内存信息
    
    Returns:
        内存信息字典
    """
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        'total': mem.total,
        'available': mem.available,
        'used': mem.used,
        'percent': mem.percent,
        'swap_total': swap.total,
        'swap_used': swap.used,
        'swap_percent': swap.percent,
    }


def get_disk_info(path: str = "/") -> Dict:
    """
    获取磁盘信息
    
    Args:
        path: 路径
        
    Returns:
        磁盘信息字典
    """
    disk = psutil.disk_usage(path)
    
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent,
    }


def get_system_info() -> Dict:
    """
    获取系统信息
    
    Returns:
        系统信息字典
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }


def check_cuda_available() -> bool:
    """
    检查CUDA是否可用
    
    Returns:
        是否可用
    """
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def get_optimal_thread_count() -> int:
    """
    获取最优线程数
    
    Returns:
        线程数
    """
    cpu_count = psutil.cpu_count(logical=True)
    
    # 保留一些CPU给系统
    optimal = max(1, cpu_count - 2)
    
    return optimal


def check_memory_available(required_mb: int) -> bool:
    """
    检查是否有足够的可用内存
    
    Args:
        required_mb: 需要的内存（MB）
        
    Returns:
        是否有足够内存
    """
    mem = psutil.virtual_memory()
    available_mb = mem.available / (1024 * 1024)
    
    return available_mb >= required_mb


def get_process_info() -> Dict:
    """
    获取当前进程信息
    
    Returns:
        进程信息字典
    """
    process = psutil.Process()
    
    return {
        'pid': process.pid,
        'name': process.name(),
        'cpu_percent': process.cpu_percent(interval=1),
        'memory_info': process.memory_info()._asdict(),
        'memory_percent': process.memory_percent(),
        'num_threads': process.num_threads(),
        'create_time': process.create_time(),
    }
