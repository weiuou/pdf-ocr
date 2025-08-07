#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
用于管理OCR工具的各种配置参数
"""

import json
import os
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        """初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "ocr": {
                "language": "chi_sim+eng",
                "dpi": 300,
                "confidence_threshold": 60
            },
            "output": {
                "format": "txt",
                "preserve_formatting": True,
                "output_directory": "./output"
            },
            "processing": {
                "max_workers": 4,
                "temp_directory": "./temp",
                "cleanup_temp": True
            }
        }
    
    def _load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告: 配置文件加载失败，使用默认配置: {e}")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """合并配置
        
        Args:
            file_config: 文件中的配置
        """
        for section, values in file_config.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"错误: 配置文件保存失败: {e}")
    
    def get(self, section: str, key: str = None, default=None):
        """获取配置值
        
        Args:
            section: 配置段名
            key: 配置键名，如果为None则返回整个段
            default: 默认值
            
        Returns:
            配置值
        """
        if section not in self.config:
            return default
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """设置配置值
        
        Args:
            section: 配置段名
            key: 配置键名
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    @property
    def ocr_language(self) -> str:
        """OCR识别语言"""
        return self.get("ocr", "language", "chi_sim+eng")
    
    @property
    def ocr_dpi(self) -> int:
        """OCR图片DPI"""
        return self.get("ocr", "dpi", 300)
    
    @property
    def confidence_threshold(self) -> int:
        """置信度阈值"""
        return self.get("ocr", "confidence_threshold", 60)
    
    @property
    def output_format(self) -> str:
        """输出格式"""
        return self.get("output", "format", "txt")
    
    @property
    def output_directory(self) -> str:
        """输出目录"""
        return self.get("output", "output_directory", "./output")
    
    @property
    def preserve_formatting(self) -> bool:
        """是否保持格式"""
        return self.get("output", "preserve_formatting", True)
    
    @property
    def max_workers(self) -> int:
        """最大工作线程数"""
        return self.get("processing", "max_workers", 4)
    
    @property
    def temp_directory(self) -> str:
        """临时目录"""
        return self.get("processing", "temp_directory", "./temp")
    
    @property
    def cleanup_temp(self) -> bool:
        """是否清理临时文件"""
        return self.get("processing", "cleanup_temp", True)


# 全局配置实例
config = Config()