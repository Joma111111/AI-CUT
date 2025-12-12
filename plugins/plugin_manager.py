"""
插件管理器
"""

import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Type
from .base_plugin import BasePlugin
from utils.logger import get_logger

logger = get_logger(__name__)


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        """
        初始化插件管理器
        
        Args:
            plugin_dir: 插件目录
        """
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, BasePlugin] = {}
        
        logger.info(f"插件管理器初始化: {plugin_dir}")
    
    def load_plugins(self):
        """加载所有插件"""
        if not self.plugin_dir.exists():
            logger.warning(f"插件目录不存在: {self.plugin_dir}")
            return
        
        # 遍历插件目录
        for file_path in self.plugin_dir.glob("*.py"):
            if file_path.stem.startswith("_"):
                continue
            
            try:
                self._load_plugin_file(file_path)
            except Exception as e:
                logger.error(f"加载插件失败 {file_path}: {str(e)}")
        
        logger.info(f"插件加载完成: {len(self.plugins)} 个")
    
    def _load_plugin_file(self, file_path: Path):
        """加载单个插件文件"""
        module_name = file_path.stem
        
        # 动态导入模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找插件类
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BasePlugin) and 
                obj != BasePlugin):
                
                # 实例化插件
                plugin = obj()
                plugin.on_load()
                
                self.plugins[plugin.name] = plugin
                logger.info(f"插件已加载: {plugin.name}")
    
    def get_plugin(self, name: str) -> BasePlugin:
        """
        获取插件
        
        Args:
            name: 插件名称
            
        Returns:
            插件实例
        """
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict]:
        """
        列出所有插件
        
        Returns:
            插件信息列表
        """
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def enable_plugin(self, name: str):
        """启用插件"""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enable()
    
    def disable_plugin(self, name: str):
        """禁用插件"""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.disable()
    
    def unload_plugin(self, name: str):
        """卸载插件"""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.on_unload()
            del self.plugins[name]
            logger.info(f"插件已卸载: {name}")
    
    def unload_all(self):
        """卸载所有插件"""
        for name in list(self.plugins.keys()):
            self.unload_plugin(name)
