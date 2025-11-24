# -*- coding: utf-8 -*-
"""
食物碳排放检测系统 - AI视觉识别模块
Food Carbon Emission Detection System - AI Vision Recognition Module

基于Google Gemini Pro Vision API的食物识别系统
Food recognition system based on Google Gemini Pro Vision API

功能特性 Features:
- 智能食物识别和分类
- 多模态分析（图像+重量信息）
- 食物质量和新鲜度评估
- 智能提示词优化
- 批量识别和分析
- 置信度评估和验证
"""

import os
import time
import base64
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import requests
from datetime import datetime

# 导入配置
from config.system_config import ai_config

@dataclass
class RecognitionResult:
    """
    识别结果数据类
    Recognition Result Data Class
    """
    food_name: str                    # 食物名称
    confidence: float                 # 置信度 (0-1)
    category: str                     # 食物类别
    description: str                  # 详细描述
    estimated_weight: Optional[float] # 估计重量(克)
    freshness: Optional[str]          # 新鲜度
    quality: Optional[str]            # 质量评估
    ingredients: List[str]            # 成分列表
    nutritional_info: Dict           # 营养信息
    processing_time: float           # 处理时间(秒)
    api_response: str                # 原始API响应
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'food_name': self.food_name,
            'confidence': self.confidence,
            'category': self.category,
            'description': self.description,
            'estimated_weight': self.estimated_weight,
            'freshness': self.freshness,
            'quality': self.quality,
            'ingredients': self.ingredients,
            'nutritional_info': self.nutritional_info,
            'processing_time': self.processing_time,
            'timestamp': datetime.now().isoformat()
        }


