# -*- coding: utf-8 -*-
"""
Food Carbon Emission Detection System - AI Vision Recognition Module

Food recognition system based on Google Gemini Pro Vision API

Features:
- Intelligent food recognition and classification
- Multi-modal analysis (Image + Weight)
- Food quality and freshness assessment
- Intelligent prompt optimization
- Batch recognition and analysis
- Confidence evaluation and verification
"""

import os
import time
import base64
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
from datetime import datetime

# Import configuration
try:
    from config.system_config import ai_config
except ImportError:
    # Fallback config if module is missing
    class AIConfig:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        model_name = "gemini-pro-vision"
        image_resize_width = 800
        image_resize_height = 600
        max_retries = 3
        retry_delay = 1
        confidence_threshold = 0.6
    ai_config = AIConfig()

@dataclass
class RecognitionResult:
    """
    Recognition Result Data Class
    """
    food_name: str                    # Food Name
    confidence: float                 # Confidence (0-1)
    category: str                     # Food Category
    description: str                  # Detailed Description
    estimated_weight: Optional[float] # Estimated Weight (g)
    freshness: Optional[str]          # Freshness
    quality: Optional[str]            # Quality Assessment
    ingredients: List[str]            # Ingredients List
    nutritional_info: Dict            # Nutritional Info
    processing_time: float            # Processing Time (s)
    api_response: str                 # Raw API Response
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
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
    Image Preprocessor
    """
    
    def __init__(self):
        """Initialize image processor"""
        self.target_size = (ai_config.image_resize_width, ai_config.image_resize_height)
        self.quality = 95
        
    def preprocess_image(self, image_path: str) -> str:
        """
        Preprocess image and convert to Base64
        
        Args:
            image_path (str): Image file path
            
        Returns:
            str: Base64 encoded image data
        """
        try:
            # Read image
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                # Assume numpy array
                image = Image.fromarray(image_path)
            
            # Image enhancement
            enhanced_image = self._enhance_image(image)
            
            # Resize
            resized_image = self._resize_image(enhanced_image)
            
            # Convert to Base64
            base64_data = self._image_to_base64(resized_image)
            
            return base64_data
            
        except Exception as e:
            logging.error(f"Image preprocessing failed: {e}")
            raise
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance image quality
        
        Args:
            image (Image.Image): Original image
            
        Returns:
            Image.Image: Enhanced image
        """
        # Brightness enhancement
        brightness_enhancer = ImageEnhance.Brightness(image)
        enhanced = brightness_enhancer.enhance(1.1)
        
        # Contrast enhancement
        contrast_enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = contrast_enhancer.enhance(1.1)
        
        # Sharpness
        sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = sharpness_enhancer.enhance(1.05)
        
        # Color enhancement
        color_enhancer = ImageEnhance.Color(enhanced)
        enhanced = color_enhancer.enhance(1.05)
        
        return enhanced
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image
        
        Args:
            image (Image.Image): Original image
            
        Returns:
            Image.Image: Resized image
        """
        # Maintain aspect ratio
        image.thumbnail(self.target_size, Image.Resampling.LANCZOS)
        
        # Create white background
        background = Image.new('RGB', self.target_size, (255, 255, 255))
        
        # Center image
        offset = ((self.target_size[0] - image.size[0]) // 2,
                 (self.target_size[1] - image.size[1]) // 2)
        background.paste(image, offset)
        
        return background
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convert image to Base64 encoding
        
        Args:
            image (Image.Image): Image object
            
        Returns:
            str: Base64 encoded string
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
        Capture image from camera
        
        Args:
            camera_index (int): Camera index
            
        Returns:
            Optional[str]: Base64 encoded image data
        """
        try:
            # Initialize camera
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                logging.error("Cannot open camera")
                return None
            
            # Set camera parameters
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Warmup camera
            for _ in range(5):
                cap.read()
            
            # Capture image
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logging.error("Cannot capture image")
                return None
            
            # Convert color space
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL image and process
            pil_image = Image.fromarray(frame_rgb)
            enhanced_image = self._enhance_image(pil_image)
            resized_image = self._resize_image(enhanced_image)
            
            return self._image_to_base64(resized_image)
            
        except Exception as e:
            logging.error(f"Camera capture failed: {e}")
            return None


