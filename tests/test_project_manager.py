"""
项目管理器测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from core.project_manager import ProjectManager


class TestProjectManager:
    """项目管理器测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """创建管理器实例"""
        return ProjectManager()
    
    def test_create_project(self, manager, temp_dir):
        """测试创建项目"""
        # 创建测试视频文件
        test_video = Path(temp_dir) / "test.mp4"
        test_video.touch()
        
        project = manager.create_project(
            name="测试项目",
            video_path=str(test_video),
            description="这是一个测试项目"
        )
        
        assert project is not None
        assert project['name'] == "测试项目"
        assert 'id' in project
    
    def test_load_project(self, manager):
        """测试加载项目"""
        # 需要先创建项目
        pytest.skip("需要先创建项目")
    
    def test_list_projects(self, manager):
        """测试列出项目"""
        projects = manager.list_projects()
        assert isinstance(projects, list)
