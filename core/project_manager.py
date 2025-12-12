"""
项目管理器
功能：项目的创建、保存、加载、同步等
"""

import os
import json
import shutil
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger
from .exceptions import ProjectManagerError
from database.db_manager import DatabaseManager
import config

logger = get_logger(__name__)


class ProjectManager:
    """项目管理器"""
    
    def __init__(self):
        """初始化项目管理器"""
        self.db = DatabaseManager()
        self.projects_dir = Path(config.PROJECTS_DIR)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("项目管理器初始化完成")
    
    def create_project(self, 
                      name: str,
                      video_path: str,
                      description: str = "") -> Dict:
        """
        创建新项目
        
        Args:
            name: 项目名称
            video_path: 视频文件路径
            description: 项目描述
            
        Returns:
            项目信息
            
        Raises:
            ProjectManagerError: 创建失败时抛出
        """
        logger.info(f"创建项目: {name}")
        
        try:
            # 生成项目ID
            project_id = self._generate_project_id(name)
            
            # 创建项目目录
            project_dir = self.projects_dir / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制视频文件到项目目录
            video_filename = os.path.basename(video_path)
            project_video_path = project_dir / video_filename
            shutil.copy2(video_path, project_video_path)
            
            # 创建子目录
            (project_dir / "keyframes").mkdir(exist_ok=True)
            (project_dir / "audios").mkdir(exist_ok=True)
            (project_dir / "exports").mkdir(exist_ok=True)
            
            # 项目信息
            project_info = {
                'id': project_id,
                'name': name,
                'description': description,
                'video_path': str(project_video_path),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'version': 1,
                'status': 'created',
            }
            
            # 保存到数据库
            self.db.save_project(project_info)
            
            # 保存项目文件
            self._save_project_file(project_id, project_info)
            
            logger.info(f"项目创建完成: {project_id}")
            return project_info
            
        except Exception as e:
            logger.error(f"项目创建失败: {str(e)}", exc_info=True)
            raise ProjectManagerError(f"项目创建失败: {str(e)}")
    
    def load_project(self, project_id: str) -> Dict:
        """
        加载项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目完整数据
            
        Raises:
            ProjectManagerError: 加载失败时抛出
        """
        logger.info(f"加载项目: {project_id}")
        
        try:
            # 从数据库加载
            project_info = self.db.get_project(project_id)
            
            if not project_info:
                raise ProjectManagerError(f"项目不存在: {project_id}")
            
            # 加载项目文件
            project_file = self.projects_dir / project_id / "project.json"
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
            else:
                project_data = project_info
            
            # 加载场景数据
            scenes = self.db.get_project_scenes(project_id)
            project_data['scenes'] = scenes
            
            # 加载文案数据
            scripts = self.db.get_project_scripts(project_id)
            project_data['scripts'] = scripts
            
            logger.info(f"项目加载完成: {project_id}")
            return project_data
            
        except Exception as e:
            logger.error(f"项目加载失败: {str(e)}", exc_info=True)
            raise ProjectManagerError(f"项目加载失败: {str(e)}")
    
    def save_project(self, project_id: str, project_data: Dict):
        """
        保存项目
        
        Args:
            project_id: 项目ID
            project_data: 项目数据
        """
        logger.info(f"保存项目: {project_id}")
        
        try:
            # 更新时间
            project_data['updated_at'] = datetime.now().isoformat()
            project_data['version'] = project_data.get('version', 1) + 1
            
            # 保存到数据库
            self.db.update_project(project_id, project_data)
            
            # 保存场景数据
            if 'scenes' in project_data:
                self.db.save_project_scenes(project_id, project_data['scenes'])
            
            # 保存文案数据
            if 'scripts' in project_data:
                self.db.save_project_scripts(project_id, project_data['scripts'])
            
            # 保存项目文件
            self._save_project_file(project_id, project_data)
            
            logger.info(f"项目保存完成: {project_id}")
            
        except Exception as e:
            logger.error(f"项目保存失败: {str(e)}", exc_info=True)
            raise ProjectManagerError(f"项目保存失败: {str(e)}")
    
    def delete_project(self, project_id: str):
        """
        删除项目
        
        Args:
            project_id: 项目ID
        """
        logger.info(f"删除项目: {project_id}")
        
        try:
            # 从数据库删除
            self.db.delete_project(project_id)
            
            # 删除项目目录
            project_dir = self.projects_dir / project_id
            if project_dir.exists():
                shutil.rmtree(project_dir)
            
            logger.info(f"项目删除完成: {project_id}")
            
        except Exception as e:
            logger.error(f"项目删除失败: {str(e)}", exc_info=True)
            raise ProjectManagerError(f"项目删除失败: {str(e)}")
    
    def list_projects(self) -> List[Dict]:
        """
        列出所有项目
        
        Returns:
            项目列表
        """
        logger.info("列出所有项目")
        
        try:
            projects = self.db.list_projects()
            return projects
            
        except Exception as e:
            logger.error(f"列出项目失败: {str(e)}", exc_info=True)
            raise ProjectManagerError(f"列出项目失败: {str(e)}")
    
    def export_project(self, 
                      project_id: str,
                      output_path: str,
                      include_source: bool = True) -> str:
        """
        导出项目
        
        Args:
            project_id: 项目ID
            output_path: 输出路径
            include_source: 是否包含源文件
            
        Returns:
            导出文件路径
        """
        logger.info(f"导出项目: {project_id}")
        
        try:
            import zipfile
            
            project_dir = self.projects_dir / project_id
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加项目文件
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(project_dir)
                        
                        # 如果不包含源文件，跳过视频文件
                        if not include_source and file_path.suffix in ['.mp4', '.avi', '.mov']:
                            continue
                        
                        zipf.write(file_path, arcname)
            
            logger.info(f"项目导出完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"项目导出失败: {str(e)}", exc_info=True)
            raise ProjectManagerError(f"项目导出失败: {str(e)}")
    
    def import_project(self, zip_path: str) -> str:
        """
        导入项目
        
        Args:
            zip_path: 项目压缩包路径
            
        Returns:
            项目ID
        """
        logger.info(f"导入项目: {zip_path}")
        
        try:
            import zipfile
            
            # 解压到临时目录
            temp_dir = Path(config.TEMP_DIR) / f"import_{os.getpid()}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # 读取项目信息
            project_file = temp_dir / "project.json"
            with open(project_file, 'r', encoding='utf-8') as f:
                project_info = json.load(f)
            
            project_id = project_info['id']
            
            # 移动到项目目录
            target_dir = self.projects_dir / project_id
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.move(str(temp_dir), str(target_dir))
            
            # 保存到数据库
            self.db.save_project(project_info)
            
            logger.info(f"项目导入完成: {project_id}")
            return project_id
            
        except Exception as e:
            logger.error(f"项目导入失败: {str(e)}", exc_info=True)
            raise ProjectManagerError(f"项目导入失败: {str(e)}")
    
    def _generate_project_id(self, name: str) -> str:
        """生成项目ID"""
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_str = hashlib.md5(f"{name}{timestamp}".encode()).hexdigest()[:8]
        return f"project_{timestamp}_{hash_str}"
    
    def _save_project_file(self, project_id: str, project_data: Dict):
        """保存项目文件"""
        project_file = self.projects_dir / project_id / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
    
    def get_project_path(self, project_id: str, subdir: str = "") -> Path:
        """
        获取项目路径
        
        Args:
            project_id: 项目ID
            subdir: 子目录名称
            
        Returns:
            路径对象
        """
        path = self.projects_dir / project_id
        if subdir:
            path = path / subdir
        return path
