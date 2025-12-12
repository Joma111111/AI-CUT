"""
人脸识别器
识别视频中的人物/演员
"""

import os
from typing import List, Dict
import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceRecognizer:
    """人脸识别器"""
    
    def __init__(self, celebrity_db_path: str = None):
        # 初始化 InsightFace
        self.app = FaceAnalysis(
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        # 加载名人数据库（可选）
        self.celebrity_db = self._load_celebrity_db(celebrity_db_path)
    
    def recognize_faces_in_frames(
        self,
        keyframes: List[str],
        timestamps: List[float]
    ) -> List[Dict]:
        """
        识别关键帧中的人脸
        
        Returns:
            人脸信息列表
            [
                {
                    'timestamp': 72.0,
                    'frame_path': 'keyframe_010.jpg',
                    'faces': [
                        {
                            'bbox': [100, 200, 300, 400],
                            'age': 35,
                            'gender': 'M',
                            'emotion': 'surprised',
                            'celebrity': 'TOM HIDDLESTON'  # 如果识别出来
                        }
                    ]
                }
            ]
        """
        face_results = []
        
        for frame_path, timestamp in zip(keyframes, timestamps):
            # 读取图片
            img = cv2.imread(frame_path)
            
            # 检测人脸
            faces = self.app.get(img)
            
            if faces:
                face_info = []
                
                for face in faces:
                    info = {
                        'bbox': face.bbox.tolist(),
                        'age': int(face.age),
                        'gender': 'M' if face.gender == 1 else 'F',
                        'embedding': face.embedding.tolist()  # 用于匹配
                    }
                    
                    # 如果有名人数据库，尝试匹配
                    if self.celebrity_db:
                        celebrity = self._match_celebrity(face.embedding)
                        if celebrity:
                            info['celebrity'] = celebrity
                    
                    face_info.append(info)
                
                face_results.append({
                    'timestamp': timestamp,
                    'frame_path': frame_path,
                    'faces': face_info
                })
        
        return face_results
    
    def _load_celebrity_db(self, db_path: str) -> Dict:
        """加载名人数据库"""
        if not db_path or not os.path.exists(db_path):
            return None
        
        # TODO: 实现名人数据库加载
        # 格式: {'TOM HIDDLESTON': embedding_vector, ...}
        return {}
    
    def _match_celebrity(self, embedding: np.ndarray) -> str:
        """匹配名人"""
        # TODO: 实现embedding匹配
        # 使用余弦相似度找到最接近的名人
        return None
