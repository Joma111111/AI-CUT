"""
云端服务客户端
功能：与云端服务器通信，实现云端处理
"""

import requests
from typing import Dict, List, Optional, BinaryIO
from utils.logger import get_logger
from core.exceptions import CloudAPIError
import config

logger = get_logger(__name__)


class CloudClient:
    """云端服务客户端"""
    
    def __init__(self, 
                 base_url: str = None,
                 api_key: str = None,
                 timeout: int = 30):
        """
        初始化云端客户端
        
        Args:
            base_url: 服务器地址
            api_key: API密钥
            timeout: 超时时间（秒）
        """
        self.base_url = base_url or config.CLOUD_SERVER_URL
        self.api_key = api_key or config.CLOUD_API_KEY
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': f'{config.APP_NAME}/{config.APP_VERSION}'
        })
        
        logger.info(f"云端客户端初始化: {self.base_url}")
    
    def _request(self, 
                method: str,
                endpoint: str,
                **kwargs) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: 请求方法
            endpoint: API端点
            **kwargs: 其他参数
            
        Returns:
            响应数据
            
        Raises:
            CloudAPIError: API错误
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            raise CloudAPIError(f"API请求失败: {str(e)}")
    
    def upload_video(self, 
                    video_path: str,
                    project_name: str,
                    progress_callback: Optional[callable] = None) -> Dict:
        """
        上传视频到云端
        
        Args:
            video_path: 视频路径
            project_name: 项目名称
            progress_callback: 进度回调
            
        Returns:
            上传结果
        """
        logger.info(f"上传视频: {video_path}")
        
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {'project_name': project_name}
            
            response = self._request(
                'POST',
                '/api/videos/upload',
                files=files,
                data=data
            )
        
        logger.info(f"视频上传成功: {response.get('video_id')}")
        return response
    
    def analyze_video(self, video_id: str) -> Dict:
        """
        云端分析视频
        
        Args:
            video_id: 视频ID
            
        Returns:
            分析结果
        """
        logger.info(f"请求云端分析: {video_id}")
        
        response = self._request(
            'POST',
            f'/api/videos/{video_id}/analyze'
        )
        
        return response
    
    def get_analysis_status(self, task_id: str) -> Dict:
        """
        获取分析任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态
        """
        response = self._request(
            'GET',
            f'/api/tasks/{task_id}/status'
        )
        
        return response
    
    def get_analysis_result(self, task_id: str) -> Dict:
        """
        获取分析结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            分析结果
        """
        logger.info(f"获取分析结果: {task_id}")
        
        response = self._request(
            'GET',
            f'/api/tasks/{task_id}/result'
        )
        
        return response
    
    def generate_script(self,
                       keyframes: List[Dict],
                       style: str = "drama",
                       length: int = 500) -> Dict:
        """
        云端生成文案
        
        Args:
            keyframes: 关键帧列表
            style: 解说风格
            length: 文案长度
            
        Returns:
            生成结果
        """
        logger.info(f"请求云端生成文案: {len(keyframes)} 个关键帧")
        
        response = self._request(
            'POST',
            '/api/scripts/generate',
            json={
                'keyframes': keyframes,
                'style': style,
                'length': length
            }
        )
        
        return response
    
    def synthesize_voice(self,
                        scripts: List[Dict],
                        voice: str,
                        rate: float = 1.0) -> Dict:
        """
        云端合成配音
        
        Args:
            scripts: 文案列表
            voice: 音色
            rate: 语速
            
        Returns:
            合成结果
        """
        logger.info(f"请求云端合成配音: {len(scripts)} 段")
        
        response = self._request(
            'POST',
            '/api/tts/synthesize',
            json={
                'scripts': scripts,
                'voice': voice,
                'rate': rate
            }
        )
        
        return response
    
    def download_file(self, file_url: str, output_path: str):
        """
        下载文件
        
        Args:
            file_url: 文件URL
            output_path: 输出路径
        """
        logger.info(f"下载文件: {file_url}")
        
        response = self.session.get(file_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"文件下载完成: {output_path}")
    
    def get_user_info(self) -> Dict:
        """
        获取用户信息
        
        Returns:
            用户信息
        """
        response = self._request('GET', '/api/user/info')
        return response
    
    def get_quota(self) -> Dict:
        """
        获取配额信息
        
        Returns:
            配额信息
        """
        response = self._request('GET', '/api/user/quota')
        return response
    
    def list_projects(self) -> List[Dict]:
        """
        列出云端项目
        
        Returns:
            项目列表
        """
        response = self._request('GET', '/api/projects')
        return response.get('projects', [])
    
    def sync_project(self, project_id: str, project_data: Dict) -> Dict:
        """
        同步项目到云端
        
        Args:
            project_id: 项目ID
            project_data: 项目数据
            
        Returns:
            同步结果
        """
        logger.info(f"同步项目: {project_id}")
        
        response = self._request(
            'POST',
            f'/api/projects/{project_id}/sync',
            json=project_data
        )
        
        return response
    
    def check_connection(self) -> bool:
        """
        检查连接状态
        
        Returns:
            是否连接成功
        """
        try:
            response = self._request('GET', '/api/health')
            return response.get('status') == 'ok'
        except:
            return False
