"""
pytest配置文件
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def sample_video(test_data_dir):
    """示例视频"""
    video_path = test_data_dir / "sample_video.mp4"
    if video_path.exists():
        return str(video_path)
    return None
