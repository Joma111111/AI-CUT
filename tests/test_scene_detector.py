"""
镜头检测器测试
"""

import pytest
from core.scene_detector import SceneDetector


class TestSceneDetector:
    """镜头检测器测试类"""
    
    @pytest.fixture
    def detector(self):
        """创建检测器实例"""
        return SceneDetector(threshold=30.0)
    
    def test_detector_init(self, detector):
        """测试初始化"""
        assert detector is not None
        assert detector.threshold == 30.0
    
    def test_detect_scenes(self, detector):
        """测试镜头检测"""
        # 这里需要实际的测试视频
        # 暂时跳过
        pytest.skip("需要测试视频")
