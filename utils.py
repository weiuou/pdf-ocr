#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供文件操作、错误处理等通用功能
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, List


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """设置日志记录
    
    Args:
        log_level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger("pdf_ocr")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def validate_file_path(file_path: str, extensions: Optional[List[str]] = None) -> bool:
    """验证文件路径
    
    Args:
        file_path: 文件路径
        extensions: 允许的文件扩展名列表
        
    Returns:
        文件是否有效
    """
    if not file_path or not os.path.exists(file_path):
        return False
    
    if not os.path.isfile(file_path):
        return False
    
    if extensions:
        file_ext = Path(file_path).suffix.lower()
        return file_ext in [ext.lower() for ext in extensions]
    
    return True


def ensure_directory(directory: str) -> bool:
    """确保目录存在
    
    Args:
        directory: 目录路径
        
    Returns:
        目录是否创建成功
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logging.error(f"创建目录失败: {directory}, 错误: {e}")
        return False


def cleanup_directory(directory: str, keep_directory: bool = True) -> bool:
    """清理目录
    
    Args:
        directory: 要清理的目录
        keep_directory: 是否保留目录本身
        
    Returns:
        清理是否成功
    """
    try:
        if os.path.exists(directory):
            if keep_directory:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            else:
                shutil.rmtree(directory)
        return True
    except OSError as e:
        logging.error(f"清理目录失败: {directory}, 错误: {e}")
        return False


def get_file_size(file_path: str) -> str:
    """获取文件大小的可读格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        格式化的文件大小字符串
    """
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except OSError:
        return "未知大小"


def generate_output_filename(input_path: str, output_dir: str, 
                           output_format: str = "txt") -> str:
    """生成输出文件名
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        output_format: 输出格式
        
    Returns:
        输出文件的完整路径
    """
    input_name = Path(input_path).stem
    output_filename = f"{input_name}_ocr.{output_format}"
    return os.path.join(output_dir, output_filename)


def safe_filename(filename: str) -> str:
    """生成安全的文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    # 移除或替换不安全的字符
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # 限制文件名长度
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
    
    return safe_name


def format_time(seconds: float) -> str:
    """格式化时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def print_progress_bar(current: int, total: int, prefix: str = "进度", 
                      suffix: str = "完成", length: int = 50) -> None:
    """打印进度条
    
    Args:
        current: 当前进度
        total: 总数
        prefix: 前缀文本
        suffix: 后缀文本
        length: 进度条长度
    """
    percent = (current / total) * 100
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {current}/{total} ({percent:.1f}%) {suffix}', end='\r')
    
    if current == total:
        print()  # 换行


class OCRError(Exception):
    """OCR处理异常"""
    pass


class FileProcessError(Exception):
    """文件处理异常"""
    pass


class ConfigError(Exception):
    """配置异常"""
    pass