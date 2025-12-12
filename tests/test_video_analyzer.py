"""
视频分析器测试
"""

import pytest
from pathlib import Path
from core.video_analyzer import VideoAnalyzer


class TestVideoAnalyzer:
    """视频分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建分析器实例"""
        return VideoAnalyzer()
    
    @pytest.fixture
    def sample_video(self):
        """示例视频路径"""
        # 需要准备一个测试视频
        return "tests/data/sample_video.mp4"
    
    def test_analyzer_init(self, analyzer):
        """测试初始化"""
        assert analyzer is not None
    
    def test_analyze_video(self, analyzer, sample_video):
        """测试视频分析"""
        if not Path(sample_video).exists():
            pytest.skip("测试视频不存在")
        
        info = analyzer.analyze(sample_video)
        
        assert 'duration' in info
        assert 'fps' in info
        assert 'width' in info
        assert 'height' in info
        assert info['duration'] > 0
        assert info['fps'] > 0
    
    def test_get_video_info(self, analyzer, sample_video):
        """测试获取视频信息"""
        if not Path(sample_video).exists():
            pytest.skip("测试视频不存在")
        
        info = analyzer.get_video_info(sample_video)
        
        assert isinstance(info, dict)
        assert 'format' in info
        assert 'streams' in info