class ImageProcessor:
    """
    图像预处理器
    Image Preprocessor
    """
    
    def __init__(self):
        """初始化图像处理器"""
        self.target_size = (ai_config.image_resize_width, ai_config.image_resize_height)
        self.quality = 95
        
    def preprocess_image(self, image_path: str) -> str:
        """
        预处理图像并转换为Base64
        Preprocess image and convert to Base64
        
        Args:
            image_path (str): 图像文件路径
            
        Returns:
            str: Base64编码的图像数据
        """
        try:
            # 读取图像
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                # 假设是numpy数组
                image = Image.fromarray(image_path)
            
            # 图像增强
            enhanced_image = self._enhance_image(image)
            
            # 调整大小
            resized_image = self._resize_image(enhanced_image)
            
            # 转换为Base64
            base64_data = self._image_to_base64(resized_image)
            
            return base64_data
            
        except Exception as e:
            logging.error(f"图像预处理失败: {e}")
            raise
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """
        增强图像质量
        Enhance image quality
        
        Args:
            image (Image.Image): 原始图像
            
        Returns:
            Image.Image: 增强后的图像
        """
        # 亮度增强
        brightness_enhancer = ImageEnhance.Brightness(image)
        enhanced = brightness_enhancer.enhance(1.1)
        
        # 对比度增强
        contrast_enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = contrast_enhancer.enhance(1.1)
        
        # 锐化
        sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = sharpness_enhancer.enhance(1.05)
        
        # 色彩增强
        color_enhancer = ImageEnhance.Color(enhanced)
        enhanced = color_enhancer.enhance(1.05)
        
        return enhanced
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        调整图像大小
        Resize image
        
        Args:
            image (Image.Image): 原始图像
            
        Returns:
            Image.Image: 调整大小后的图像
        """
        # 保持宽高比
        image.thumbnail(self.target_size, Image.Resampling.LANCZOS)
        
        # 创建白色背景
        background = Image.new('RGB', self.target_size, (255, 255, 255))
        
        # 居中放置图像
        offset = ((self.target_size[0] - image.size[0]) // 2,
                 (self.target_size[1] - image.size[1]) // 2)
        background.paste(image, offset)
        
        return background
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """
        将图像转换为Base64编码
        Convert image to Base64 encoding
        
        Args:
            image (Image.Image): 图像对象
            
        Returns:
            str: Base64编码字符串
        """
        import io
        
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=self.quality)
        buffer.seek(0)
        
        image_data = buffer.getvalue()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        return base64_data
    
    def capture_from_camera(self, camera_index: int = 0) -> Optional[str]:
        """
        从摄像头捕获图像
        Capture image from camera
        
        Args:
            camera_index (int): 摄像头索引
            
        Returns:
            Optional[str]: Base64编码的图像数据
        """
        try:
            # 初始化摄像头
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                logging.error("无法打开摄像头")
                return None
            
            # 设置摄像头参数
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # 预热摄像头
            for _ in range(5):
                cap.read()
            
            # 捕获图像
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logging.error("无法捕获图像")
                return None
            
            # 转换颜色空间
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为PIL图像并处理
            pil_image = Image.fromarray(frame_rgb)
            enhanced_image = self._enhance_image(pil_image)
            resized_image = self._resize_image(enhanced_image)
            
            return self._image_to_base64(resized_image)
            
        except Exception as e:
            logging.error(f"摄像头捕获失败: {e}")
            return None


class PromptGenerator:
    """
    智能提示词生成器
    Intelligent Prompt Generator
    """
    
    def __init__(self):
        """初始化提示词生成器"""
        self.base_prompt_zh = """
        请分析这张图片中的食物，并提供以下信息：

        1. 食物名称（中文和英文）
        2. 食物类别（如：肉类、蔬菜、水果、谷物等）
        3. 详细描述食物的外观、颜色、质地
        4. 估计重量（克）
        5. 新鲜度评估（新鲜/一般/不新鲜）
        6. 质量评估（优质/良好/一般/较差）
        7. 主要成分或配料
        8. 简要营养信息
        9. 识别置信度（0-100%）

        请用JSON格式回答，确保所有字段都填写完整。
        """
        
        self.base_prompt_en = """
        You are a highly accurate food recognition AI. Analyze this image and identify the food with precision.

        CRITICAL REQUIREMENTS:
        1. Return ONLY the standard English food name (e.g., "apple", "beef", "rice", "chicken")
        2. Use common, simple English food names that match a database
        3. If multiple foods are present, identify the MAIN/PRIMARY food item
        4. Be very specific - avoid generic terms like "fruit" or "vegetable"
        5. For prepared foods, identify the main ingredient (e.g., "chicken" for chicken sandwich)

        Respond with a JSON object containing:
        {
            "food_name": "standard_english_name",
            "category": "meat/vegetable/fruit/grain/dairy/seafood/nuts",
            "confidence": 0.95,
            "description": "brief description"
        }

        EXAMPLES:
        - Red apple → "apple"
        - Grilled chicken breast → "chicken" 
        - White rice → "rice"
        - Cheddar cheese → "cheese"
        - Fresh salmon → "salmon"

        Focus on accuracy and use the most common English name for the food.
        """
    
    def generate_prompt(
        self, 
        weight_info: Optional[float] = None,
        context: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """
        生成智能提示词
        Generate intelligent prompt
        
        Args:
            weight_info (Optional[float]): 称重信息（克）
            context (Optional[str]): 上下文信息
            language (str): 语言（zh/en）
            
        Returns:
            str: 生成的提示词
        """
        if language == "zh":
            prompt = self.base_prompt_zh
        else:
            prompt = self.base_prompt_en
        
        # 添加重量信息
        if weight_info is not None:
            weight_hint = f"\n\n已知重量信息：{weight_info:.1f}克，请结合此信息进行分析。"
            if language == "en":
                weight_hint = f"\n\nKnown weight information: {weight_info:.1f}g, please analyze considering this information."
            prompt += weight_hint
        
        # 添加上下文信息
        if context:
            context_hint = f"\n\n上下文信息：{context}"
            if language == "en":
                context_hint = f"\n\nContext information: {context}"
            prompt += context_hint
        
        # 添加特殊指令
        if language == "zh":
            prompt += """
            
            特别注意：
            - 如果图片中有多种食物，请识别主要的食物
            - 如果无法确定具体食物，请给出最可能的分类
            - 置信度要真实反映识别的准确性
            - 重量估计要合理，考虑食物的密度和体积
            """
        else:
            prompt += """
            
            Special instructions:
            - If there are multiple foods in the image, identify the main food item
            - If specific food cannot be determined, provide the most likely category
            - Confidence should realistically reflect recognition accuracy
            - Weight estimation should be reasonable, considering food density and volume
            """
        
        return prompt
    
    def generate_comparison_prompt(self, food_list: List[str]) -> str:
        """
        生成食物对比提示词
        Generate food comparison prompt
        
        Args:
            food_list (List[str]): 食物列表
            
        Returns:
            str: 对比提示词
        """
        foods_str = "、".join(food_list)
        
        prompt = f"""
        请比较分析图片中的食物与以下食物的相似性：{foods_str}

        请提供：
        1. 与每种食物的相似度评分（0-100%）
        2. 最相似的食物及原因
        3. 主要差异点分析
        4. 最终识别结果

        请用JSON格式回答。
        """
        
        return prompt


class VisionAI:
    """
    视觉AI识别主类
    Vision AI Recognition Main Class
    """
    
    def __init__(self):
        """初始化视觉AI系统"""
        self.image_processor = ImageProcessor()
        self.prompt_generator = PromptGenerator()
        
        # 配置Gemini API
        self._configure_gemini()
        
        # 统计信息
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # 缓存
        self.response_cache = {}
        self.cache_max_size = 100
        
        logging.info("视觉AI系统初始化完成")
    
    def _configure_gemini(self):
        """配置Gemini API"""
        try:
            genai.configure(api_key=ai_config.api_key)
            
            # 安全设置
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # 生成配置
            self.generation_config = {
                "temperature": 0.1,  # 降低随机性
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            # 初始化模型
            self.model = genai.GenerativeModel(
                model_name=ai_config.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            logging.info(f"Gemini模型配置完成: {ai_config.model_name}")
            
        except Exception as e:
            logging.error(f"Gemini API配置失败: {e}")
            raise
    
    def recognize_food(
        self,
        image_source: Union[str, np.ndarray],
        weight_info: Optional[float] = None,
        context: Optional[str] = None
    ) -> RecognitionResult:
        """
        识别食物
        Recognize food
        
        Args:
            image_source (Union[str, np.ndarray]): 图像源（文件路径或numpy数组）
            weight_info (Optional[float]): 重量信息（克）
            context (Optional[str]): 上下文信息
            
        Returns:
            RecognitionResult: 识别结果
        """
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # 预处理图像
            if isinstance(image_source, str):
                base64_image = self.image_processor.preprocess_image(image_source)
            else:
                # numpy数组
                pil_image = Image.fromarray(image_source)
                enhanced = self.image_processor._enhance_image(pil_image)
                resized = self.image_processor._resize_image(enhanced)
                base64_image = self.image_processor._image_to_base64(resized)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(base64_image, weight_info, context)
            
            # 检查缓存
            if cache_key in self.response_cache:
                logging.info("使用缓存的识别结果")
                cached_result = self.response_cache[cache_key]
                cached_result.processing_time = time.time() - start_time
                return cached_result
            
            # 生成提示词
            prompt = self.prompt_generator.generate_prompt(weight_info, context)
            
            # 调用API进行识别
            result = self._call_gemini_api(base64_image, prompt)
            
            # 解析响应
            recognition_result = self._parse_response(result, time.time() - start_time)
            
            # 后处理
            recognition_result = self._post_process_result(recognition_result, weight_info)
            
            # 缓存结果
            self._cache_result(cache_key, recognition_result)
            
            self.successful_requests += 1
            logging.info(f"食物识别成功: {recognition_result.food_name}")
            
            return recognition_result
            
        except Exception as e:
            self.failed_requests += 1
            logging.error(f"食物识别失败: {e}")
            
            # 返回默认结果
            return self._create_fallback_result(str(e), time.time() - start_time)
    
    def _call_gemini_api(self, base64_image: str, prompt: str) -> str:
        """
        调用Gemini API
        Call Gemini API
        
        Args:
            base64_image (str): Base64编码的图像
            prompt (str): 提示词
            
        Returns:
            str: API响应
        """
        max_retries = ai_config.max_retries
        retry_delay = ai_config.retry_delay
        
        for attempt in range(max_retries):
            try:
                # 准备图像数据
                image_parts = [
                    {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                ]
                
                # 发送请求
                response = self.model.generate_content(
                    [prompt] + image_parts,
                    safety_settings=self.safety_settings,
                    generation_config=self.generation_config
                )
                
                if response.text:
                    return response.text
                else:
                    raise Exception("API返回空响应")
                    
            except Exception as e:
                logging.warning(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    raise Exception(f"API调用失败，已重试{max_retries}次: {e}")
    
    def _parse_response(self, response_text: str, processing_time: float) -> RecognitionResult:
        """
        解析API响应
        Parse API response
        
        Args:
            response_text (str): API响应文本
            processing_time (float): 处理时间
            
        Returns:
            RecognitionResult: 解析后的识别结果
        """
        try:
            # 尝试提取JSON
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)
            
            # 解析字段
            food_name = data.get('food_name', data.get('名称', '未知食物'))
            confidence = float(data.get('confidence', data.get('置信度', 50))) / 100.0
            category = data.get('category', data.get('类别', '未知'))
            description = data.get('description', data.get('描述', ''))
            
            # 重量信息
            estimated_weight = data.get('estimated_weight', data.get('估计重量'))
            if isinstance(estimated_weight, str):
                # 尝试从字符串中提取数字
                import re
                numbers = re.findall(r'\d+\.?\d*', estimated_weight)
                estimated_weight = float(numbers[0]) if numbers else None
            
            # 质量评估
            freshness = data.get('freshness', data.get('新鲜度'))
            quality = data.get('quality', data.get('质量'))
            
            # 成分和营养信息
            ingredients = data.get('ingredients', data.get('成分', []))
            if isinstance(ingredients, str):
                ingredients = [ing.strip() for ing in ingredients.split(',')]
            
            nutritional_info = data.get('nutritional_info', data.get('营养信息', {}))
            if isinstance(nutritional_info, str):
                nutritional_info = {'description': nutritional_info}
            
            return RecognitionResult(
                food_name=food_name,
                confidence=max(0.0, min(1.0, confidence)),  # 限制在0-1范围
                category=category,
                description=description,
                estimated_weight=estimated_weight,
                freshness=freshness,
                quality=quality,
                ingredients=ingredients,
                nutritional_info=nutritional_info,
                processing_time=processing_time,
                api_response=response_text
            )
            
        except Exception as e:
            logging.error(f"响应解析失败: {e}")
            logging.debug(f"原始响应: {response_text}")
            
            # 回退到文本解析
            return self._fallback_text_parse(response_text, processing_time)
    
    def _extract_json(self, text: str) -> str:
        """
        从文本中提取JSON
        Extract JSON from text
        
        Args:
            text (str): 包含JSON的文本
            
        Returns:
            str: 提取的JSON字符串
        """
        # 寻找JSON块
        import re
        
        # 尝试匹配 ```json ... ``` 格式
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # 尝试匹配 {...} 格式
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # 如果都没找到，返回原文本
        return text
    
    def _fallback_text_parse(self, text: str, processing_time: float) -> RecognitionResult:
        """
        回退文本解析
        Fallback text parsing
        
        Args:
            text (str): 响应文本
            processing_time (float): 处理时间
            
        Returns:
            RecognitionResult: 识别结果
        """
        # 简单的文本解析逻辑
        lines = text.split('\n')
        
        food_name = "未知食物"
        confidence = 0.5
        category = "未知"
        description = text[:200]  # 前200字符作为描述
        
        # 尝试从文本中提取信息
        for line in lines:
            line = line.strip()
            if '名称' in line or 'name' in line.lower():
                # 提取食物名称
                parts = line.split(':')
                if len(parts) > 1:
                    food_name = parts[1].strip()
            elif '类别' in line or 'category' in line.lower():
                parts = line.split(':')
                if len(parts) > 1:
                    category = parts[1].strip()
        
        return RecognitionResult(
            food_name=food_name,
            confidence=confidence,
            category=category,
            description=description,
            estimated_weight=None,
            freshness=None,
            quality=None,
            ingredients=[],
            nutritional_info={},
            processing_time=processing_time,
            api_response=text
        )
    
    def _post_process_result(
        self, 
        result: RecognitionResult, 
        weight_info: Optional[float]
    ) -> RecognitionResult:
        """
        后处理识别结果
        Post-process recognition result
        
        Args:
            result (RecognitionResult): 原始识别结果
            weight_info (Optional[float]): 实际重量信息
            
        Returns:
            RecognitionResult: 后处理后的结果
        """
        # 如果有实际重量信息，进行验证和调整
        if weight_info is not None and result.estimated_weight is not None:
            weight_diff = abs(result.estimated_weight - weight_info)
            weight_ratio = weight_diff / max(weight_info, 1.0)
            
            # 如果重量差异过大，降低置信度
            if weight_ratio > 0.5:  # 差异超过50%
                result.confidence *= 0.7
            elif weight_ratio > 0.3:  # 差异超过30%
                result.confidence *= 0.9
            
            # 更新估计重量为实际重量
            result.estimated_weight = weight_info
        
        # 置信度验证
        if result.confidence < ai_config.confidence_threshold:
            logging.warning(f"识别置信度较低: {result.confidence:.2f}")
        
        return result
    
    def _create_fallback_result(self, error_msg: str, processing_time: float) -> RecognitionResult:
        """
        创建回退识别结果
        Create fallback recognition result
        
        Args:
            error_msg (str): 错误信息
            processing_time (float): 处理时间
            
        Returns:
            RecognitionResult: 回退结果
        """
        return RecognitionResult(
            food_name="识别失败",
            confidence=0.0,
            category="未知",
            description=f"识别过程中发生错误: {error_msg}",
            estimated_weight=None,
            freshness=None,
            quality=None,
            ingredients=[],
            nutritional_info={},
            processing_time=processing_time,
            api_response=""
        )
    
    def _generate_cache_key(
        self, 
        base64_image: str, 
        weight_info: Optional[float], 
        context: Optional[str]
    ) -> str:
        """
        生成缓存键
        Generate cache key
        
        Args:
            base64_image (str): Base64图像数据
            weight_info (Optional[float]): 重量信息
            context (Optional[str]): 上下文
            
        Returns:
            str: 缓存键
        """
        import hashlib
        
        # 计算图像hash
        image_hash = hashlib.md5(base64_image.encode()).hexdigest()[:16]
        
        # 组合其他信息
        key_parts = [image_hash]
        if weight_info is not None:
            key_parts.append(f"w{weight_info:.1f}")
        if context:
            key_parts.append(hashlib.md5(context.encode()).hexdigest()[:8])
        
        return "_".join(key_parts)
    
    def _cache_result(self, cache_key: str, result: RecognitionResult):
        """
        缓存识别结果
        Cache recognition result
        
        Args:
            cache_key (str): 缓存键
            result (RecognitionResult): 识别结果
        """
        # 限制缓存大小
        if len(self.response_cache) >= self.cache_max_size:
            # 移除最老的条目
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        
        self.response_cache[cache_key] = result
    
    def capture_and_recognize(
        self, 
        camera_index: int = 0,
        weight_info: Optional[float] = None
    ) -> RecognitionResult:
        """
        从摄像头捕获并识别
        Capture from camera and recognize
        
        Args:
            camera_index (int): 摄像头索引
            weight_info (Optional[float]): 重量信息
            
        Returns:
            RecognitionResult: 识别结果
        """
        # 从摄像头捕获图像
        base64_image = self.image_processor.capture_from_camera(camera_index)
        
        if base64_image is None:
            return self._create_fallback_result("摄像头捕获失败", 0.0)
        
        # 将base64转换为numpy数组进行识别
        import io
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        return self.recognize_food(image_array, weight_info)
    
    def batch_recognize(
        self, 
        image_sources: List[Union[str, np.ndarray]],
        weight_info_list: Optional[List[float]] = None
    ) -> List[RecognitionResult]:
        """
        批量识别
        Batch recognition
        
        Args:
            image_sources (List[Union[str, np.ndarray]]): 图像源列表
            weight_info_list (Optional[List[float]]): 重量信息列表
            
        Returns:
            List[RecognitionResult]: 识别结果列表
        """
        results = []
        
        for i, image_source in enumerate(image_sources):
            weight_info = None
            if weight_info_list and i < len(weight_info_list):
                weight_info = weight_info_list[i]
            
            try:
                result = self.recognize_food(image_source, weight_info)
                results.append(result)
            except Exception as e:
                logging.error(f"批量识别第{i+1}项失败: {e}")
                fallback = self._create_fallback_result(str(e), 0.0)
                results.append(fallback)
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        Get statistics
        
        Returns:
            Dict: 统计信息
        """
        success_rate = 0.0
        if self.total_requests > 0:
            success_rate = self.successful_requests / self.total_requests
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'cache_size': len(self.response_cache),
            'model_name': ai_config.model_name
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.response_cache.clear()
        logging.info("识别结果缓存已清空")


