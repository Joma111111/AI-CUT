"""
AI服务客户端
功能：统一的AI服务接口，支持多种AI提供商
"""

import openai
import google.generativeai as genai
from typing import List, Dict, Optional
from utils.logger import get_logger
from core.exceptions import AIServiceError
import config

logger = get_logger(__name__)


class AIClient:
    """AI服务客户端"""
    
    def __init__(self, provider: str = "gemini"):
        """
        初始化AI客户端
        
        Args:
            provider: AI提供商 (gemini, openai, claude)
        """
        self.provider = provider
        
        if provider == "gemini":
            self._init_gemini()
        elif provider == "openai":
            self._init_openai()
        elif provider == "claude":
            self._init_claude()
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        logger.info(f"AI客户端初始化: {provider}")
    
    def _init_gemini(self):
        """初始化Gemini"""
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def _init_openai(self):
        """初始化OpenAI"""
        openai.api_key = config.OPENAI_API_KEY
        if config.OPENAI_BASE_URL:
            openai.api_base = config.OPENAI_BASE_URL
        self.model_name = "gpt-4-turbo-preview"
    
    def _init_claude(self):
        """初始化Claude"""
        # TODO: 实现Claude初始化
        pass
    
    def generate_text(self,
                     prompt: str,
                     max_tokens: int = 2000,
                     temperature: float = 0.7) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
            max_tokens: 最大token数
            temperature: 温度参数
            
        Returns:
            生成的文本
            
        Raises:
            AIServiceError: AI服务错误
        """
        try:
            if self.provider == "gemini":
                return self._generate_gemini(prompt, max_tokens, temperature)
            elif self.provider == "openai":
                return self._generate_openai(prompt, max_tokens, temperature)
            elif self.provider == "claude":
                return self._generate_claude(prompt, max_tokens, temperature)
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise AIServiceError(f"文本生成失败: {str(e)}")
    
    def _generate_gemini(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """使用Gemini生成"""
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        )
        return response.text
    
    def _generate_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """使用OpenAI生成"""
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    
    def _generate_claude(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """使用Claude生成"""
        # TODO: 实现Claude生成
        raise NotImplementedError("Claude暂未实现")
    
    def generate_script_from_images(self,
                                   image_paths: List[str],
                                   style: str = "drama",
                                   context: str = "") -> List[str]:
        """
        根据图片生成文案
        
        Args:
            image_paths: 图片路径列表
            style: 解说风格
            context: 额外上下文
            
        Returns:
            文案列表
        """
        logger.info(f"生成图片文案: {len(image_paths)} 张图片")
        
        scripts = []
        
        for image_path in image_paths:
            # 构建提示词
            prompt = self._build_image_prompt(image_path, style, context)
            
            # 生成文案
            script = self.generate_text(prompt)
            scripts.append(script)
        
        return scripts
    
    def _build_image_prompt(self, image_path: str, style: str, context: str) -> str:
        """构建图片分析提示词"""
        style_prompts = {
            'drama': '请用戏剧化的语言描述这个画面',
            'funny': '请用幽默风趣的语言描述这个画面',
            'suspense': '请用悬疑紧张的语言描述这个画面',
            'documentary': '请用纪录片的客观语言描述这个画面',
            'casual': '请用轻松随意的语言描述这个画面',
        }
        
        base_prompt = style_prompts.get(style, style_prompts['drama'])
        
        if context:
            base_prompt += f"\n\n背景信息: {context}"
        
        base_prompt += "\n\n要求：\n1. 语言生动形象\n2. 长度控制在50-100字\n3. 适合作为视频解说"
        
        return base_prompt
    
    def optimize_script(self, script: str) -> str:
        """
        优化文案
        
        Args:
            script: 原始文案
            
        Returns:
            优化后的文案
        """
        logger.info("优化文案")
        
        prompt = f"""
请优化以下视频解说文案，使其更加生动、流畅、专业。

原文案：
{script}

优化要求：
1. 保持原意不变
2. 语言更加生动形象
3. 逻辑更加清晰
4. 适合口语表达
5. 长度与原文相近

请直接输出优化后的文案，不要添加其他说明。
"""
        
        return self.generate_text(prompt)
    
    def translate_script(self, script: str, target_lang: str = "en") -> str:
        """
        翻译文案
        
        Args:
            script: 原始文案
            target_lang: 目标语言
            
        Returns:
            翻译后的文案
        """
        logger.info(f"翻译文案: {target_lang}")
        
        lang_names = {
            'en': '英语',
            'ja': '日语',
            'ko': '韩语',
            'fr': '法语',
            'de': '德语',
            'es': '西班牙语',
        }
        
        target_name = lang_names.get(target_lang, target_lang)
        
        prompt = f"""
请将以下中文视频解说文案翻译成{target_name}。

原文案：
{script}

翻译要求：
1. 准确传达原意
2. 符合目标语言习惯
3. 适合作为视频解说
4. 保持语气和风格

请直接输出翻译结果，不要添加其他说明。
"""
        
        return self.generate_text(prompt)
    
    def summarize_video(self, scripts: List[str]) -> str:
        """
        总结视频内容
        
        Args:
            scripts: 文案列表
            
        Returns:
            总结文本
        """
        logger.info("总结视频内容")
        
        combined = "\n\n".join(scripts)
        
        prompt = f"""
请根据以下视频解说文案，总结视频的主要内容。

文案内容：
{combined}

总结要求：
1. 提炼核心主题
2. 概括主要情节
3. 长度控制在200字以内
4. 语言简洁明了

请直接输出总结内容，不要添加其他说明。
"""
        
        return self.generate_text(prompt)
    
    def generate_title(self, scripts: List[str], count: int = 5) -> List[str]:
        """
        生成视频标题
        
        Args:
            scripts: 文案列表
            count: 生成数量
            
        Returns:
            标题列表
        """
        logger.info(f"生成视频标题: {count} 个")
        
        combined = "\n\n".join(scripts[:3])  # 只用前3段
        
        prompt = f"""
请根据以下视频解说文案，生成{count}个吸引人的视频标题。

文案内容：
{combined}

标题要求：
1. 简洁有力，15-30字
2. 吸引眼球，引发好奇
3. 准确反映内容
4. 适合社交媒体传播

请以列表形式输出{count}个标题，每行一个，不要编号。
"""
        
        result = self.generate_text(prompt)
        titles = [line.strip() for line in result.split('\n') if line.strip()]
        
        return titles[:count]
    
    def generate_tags(self, scripts: List[str], count: int = 10) -> List[str]:
        """
        生成视频标签
        
        Args:
            scripts: 文案列表
            count: 生成数量
            
        Returns:
            标签列表
        """
        logger.info(f"生成视频标签: {count} 个")
        
        combined = "\n\n".join(scripts)
        
        prompt = f"""
请根据以下视频解说文案，提取{count}个相关标签。

文案内容：
{combined}

标签要求：
1. 准确反映内容主题
2. 适合搜索和分类
3. 简洁明了，2-5个字
4. 包含热门关键词

请以逗号分隔输出{count}个标签。
"""
        
        result = self.generate_text(prompt)
        tags = [tag.strip() for tag in result.split(',') if tag.strip()]
        
        return tags[:count]
