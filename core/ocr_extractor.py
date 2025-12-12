"""
OCR文字提取器
从视频帧中提取文字信息
"""

import os
from typing import List, Dict
from paddleocr import PaddleOCR
# 或者使用 EasyOCR
# from easyocr import Reader


class OCRExtractor:
    """OCR文字提取器"""
    
    def __init__(self):
        # 初始化 PaddleOCR
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',  # 中文
            use_gpu=True  # 如果有GPU
        )
        
        # 或者使用 EasyOCR
        # self.reader = Reader(['ch_sim', 'en'])
    
    def extract_text_from_frames(
        self,
        keyframes: List[str],
        timestamps: List[float]
    ) -> List[Dict]:
        """
        从关键帧中提取文字
        
        Args:
            keyframes: 关键帧路径列表
            timestamps: 对应的时间戳列表
        
        Returns:
            文字信息列表
            [
                {
                    'timestamp': 10.0,
                    'frame_path': 'keyframe_001.jpg',
                    'texts': [
                        {'text': 'WARNER BROS. PICTURES', 'confidence': 0.98},
                        {'text': 'LEGENDARY PICTURES', 'confidence': 0.95}
                    ]
                }
            ]
        """
        ocr_results = []
        
        for frame_path, timestamp in zip(keyframes, timestamps):
            # 使用 PaddleOCR 识别
            result = self.ocr.ocr(frame_path, cls=True)
            
            # 提取文字和置信度
            texts = []
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]  # 文字内容
                    confidence = line[1][1]  # 置信度
                    
                    # 过滤低置信度结果
                    if confidence > 0.7:
                        texts.append({
                            'text': text,
                            'confidence': confidence
                        })
            
            if texts:
                ocr_results.append({
                    'timestamp': timestamp,
                    'frame_path': frame_path,
                    'texts': texts
                })
        
        return ocr_results
    
    def save_ocr_results(self, ocr_results: List[Dict], output_path: str):
        """保存OCR结果"""
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_results, f, ensure_ascii=False, indent=2)