# 异步版本的视觉AI类
class AsyncVisionAI(VisionAI):
    """
    异步视觉AI识别类
    Async Vision AI Recognition Class
    """
    
    async def recognize_food_async(
        self,
        image_source: Union[str, np.ndarray],
        weight_info: Optional[float] = None,
        context: Optional[str] = None
    ) -> RecognitionResult:
        """
        异步识别食物
        Async recognize food
        
        Args:
            image_source (Union[str, np.ndarray]): 图像源
            weight_info (Optional[float]): 重量信息
            context (Optional[str]): 上下文信息
            
        Returns:
            RecognitionResult: 识别结果
        """
        # 在线程池中运行同步识别方法
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self.recognize_food, 
            image_source, 
            weight_info, 
            context
        )
        return result
    
    async def batch_recognize_async(
        self, 
        image_sources: List[Union[str, np.ndarray]],
        weight_info_list: Optional[List[float]] = None
    ) -> List[RecognitionResult]:
        """
        异步批量识别
        Async batch recognition
        
        Args:
            image_sources (List[Union[str, np.ndarray]]): 图像源列表
            weight_info_list (Optional[List[float]]): 重量信息列表
            
        Returns:
            List[RecognitionResult]: 识别结果列表
        """
        # 创建异步任务
        tasks = []
        for i, image_source in enumerate(image_sources):
            weight_info = None
            if weight_info_list and i < len(weight_info_list):
                weight_info = weight_info_list[i]
            
            task = self.recognize_food_async(image_source, weight_info)
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"异步批量识别第{i+1}项失败: {result}")
                fallback = self._create_fallback_result(str(result), 0.0)
                processed_results.append(fallback)
            else:
                processed_results.append(result)
        
        return processed_results 