"""
性能测试脚本
"""

import time
import psutil
from pathlib import Path
from core.video_analyzer import VideoAnalyzer
from core.scene_detector import SceneDetector
from core.keyframe_extractor import KeyframeExtractor
from utils.logger import get_logger

logger = get_logger(__name__)


class Benchmark:
    """性能测试"""
    
    def __init__(self, video_path: str):
        """
        初始化测试
        
        Args:
            video_path: 测试视频路径
        """
        self.video_path = video_path
        self.results = {}
    
    def run_all(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("  AICraft 性能测试")
        print("="*60)
        
        print(f"\n测试视频: {self.video_path}")
        
        # 系统信息
        self.print_system_info()
        
        # 测试项目
        tests = [
            ("视频分析", self.test_video_analysis),
            ("镜头检测", self.test_scene_detection),
            ("关键帧提取", self.test_keyframe_extraction),
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"  {test_name}")
            print('='*60)
            
            try:
                result = test_func()
                self.results[test_name] = result
                self.print_result(result)
            except Exception as e:
                print(f"❌ 测试失败: {str(e)}")
        
        # 总结
        self.print_summary()
    
    def print_system_info(self):
        """打印系统信息"""
        print("\n系统信息:")
        print(f"  CPU: {psutil.cpu_count()} 核心")
        print(f"  内存: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"  可用内存: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    
    def test_video_analysis(self) -> dict:
        """测试视频分析"""
        analyzer = VideoAnalyzer()
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        info = analyzer.analyze(self.video_path)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        return {
            'duration': end_time - start_time,
            'memory': (end_memory - start_memory) / (1024**2),
            'video_duration': info['duration'],
            'fps': info['fps'],
        }
    
    def test_scene_detection(self) -> dict:
        """测试镜头检测"""
        detector = SceneDetector()
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        scenes = detector.detect(self.video_path)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        return {
            'duration': end_time - start_time,
            'memory': (end_memory - start_memory) / (1024**2),
            'scene_count': len(scenes),
        }
    
    def test_keyframe_extraction(self) -> dict:
        """测试关键帧提取"""
        detector = SceneDetector()
        scenes = detector.detect(self.video_path)
        
        extractor = KeyframeExtractor()
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        keyframes = extractor.extract(
            self.video_path,
            scenes,
            output_dir="temp/benchmark_keyframes"
        )
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        return {
            'duration': end_time - start_time,
            'memory': (end_memory - start_memory) / (1024**2),
            'keyframe_count': len(keyframes),
        }
    
    def print_result(self, result: dict):
        """打印测试结果"""
        print(f"\n耗时: {result['duration']:.2f} 秒")
        print(f"内存: {result['memory']:.2f} MB")
        
        for key, value in result.items():
            if key not in ['duration', 'memory']:
                print(f"{key}: {value}")
    
    def print_summary(self):
        """打印总结"""
        print("\n" + "="*60)
        print("  测试总结")
        print("="*60)
        
        total_time = sum(r['duration'] for r in self.results.values())
        total_memory = sum(r['memory'] for r in self.results.values())
        
        print(f"\n总耗时: {total_time:.2f} 秒")
        print(f"总内存: {total_memory:.2f} MB")
        
        print("\n各项测试:")
        for test_name, result in self.results.items():
            print(f"  {test_name}: {result['duration']:.2f}s")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python benchmark.py <video_path>")
        return 1
    
    video_path = sys.argv[1]
    
    if not Path(video_path).exists():
        print(f"❌ 视频文件不存在: {video_path}")
        return 1
    
    benchmark = Benchmark(video_path)
    benchmark.run_all()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
