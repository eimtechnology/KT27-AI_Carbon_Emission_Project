# -*- coding: utf-8 -*-
"""
Food Carbon Emission Detection System - System Configuration

Contains all system parameters and configuration items for the carbon emission detection system.
This module provides centralized configuration management for hardware, AI, and system settings.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

# Google API Configuration
GOOGLE_API_KEY = "AIzaSyBO0Uhx-PVnwpZS-972J73XS6xnzl01qvs"

@dataclass
class HardwareConfig:
    """Hardware Configuration Class"""
    
    # UART Communication Configuration
    uart_port: str = "COM3"  # Windows: COM3, Linux: /dev/ttyUSB0, macOS: /dev/tty.usbserial
    uart_baudrate: int = 115200
    uart_timeout: float = 1.0
    
    # Camera Configuration
    camera_index: int = 0
    image_width: int = 640
    image_height: int = 480
    image_quality: int = 95
    
    # Weight Sensor Configuration
    weight_stable_threshold: float = 5.0  # grams
    weight_stable_count: int = 5
    weight_max_capacity: float = 5000.0  # 5kg
    
    # System Timer Configuration
    update_interval_ms: int = 100  # 100ms
    data_send_interval_s: float = 1.0  # 1 second


@dataclass
class AIConfig:
    """AI Configuration Class"""
    
    # Gemini API Configuration
    model_name: str = "models/gemini-2.0-flash-exp"
    api_key: str = GOOGLE_API_KEY
    max_retries: int = 3
    retry_delay: float = 1.0
    request_timeout: float = 30.0
    
    # Image Processing Configuration
    image_resize_width: int = 800
    image_resize_height: int = 600
    image_format: str = "JPEG"
    
    # Recognition Parameters
    confidence_threshold: float = 0.7
    enable_local_fallback: bool = True


@dataclass
class CarbonCalculationConfig:
    """Carbon Calculation Configuration Class"""
    
    # Calculation Precision
    calculation_precision: int = 2
    
    # Default Emission Factor (kg CO2 per kg)
    default_emission_factor: float = 2.5
    
    # Unit Conversions
    units: Dict[str, float] = None
    
    def __post_init__(self):
        if self.units is None:
            self.units = {
                'kg': 1.0,
                'g': 0.001,
                'lb': 0.453592,
                'oz': 0.0283495
            }


@dataclass
class SystemConfig:
    """System Configuration Class"""
    
    # System Information
    system_name: str = "Food Carbon Emission Detection System"
    version: str = "1.0.0"
    debug_mode: bool = True
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/system.log"
    log_max_size: int = 10  # MB
    log_backup_count: int = 5
    
    # Data Storage Configuration
    database_file: str = "data/carbon_detection.db"
    backup_interval_hours: int = 24
    data_retention_days: int = 90
    
    # Language Configuration
    default_language: str = "en_US"
    supported_languages: List[str] = None
    
    # Performance Configuration
    max_concurrent_detections: int = 1
    detection_timeout_s: float = 30.0
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["en_US", "zh_CN"]


# Global Configuration Instances
hardware_config = HardwareConfig()
ai_config = AIConfig()
carbon_config = CarbonCalculationConfig()
system_config = SystemConfig()


def get_config_dict() -> Dict:
    """Get all configuration as a dictionary"""
    return {
        'hardware': hardware_config.__dict__,
        'ai': ai_config.__dict__,
        'carbon': carbon_config.__dict__,
        'system': system_config.__dict__
    }


def load_config_from_file(config_file: str) -> bool:
    """Load configuration from JSON file"""
    try:
        import json
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Update configuration instances
            if 'hardware' in config_data:
                for key, value in config_data['hardware'].items():
                    if hasattr(hardware_config, key):
                        setattr(hardware_config, key, value)
                        
            if 'ai' in config_data:
                for key, value in config_data['ai'].items():
                    if hasattr(ai_config, key):
                        setattr(ai_config, key, value)
                        
            if 'carbon' in config_data:
                for key, value in config_data['carbon'].items():
                    if hasattr(carbon_config, key):
                        setattr(carbon_config, key, value)
                        
            if 'system' in config_data:
                for key, value in config_data['system'].items():
                    if hasattr(system_config, key):
                        setattr(system_config, key, value)
                        
            print(f"Configuration loaded from {config_file}")
            return True
        else:
            print(f"Configuration file {config_file} not found")
            return False
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False


def save_config_to_file(config_file: str) -> bool:
    """Save current configuration to JSON file"""
    try:
        import json
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        config_data = get_config_dict()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        print(f"Configuration saved to {config_file}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def load_env_config():
    """Load configuration from environment variables"""
    # Hardware configuration
    if os.getenv('UART_PORT'):
        hardware_config.uart_port = os.getenv('UART_PORT')
    if os.getenv('UART_BAUDRATE'):
        hardware_config.uart_baudrate = int(os.getenv('UART_BAUDRATE'))
    if os.getenv('CAMERA_INDEX'):
        hardware_config.camera_index = int(os.getenv('CAMERA_INDEX'))
        
    # AI configuration
    if os.getenv('GOOGLE_API_KEY'):
        ai_config.api_key = os.getenv('GOOGLE_API_KEY')
    if os.getenv('AI_MODEL_NAME'):
        ai_config.model_name = os.getenv('AI_MODEL_NAME')
        
    # System configuration
    if os.getenv('DEBUG_MODE'):
        system_config.debug_mode = os.getenv('DEBUG_MODE').lower() == 'true'
    if os.getenv('LOG_LEVEL'):
        system_config.log_level = os.getenv('LOG_LEVEL')
    if os.getenv('DEFAULT_LANGUAGE'):
        system_config.default_language = os.getenv('DEFAULT_LANGUAGE')


# Load environment configuration on import
load_env_config() 