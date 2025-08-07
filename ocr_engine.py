#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR识别引擎模块
负责图片文字识别和语言处理
"""

import logging
import re
import shutil
import os
import sys
from typing import List, Dict, Optional, Tuple
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import OCRError, print_progress_bar
from config import config


class OCREngine:
    """OCR识别引擎类"""
    
    def __init__(self):
        """初始化OCR引擎"""
        self.logger = logging.getLogger("pdf_ocr.ocr_engine")
        self.language = config.ocr_language
        self.confidence_threshold = config.confidence_threshold
        
        # 设置Tesseract路径（支持打包环境）
        self._setup_tesseract_path()
        self._check_tesseract()
    
    def _setup_tesseract_path(self):
        """设置Tesseract路径，支持打包环境和Windows自动配置"""
        try:
            # 检查是否在PyInstaller打包环境中
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # 在打包环境中
                base_path = sys._MEIPASS
                tesseract_path = os.path.join(base_path, 'tesseract')
                tessdata_path = os.path.join(base_path, 'tessdata')
                
                # 设置Tesseract可执行文件路径
                if os.path.exists(tesseract_path):
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                    self.logger.info(f"使用打包的Tesseract: {tesseract_path}")
                
                # 设置tessdata路径
                if os.path.exists(tessdata_path):
                    os.environ['TESSDATA_PREFIX'] = tessdata_path
                    self.logger.info(f"使用打包的tessdata: {tessdata_path}")
            else:
                # 在开发环境中，尝试自动检测和配置Tesseract路径
                self._auto_configure_tesseract()
                    
        except Exception as e:
            self.logger.warning(f"设置Tesseract路径时出现警告: {e}")
    
    def _auto_configure_tesseract(self):
        """自动配置Tesseract路径（特别针对Windows）"""
        import platform
        
        # 首先尝试从PATH中找到tesseract
        tesseract_cmd = shutil.which('tesseract')
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            self.logger.info(f"检测到Tesseract: {tesseract_cmd}")
            
            # 尝试自动设置TESSDATA_PREFIX
            if platform.system() == "Windows":
                self._setup_windows_tessdata(tesseract_cmd)
        else:
            # 如果PATH中没有找到，尝试常见的安装路径
            if platform.system() == "Windows":
                self._find_windows_tesseract()
    
    def _setup_windows_tessdata(self, tesseract_cmd):
        """为Windows设置TESSDATA_PREFIX环境变量"""
        try:
            # 从tesseract.exe路径推断tessdata路径
            tesseract_dir = os.path.dirname(tesseract_cmd)
            tessdata_path = os.path.join(tesseract_dir, 'tessdata')
            
            if os.path.exists(tessdata_path):
                os.environ['TESSDATA_PREFIX'] = tessdata_path
                self.logger.info(f"自动设置TESSDATA_PREFIX: {tessdata_path}")
            else:
                # 尝试其他可能的tessdata位置
                possible_paths = [
                    os.path.join(os.path.dirname(tesseract_dir), 'tessdata'),
                    os.path.join(tesseract_dir, '..', 'tessdata'),
                    r'C:\Program Files\Tesseract-OCR\tessdata',
                    r'C:\Program Files (x86)\Tesseract-OCR\tessdata'
                ]
                
                for path in possible_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        os.environ['TESSDATA_PREFIX'] = abs_path
                        self.logger.info(f"找到tessdata目录: {abs_path}")
                        break
                else:
                    self.logger.warning("无法找到tessdata目录，可能需要手动设置TESSDATA_PREFIX环境变量")
                    
        except Exception as e:
            self.logger.warning(f"设置Windows tessdata路径失败: {e}")
    
    def _find_windows_tesseract(self):
        """在Windows上查找Tesseract安装"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\software\Tesseract-OCR\tesseract.exe',
            r'C:\tools\Tesseract-OCR\tesseract.exe'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                self.logger.info(f"找到Tesseract安装: {path}")
                
                # 设置对应的tessdata路径
                tesseract_dir = os.path.dirname(path)
                tessdata_path = os.path.join(tesseract_dir, 'tessdata')
                if os.path.exists(tessdata_path):
                    os.environ['TESSDATA_PREFIX'] = tessdata_path
                    self.logger.info(f"设置tessdata路径: {tessdata_path}")
                break
        else:
            self.logger.warning("未找到Tesseract安装，请确保已正确安装Tesseract OCR")
    
    def _check_tesseract(self):
        """检查Tesseract是否可用"""
        # 检查tesseract命令是否存在
        if not shutil.which('tesseract'):
            error_msg = (
                "Tesseract OCR 未安装或未添加到 PATH\n"
                "请安装 Tesseract OCR:\n"
                "  macOS: brew install tesseract tesseract-lang\n"
                "  Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim\n"
                "  Windows: 下载并安装 https://github.com/UB-Mannheim/tesseract/wiki"
            )
            self.logger.error(error_msg)
            raise OCRError(error_msg)
        
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract版本: {version}")
            
            # 检查基本语言包
            available_langs = self.get_available_languages()
            if not available_langs or 'eng' not in available_langs:
                self.logger.warning("英文语言包缺失，OCR功能可能受限")
                
        except Exception as e:
            error_msg = (
                f"Tesseract OCR 配置错误: {e}\n"
                "请检查 Tesseract 安装是否正确，并确保已添加到系统 PATH"
            )
            self.logger.error(error_msg)
            raise OCRError(error_msg)
    
    def get_available_languages(self) -> List[str]:
        """获取可用的OCR语言
        
        Returns:
            可用语言列表
        """
        try:
            languages = pytesseract.get_languages()
            self.logger.info(f"可用OCR语言: {languages}")
            return languages
        except Exception as e:
            self.logger.error(f"获取语言列表失败: {e}")
            return []
    
    def validate_language(self, language: str) -> bool:
        """验证语言是否可用
        
        Args:
            language: 语言代码
            
        Returns:
            语言是否可用
        """
        available_langs = self.get_available_languages()
        
        # 处理组合语言（如 chi_sim+eng）
        if '+' in language:
            langs = language.split('+')
            return all(lang in available_langs for lang in langs)
        
        return language in available_langs
    
    def extract_text_from_image(self, image: Image.Image, 
                              language: str = None) -> Dict[str, any]:
        """从图片中提取文字
        
        Args:
            image: PIL图片对象
            language: OCR识别语言
            
        Returns:
            包含文字内容和置信度的字典
        """
        if language is None:
            language = self.language
        
        if not self.validate_language(language):
            self.logger.warning(f"语言 {language} 不可用，使用默认语言")
            # 尝试分解组合语言，保留可用的部分
            if '+' in language:
                available_langs = self.get_available_languages()
                valid_langs = [lang for lang in language.split('+') if lang in available_langs]
                if valid_langs:
                    language = '+'.join(valid_langs)
                    self.logger.info(f"使用可用语言: {language}")
                else:
                    language = 'eng'  # 最后回退到英语
            else:
                language = 'eng'  # 回退到英语
        
        try:
            # 配置OCR参数 - 移除字符白名单限制以支持更好的中文识别
            if 'chi' in language.lower():
                # 中文模式：使用更宽松的配置
                custom_config = r'--oem 3 --psm 6'
            else:
                # 其他语言：保持原有配置
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            
            # 提取文字
            text = pytesseract.image_to_string(
                image, 
                lang=language,
                config=custom_config
            )
            
            # 获取详细信息（包含置信度）
            data = pytesseract.image_to_data(
                image, 
                lang=language,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # 计算平均置信度
            confidences = [int(conf) for conf in data['conf'] if int(conf) > -1]  # 包含0置信度
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # 如果置信度过低，记录调试信息
            if avg_confidence < 50:
                self.logger.warning(f"OCR置信度较低: {avg_confidence:.1f}%, 语言: {language}")
                self.logger.debug(f"原始文本: {text[:100]}...")
            
            # 清理文本
            cleaned_text = self._clean_text(text)
            
            result = {
                'text': cleaned_text,
                'raw_text': text,
                'confidence': round(avg_confidence, 2),
                'language': language,
                'word_count': len(cleaned_text.split()),
                'char_count': len(cleaned_text)
            }
            
            self.logger.debug(f"OCR结果: 置信度={avg_confidence:.1f}%, 字符数={len(cleaned_text)}")
            return result
            
        except Exception as e:
            error_msg = f"OCR识别失败: {e}"
            self.logger.error(error_msg)
            raise OCRError(error_msg)
    
    def _clean_text(self, text: str) -> str:
        """清理OCR识别的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除行首行尾空白
        text = text.strip()
        
        # 处理常见的OCR错误
        # 这里可以添加更多的文本清理规则
        replacements = {
            '|': 'l',  # 竖线误识别为l
            '0': 'O',  # 在某些上下文中
            # 可以根据需要添加更多替换规则
        }
        
        # 应用替换（谨慎使用，可能影响正确文本）
        # for old, new in replacements.items():
        #     text = text.replace(old, new)
        
        return text
    
    def batch_extract_text(self, images: List[Image.Image], 
                         language: str = None, 
                         show_progress: bool = True) -> List[Dict[str, any]]:
        """批量提取文字
        
        Args:
            images: PIL图片对象列表
            language: OCR识别语言
            show_progress: 是否显示进度
            
        Returns:
            OCR结果列表
        """
        if not images:
            return []
        
        results = []
        total_images = len(images)
        
        self.logger.info(f"开始批量OCR识别，共 {total_images} 张图片")
        
        # 使用线程池并行处理
        max_workers = min(config.max_workers, total_images)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_index = {
                executor.submit(self.extract_text_from_image, img, language): i 
                for i, img in enumerate(images)
            }
            
            # 收集结果
            completed = 0
            results = [None] * total_images  # 预分配结果列表
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                completed += 1
                
                try:
                    result = future.result()
                    result['page_number'] = index + 1
                    results[index] = result
                    
                    if show_progress:
                        print_progress_bar(completed, total_images, "OCR识别")
                        
                except Exception as e:
                    self.logger.error(f"页面 {index + 1} OCR失败: {e}")
                    results[index] = {
                        'text': '',
                        'raw_text': '',
                        'confidence': 0,
                        'language': language or self.language,
                        'word_count': 0,
                        'char_count': 0,
                        'page_number': index + 1,
                        'error': str(e)
                    }
        
        # 过滤掉None值（如果有的话）
        results = [r for r in results if r is not None]
        
        self.logger.info(f"批量OCR完成，成功处理 {len(results)} 页")
        return results
    
    def extract_text_with_layout(self, image: Image.Image, 
                               language: str = None) -> Dict[str, any]:
        """提取文字并保持布局信息
        
        Args:
            image: PIL图片对象
            language: OCR识别语言
            
        Returns:
            包含布局信息的OCR结果
        """
        if language is None:
            language = self.language
        
        try:
            # 获取详细的OCR数据
            data = pytesseract.image_to_data(
                image, 
                lang=language,
                output_type=pytesseract.Output.DICT
            )
            
            # 组织文本块
            text_blocks = []
            current_block = []
            current_line = data['line_num'][0] if data['line_num'] else 0
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > self.confidence_threshold:
                    word_info = {
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'line_num': data['line_num'][i],
                        'block_num': data['block_num'][i]
                    }
                    
                    if data['line_num'][i] != current_line:
                        if current_block:
                            text_blocks.append(current_block)
                        current_block = [word_info]
                        current_line = data['line_num'][i]
                    else:
                        current_block.append(word_info)
            
            if current_block:
                text_blocks.append(current_block)
            
            # 重建文本
            formatted_text = self._rebuild_text_from_blocks(text_blocks)
            
            return {
                'text': formatted_text,
                'text_blocks': text_blocks,
                'language': language,
                'total_blocks': len(text_blocks)
            }
            
        except Exception as e:
            error_msg = f"布局OCR识别失败: {e}"
            self.logger.error(error_msg)
            raise OCRError(error_msg)
    
    def _rebuild_text_from_blocks(self, text_blocks: List[List[Dict]]) -> str:
        """从文本块重建文本
        
        Args:
            text_blocks: 文本块列表
            
        Returns:
            重建的文本
        """
        lines = []
        
        for block in text_blocks:
            if not block:
                continue
            
            # 按水平位置排序单词
            block.sort(key=lambda x: x['left'])
            
            # 组合单词为行
            line_text = ' '.join(word['text'] for word in block if word['text'].strip())
            if line_text.strip():
                lines.append(line_text)
        
        return '\n'.join(lines)
    
    def get_ocr_statistics(self, results: List[Dict[str, any]]) -> Dict[str, any]:
        """获取OCR统计信息
        
        Args:
            results: OCR结果列表
            
        Returns:
            统计信息字典
        """
        if not results:
            return {}
        
        total_pages = len(results)
        total_chars = sum(r.get('char_count', 0) for r in results)
        total_words = sum(r.get('word_count', 0) for r in results)
        avg_confidence = sum(r.get('confidence', 0) for r in results) / total_pages
        
        # 统计低置信度页面
        low_confidence_pages = [
            r.get('page_number', i+1) 
            for i, r in enumerate(results) 
            if r.get('confidence', 0) < self.confidence_threshold
        ]
        
        # 统计错误页面
        error_pages = [
            r.get('page_number', i+1) 
            for i, r in enumerate(results) 
            if 'error' in r
        ]
        
        return {
            'total_pages': total_pages,
            'total_characters': total_chars,
            'total_words': total_words,
            'average_confidence': round(avg_confidence, 2),
            'low_confidence_pages': low_confidence_pages,
            'error_pages': error_pages,
            'success_rate': round((total_pages - len(error_pages)) / total_pages * 100, 2)
        }