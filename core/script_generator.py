"""
文案生成器
功能：使用AI生成视频解说文案
"""

import os
import requests
from typing import List, Dict, Optional
from openai import OpenAI
from utils.logger import get_logger
from .exceptions import ScriptGenerationError
import config

logger = get_logger(__name__)


class ScriptGenerator:
    """文案生成器"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化文案生成器
        
        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        self.base_url = base_url or config.OPENAI_BASE_URL
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info("文案生成器初始化完成")
    
    def generate(self, 
                script_data: List[Dict],
                style: str = "drama",
                length: int = 500,
                context: Optional[str] = None,
                progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        根据剧本生成解说文案
        
        Args:
            script_data: 剧本数据（画面描述+对白+时间戳）
            style: 解说风格
            length: 文案长度
            context: 额外上下文
            progress_callback: 进度回调
            
        Returns:
            解说文案列表
        """
        logger.info(f"开始生成解说文案: {len(script_data)} 个镜头")
        
        # 使用新的 GPT-5 模型生成整体解说
        try:
            if progress_callback:
                progress_callback(20)
            
            commentary = self._generate_with_gpt5(script_data, style, length, context)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"解说文案生成完成: {len(commentary)} 字")
            
            # 返回统一格式
            return [{
                'scene_id': 'full',
                'script': commentary,
                'word_count': len(commentary),
            }]
        
        except Exception as e:
            logger.error(f"解说文案生成失败: {str(e)}", exc_info=True)
            raise ScriptGenerationError(f"解说文案生成失败: {str(e)}")
    
    def _generate_with_gpt5(self,
                           script_data: List[Dict],
                           style: str,
                           length: int,
                           context: Optional[str]) -> str:
        """使用 GPT-5 生成整体解说"""
        
        # 构建 prompt
        prompt = self._build_prompt_with_script_full(script_data, style, length, context)
        
        try:
            # 使用中转 API
            response = requests.post(
                f"{config.API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": getattr(config, 'CHAT_MODEL', 'gpt-5'),
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位专业的视频解说撰稿人，擅长根据视频内容生成引人入胜的解说词。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            commentary = result['choices'][0]['message']['content'].strip()
            return commentary
        
        except requests.exceptions.RequestException as e:
            logger.error(f"GPT-5 API 调用失败: {str(e)}")
            raise ScriptGenerationError(f"GPT-5 API 调用失败: {str(e)}")
        except Exception as e:
            logger.error(f"解说词解析失败: {str(e)}")
            raise ScriptGenerationError(f"解说词解析失败: {str(e)}")
    
    def _build_prompt_with_script_full(self,
                                      script_data: List[Dict],
                                      style: str,
                                      length: int,
                                      context: Optional[str]) -> str:
        """根据完整剧本构建提示词"""
        
        style_descriptions = {
            'drama': '剧情解说风格，注重情节发展和情感表达',
            'comedy': '搞笑解说风格，幽默风趣，轻松活泼',
            'suspense': '悬疑解说风格，营造紧张氛围，引发思考',
            'action': '动作解说风格，节奏紧凑，激情澎湃',
            'documentary': '纪录片风格，客观理性，信息丰富',
        }
        
        style_desc = style_descriptions.get(style, '专业解说风格')
        
        # 构建剧本摘要
        script_summary = []
        for scene in script_data:
            scene_info = f"""
镜头 {scene['scene_id']} ({scene['start_time']:.1f}s - {scene['end_time']:.1f}s):
- 画面: {scene['visual_description']}
- 对白: {scene['dialogue'] if scene['dialogue'] else '无对白'}
"""
            script_summary.append(scene_info.strip())
        
        script_text = "\n\n".join(script_summary)
        
        prompt = f"""你是一位专业的视频解说撰稿人。请根据以下视频剧本，生成一段{style_desc}的解说词。

要求：
1. 解说词要流畅自然，适合配音朗读
2. 要结合画面描述和对白内容
3. 风格：{style_desc}
4. 长度：适中，不要过长或过短
5. 不要使用"镜头1"、"scene_001"等技术术语
6. 直接输出解说词文本，不要有其他说明

视频剧本：
{script_text}

请生成解说词："""
        
        if context:
            prompt += f"\n\n额外背景信息：{context}"
        
        return prompt
    
    def _generate_for_scene(self,
                           scene_script: Dict,
                           style: str,
                           length: int,
                           context: Optional[str]) -> str:
        """为单个镜头生成解说（保留兼容性）"""
        
        # 构建提示词
        prompt = self._build_prompt_with_script(scene_script, style, length, context)
        
        # 调用 OpenAI
        return self._generate_with_openai(prompt)
    
    def _build_prompt_with_script(self,
                                  scene_script: Dict,
                                  style: str,
                                  length: int,
                                  context: Optional[str]) -> str:
        """根据剧本构建提示词"""
        
        style_descriptions = {
            'drama': '剧情解说风格，注重情节发展和情感表达',
            'comedy': '搞笑解说风格，幽默风趣，轻松活泼',
            'suspense': '悬疑解说风格，营造紧张氛围，引发思考',
            'action': '动作解说风格，节奏紧凑，激情澎湃',
            'documentary': '纪录片风格，客观理性，信息丰富',
        }
        
        style_desc = style_descriptions.get(style, '专业解说风格')
        
        prompt = f"""
你是一位专业的视频解说文案创作者。请根据以下视频剧本信息，创作一段{style_desc}的解说文案。

【剧本信息】
时间段：{scene_script['start_time']:.2f}秒 - {scene_script['end_time']:.2f}秒
时长：{scene_script['duration']:.2f}秒

画面描述：
{scene_script['visual_description']}
"""
        
        # 如果有对白，加入提示词
        if scene_script.get('dialogue'):
            prompt += f"""
视频对白：
"{scene_script['dialogue']}"
"""
        
        prompt += f"""
【创作要求】
1. 文案长度约 {length // len([scene_script])} 字（根据时长调整）
2. 风格：{style_desc}
3. 紧密结合画面描述和对白内容
4. 语言流畅自然，富有感染力
5. 适合作为视频旁白使用
6. 不要重复对白内容，而是补充解说

【重要】
- 如果有对白，解说要与对白配合，不要冲突
- 解说要补充画面信息，而不是简单描述
- 保持解说的连贯性和节奏感

请直接输出解说文案，不要包含任何解释或标注。
"""
        
        if context:
            prompt += f"\n\n额外背景信息：{context}"
        
        return prompt
    
    def _generate_with_openai(self, prompt: str) -> str:
        """调用OpenAI生成文案"""
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的视频解说文案创作者，擅长创作各种风格的解说文案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            script = response.choices[0].message.content.strip()
            return script
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}", exc_info=True)
            raise ScriptGenerationError(f"文案生成失败: {str(e)}")
    
    def optimize(self, script: str, requirements: str) -> str:
        """
        优化文案
        
        Args:
            script: 原文案
            requirements: 优化要求
            
        Returns:
            优化后的文案
        """
        prompt = f"""
请优化以下视频解说文案：

【原文案】
{script}

【优化要求】
{requirements}

请直接输出优化后的文案，不要包含任何解释。
"""
        
        return self._generate_with_openai(prompt)
    
    def batch_generate(self,
                      script_data_list: List[Dict],
                      style: str = "drama",
                      length: int = 500,
                      progress_callback: Optional[callable] = None) -> List[Dict]:
        """
        批量生成文案（已废弃，使用generate方法）
        """
        return self.generate(script_data_list, style, length, None, progress_callback)