class PromptGenerator:
    """
    Intelligent Prompt Generator
    """
    
    def __init__(self):
        """Initialize prompt generator"""
        self.base_prompt = """
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
            "description": "brief description",
            "estimated_weight": 150.0,
            "freshness": "Fresh/Average/Stale",
            "quality": "Premium/Good/Average",
            "ingredients": ["ingredient1", "ingredient2"]
        }

        EXAMPLES:
        - Red apple → "Apple"
        - Grilled chicken breast → "Chicken" 
        - White rice → "Rice"
        - Cheddar cheese → "Cheese"
        - Fresh salmon → "Salmon"

        Focus on accuracy and use the most common English name for the food.
        """
    
    def generate_prompt(
        self, 
        weight_info: Optional[float] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate intelligent prompt
        
        Args:
            weight_info (Optional[float]): Weight info (g)
            context (Optional[str]): Context info
            
        Returns:
            str: Generated prompt
        """
        prompt = self.base_prompt
        
        # Add weight info
        if weight_info is not None:
            weight_hint = f"\n\nKnown weight information: {weight_info:.1f}g, please analyze considering this information."
            prompt += weight_hint
        
        # Add context info
        if context:
            context_hint = f"\n\nContext information: {context}"
            prompt += context_hint
        
        # Add special instructions
        prompt += """
        
        Special instructions:
        - If there are multiple foods in the image, identify the main food item
        - If specific food cannot be determined, provide the most likely category
        - Confidence should realistically reflect recognition accuracy
        - Weight estimation should be reasonable, considering food density and volume
        """
        
        return prompt


class VisionAI:
    """
    Vision AI Recognition Main Class
    """
    
    def __init__(self):
        """Initialize Vision AI System"""
        self.image_processor = ImageProcessor()
        self.prompt_generator = PromptGenerator()
        
        # Configure Gemini API
        self._configure_gemini()
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Cache
        self.response_cache = {}
        self.cache_max_size = 100
        
        logging.info("Vision AI System Initialized")
    
    def _configure_gemini(self):
        """Configure Gemini API"""
        try:
            genai.configure(api_key=ai_config.api_key)
            
            # Safety settings
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Generation config
            self.generation_config = {
                "temperature": 0.1,  # Reduce randomness
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name=ai_config.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            logging.info(f"Gemini Model Configured: {ai_config.model_name}")
            
        except Exception as e:
            logging.error(f"Gemini API Configuration Failed: {e}")
            # Don't raise here to allow fallback/mock mode usage if desired by caller
            # But for now we'll log it.
            # Note: The caller (gui_main.py) handles exceptions during usage.
    
    def recognize_food(
        self,
        image_source: Union[str, np.ndarray],
        weight_info: Optional[float] = None,
        context: Optional[str] = None
    ) -> RecognitionResult:
        """
        Recognize food
        
        Args:
            image_source (Union[str, np.ndarray]): Image source (path or numpy array)
            weight_info (Optional[float]): Weight info (g)
            context (Optional[str]): Context info
            
        Returns:
            RecognitionResult: Recognition result
        """
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Preprocess image
            if isinstance(image_source, str):
                base64_image = self.image_processor.preprocess_image(image_source)
            else:
                # numpy array
                pil_image = Image.fromarray(image_source)
                enhanced = self.image_processor._enhance_image(pil_image)
                resized = self.image_processor._resize_image(enhanced)
                base64_image = self.image_processor._image_to_base64(resized)
            
            # Generate cache key
            cache_key = self._generate_cache_key(base64_image, weight_info, context)
            
            # Check cache
            if cache_key in self.response_cache:
                logging.info("Using cached recognition result")
                cached_result = self.response_cache[cache_key]
                cached_result.processing_time = time.time() - start_time
                return cached_result
            
            # Generate prompt
            prompt = self.prompt_generator.generate_prompt(weight_info, context)
            
            # Call API
            result = self._call_gemini_api(base64_image, prompt)
            
            # Parse response
            recognition_result = self._parse_response(result, time.time() - start_time)
            
            # Post-process
            recognition_result = self._post_process_result(recognition_result, weight_info)
            
            # Cache result
            self._cache_result(cache_key, recognition_result)
            
            self.successful_requests += 1
            logging.info(f"Food recognized successfully: {recognition_result.food_name}")
            
            return recognition_result
            
        except Exception as e:
            self.failed_requests += 1
            logging.error(f"Food recognition failed: {e}")
            
            # Return fallback result
            return self._create_fallback_result(str(e), time.time() - start_time)
    
    def _call_gemini_api(self, base64_image: str, prompt: str) -> str:
        """
        Call Gemini API
        
        Args:
            base64_image (str): Base64 encoded image
            prompt (str): Prompt
            
        Returns:
            str: API response
        """
        # Ensure model is initialized
        if not hasattr(self, 'model'):
            raise Exception("Gemini model not initialized")

        max_retries = ai_config.max_retries
        retry_delay = ai_config.retry_delay
        
        for attempt in range(max_retries):
            try:
                # Prepare image data
                image_parts = [
                    {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                ]
                
                # Send request
                response = self.model.generate_content(
                    [prompt] + image_parts,
                    safety_settings=self.safety_settings,
                    generation_config=self.generation_config
                )
                
                if response.text:
                    return response.text
                else:
                    raise Exception("API returned empty response")
                    
            except Exception as e:
                logging.warning(f"API call failed (Attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise Exception(f"API call failed after {max_retries} attempts: {e}")
    
    def _parse_response(self, response_text: str, processing_time: float) -> RecognitionResult:
        """
        Parse API response
        
        Args:
            response_text (str): API response text
            processing_time (float): Processing time
            
        Returns:
            RecognitionResult: Parsed result
        """
        try:
            # Try to extract JSON
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)
            
            # Parse fields
            food_name = data.get('food_name', 'Unknown Food')
            confidence = float(data.get('confidence', 0.5))
            category = data.get('category', 'Unknown')
            description = data.get('description', '')
            
            # Weight info
            estimated_weight = data.get('estimated_weight')
            if isinstance(estimated_weight, str):
                # Try to extract number from string
                import re
                numbers = re.findall(r'\d+\.?\d*', estimated_weight)
                estimated_weight = float(numbers[0]) if numbers else None
            
            # Quality assessment
            freshness = data.get('freshness')
            quality = data.get('quality')
            
            # Ingredients and nutritional info
            ingredients = data.get('ingredients', [])
            if isinstance(ingredients, str):
                ingredients = [ing.strip() for ing in ingredients.split(',')]
            
            nutritional_info = data.get('nutritional_info', {})
            if isinstance(nutritional_info, str):
                nutritional_info = {'description': nutritional_info}
            
            return RecognitionResult(
                food_name=food_name,
                confidence=max(0.0, min(1.0, confidence)),  # Limit to 0-1
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
            logging.error(f"Response parsing failed: {e}")
            logging.debug(f"Raw response: {response_text}")
            
            # Fallback to text parsing
            return self._fallback_text_parse(response_text, processing_time)
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text
        
        Args:
            text (str): Text containing JSON
            
        Returns:
            str: Extracted JSON string
        """
        import re
        
        # Try matching ```json ... ``` format
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Try matching {...} format
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If not found, return original text
        return text
    
    def _fallback_text_parse(self, text: str, processing_time: float) -> RecognitionResult:
        """
        Fallback text parsing
        
        Args:
            text (str): Response text
            processing_time (float): Processing time
            
        Returns:
            RecognitionResult: Recognition result
        """
        # Simple text parsing logic
        lines = text.split('\n')
        
        food_name = "Unknown Food"
        confidence = 0.5
        category = "Unknown"
        description = text[:200]  # First 200 chars as description
        
        # Try to extract info from text
        for line in lines:
            line = line.strip()
            if 'name' in line.lower():
                parts = line.split(':')
                if len(parts) > 1:
                    food_name = parts[1].strip()
            elif 'category' in line.lower():
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
        Post-process recognition result
        
        Args:
            result (RecognitionResult): Original result
            weight_info (Optional[float]): Actual weight info
            
        Returns:
            RecognitionResult: Post-processed result
        """
        # If actual weight info exists, verify and adjust
        if weight_info is not None and result.estimated_weight is not None:
            weight_diff = abs(result.estimated_weight - weight_info)
            weight_ratio = weight_diff / max(weight_info, 1.0)
            
            # If weight difference is large, lower confidence
            if weight_ratio > 0.5:  # Diff > 50%
                result.confidence *= 0.7
            elif weight_ratio > 0.3:  # Diff > 30%
                result.confidence *= 0.9
            
            # Update estimated weight to actual weight
            result.estimated_weight = weight_info
        
        # Confidence verification
        if result.confidence < ai_config.confidence_threshold:
            logging.warning(f"Low recognition confidence: {result.confidence:.2f}")
        
        return result
    
    def _create_fallback_result(self, error_msg: str, processing_time: float) -> RecognitionResult:
        """
        Create fallback recognition result
        
        Args:
            error_msg (str): Error message
            processing_time (float): Processing time
            
        Returns:
            RecognitionResult: Fallback result
        """
        return RecognitionResult(
            food_name="Recognition Failed",
            confidence=0.0,
            category="Unknown",
            description=f"Error during recognition: {error_msg}",
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
        Generate cache key
        
        Args:
            base64_image (str): Base64 image data
            weight_info (Optional[float]): Weight info
            context (Optional[str]): Context
            
        Returns:
            str: Cache key
        """
        import hashlib
        
        # Calculate image hash
        image_hash = hashlib.md5(base64_image.encode()).hexdigest()[:16]
        
        # Combine other info
        key_parts = [image_hash]
        if weight_info is not None:
            key_parts.append(f"w{weight_info:.1f}")
        if context:
            key_parts.append(hashlib.md5(context.encode()).hexdigest()[:8])
        
        return "_".join(key_parts)
    
    def _cache_result(self, cache_key: str, result: RecognitionResult):
        """
        Cache recognition result
        
        Args:
            cache_key (str): Cache key
            result (RecognitionResult): Result
        """
        # Limit cache size
        if len(self.response_cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        
        self.response_cache[cache_key] = result
    
    def detect_food(self, image_source):
        """Wrapper for recognize_food to match GUI expected interface"""
        result = self.recognize_food(image_source)
        # Convert to dict format expected by GUI
        return {
            'ai_detected': result.food_name,
            'standard_name': result.food_name,
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'timestamp': datetime.now()
        }
