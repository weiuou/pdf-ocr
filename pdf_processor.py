#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF处理模块
负责PDF文件的读取、页面提取和图片转换
"""

import os
import logging
import subprocess
import shutil
from typing import List, Optional, Tuple
from PIL import Image
from pdf2image import convert_from_path
from utils import validate_file_path, ensure_directory, FileProcessError
from config import config


class PDFProcessor:
    """PDF处理器类"""
    
    def __init__(self):
        """初始化PDF处理器"""
        self.logger = logging.getLogger("pdf_ocr.pdf_processor")
        self.temp_dir = config.temp_directory
        ensure_directory(self.temp_dir)
        
        # 检查依赖
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查必要的系统依赖"""
        missing_deps = []
        
        # 检查 poppler 工具
        poppler_tools = ['pdfinfo', 'pdftoppm']
        for tool in poppler_tools:
            if not shutil.which(tool):
                missing_deps.append(f"poppler ({tool})")
        
        if missing_deps:
            error_msg = (
                f"缺少必要的系统依赖: {', '.join(missing_deps)}\n"
                "请安装 poppler-utils:\n"
                "  macOS: brew install poppler 或 conda install -c conda-forge poppler\n"
                "  Ubuntu: sudo apt-get install poppler-utils\n"
                "  Windows: 下载并安装 poppler，确保添加到 PATH"
            )
            self.logger.error(error_msg)
            raise FileProcessError(error_msg)
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """验证PDF文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            PDF文件是否有效
        """
        if not validate_file_path(pdf_path, ['.pdf']):
            self.logger.error(f"无效的PDF文件: {pdf_path}")
            return False
        
        try:
            # 尝试读取PDF的第一页来验证文件完整性
            convert_from_path(pdf_path, first_page=1, last_page=1)
            return True
        except Exception as e:
            error_str = str(e)
            if "poppler" in error_str.lower() or "unable to get page count" in error_str.lower():
                self.logger.error(
                    f"PDF处理失败，poppler依赖缺失: {pdf_path}\n"
                    "请安装 poppler-utils:\n"
                    "  macOS: brew install poppler 或 conda install -c conda-forge poppler\n"
                    "  Ubuntu: sudo apt-get install poppler-utils"
                )
            elif "encrypted" in error_str.lower() or "password" in error_str.lower():
                self.logger.error(f"PDF文件已加密，需要密码: {pdf_path}")
            else:
                self.logger.error(f"PDF文件损坏或无法读取: {pdf_path}, 错误: {e}")
            return False
    
    def get_pdf_info(self, pdf_path: str) -> Optional[dict]:
        """获取PDF文件信息
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            PDF文件信息字典，包含页数、文件大小等
        """
        if not self.validate_pdf(pdf_path):
            return None
        
        try:
            # 获取总页数
            images = convert_from_path(pdf_path, first_page=1, last_page=1)
            if not images:
                return None
            
            # 通过尝试转换所有页面来获取总页数
            all_images = convert_from_path(pdf_path)
            total_pages = len(all_images)
            
            # 获取文件大小
            file_size = os.path.getsize(pdf_path)
            
            return {
                'file_path': pdf_path,
                'total_pages': total_pages,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }
        except Exception as e:
            self.logger.error(f"获取PDF信息失败: {pdf_path}, 错误: {e}")
            return None
    
    def convert_pdf_to_images(self, pdf_path: str, dpi: int = None, 
                            page_range: Optional[Tuple[int, int]] = None) -> List[Image.Image]:
        """将PDF转换为图片列表
        
        Args:
            pdf_path: PDF文件路径
            dpi: 图片分辨率，默认使用配置中的值
            page_range: 页面范围 (start_page, end_page)，从1开始
            
        Returns:
            PIL图片对象列表
            
        Raises:
            FileProcessError: 文件处理错误
        """
        if not self.validate_pdf(pdf_path):
            raise FileProcessError(f"无效的PDF文件: {pdf_path}")
        
        if dpi is None:
            dpi = config.ocr_dpi
        
        try:
            self.logger.info(f"开始转换PDF: {pdf_path}, DPI: {dpi}")
            
            # 设置转换参数
            convert_kwargs = {
                'dpi': dpi,
                'fmt': 'RGB',
                'thread_count': config.max_workers
            }
            
            # 如果指定了页面范围
            if page_range:
                start_page, end_page = page_range
                convert_kwargs['first_page'] = start_page
                convert_kwargs['last_page'] = end_page
                self.logger.info(f"转换页面范围: {start_page}-{end_page}")
            
            # 转换PDF为图片
            images = convert_from_path(pdf_path, **convert_kwargs)
            
            if not images:
                raise FileProcessError("PDF转换结果为空")
            
            self.logger.info(f"PDF转换完成，共 {len(images)} 页")
            return images
            
        except Exception as e:
            error_msg = f"PDF转换失败: {pdf_path}, 错误: {e}"
            self.logger.error(error_msg)
            raise FileProcessError(error_msg)
    
    def convert_single_page(self, pdf_path: str, page_number: int, 
                          dpi: int = None) -> Optional[Image.Image]:
        """转换PDF的单个页面
        
        Args:
            pdf_path: PDF文件路径
            page_number: 页码（从1开始）
            dpi: 图片分辨率
            
        Returns:
            PIL图片对象，失败时返回None
        """
        try:
            images = self.convert_pdf_to_images(
                pdf_path, dpi, (page_number, page_number)
            )
            return images[0] if images else None
        except FileProcessError:
            return None
    
    def save_images_to_temp(self, images: List[Image.Image], 
                          prefix: str = "page") -> List[str]:
        """将图片保存到临时目录
        
        Args:
            images: PIL图片对象列表
            prefix: 文件名前缀
            
        Returns:
            保存的图片文件路径列表
        """
        saved_paths = []
        
        for i, image in enumerate(images, 1):
            try:
                filename = f"{prefix}_{i:04d}.png"
                file_path = os.path.join(self.temp_dir, filename)
                
                # 保存图片
                image.save(file_path, 'PNG', optimize=True)
                saved_paths.append(file_path)
                
                self.logger.debug(f"保存图片: {file_path}")
                
            except Exception as e:
                self.logger.error(f"保存图片失败: {e}")
                continue
        
        self.logger.info(f"保存了 {len(saved_paths)} 张图片到临时目录")
        return saved_paths
    
    def save_images_to_directory(self, images: List[Image.Image], 
                               output_dir: str, prefix: str = "page") -> List[str]:
        """将图片保存到指定目录
        
        Args:
            images: PIL图片对象列表
            output_dir: 输出目录路径
            prefix: 文件名前缀
            
        Returns:
            保存的图片文件路径列表
        """
        # 确保输出目录存在
        ensure_directory(output_dir)
        
        saved_paths = []
        
        for i, image in enumerate(images, 1):
            try:
                filename = f"{prefix}_{i:04d}.png"
                file_path = os.path.join(output_dir, filename)
                
                # 保存图片
                image.save(file_path, 'PNG', optimize=True)
                saved_paths.append(file_path)
                
                self.logger.info(f"保存图片: {file_path}")
                
            except Exception as e:
                self.logger.error(f"保存图片失败: {e}")
                continue
        
        self.logger.info(f"保存了 {len(saved_paths)} 张图片到目录: {output_dir}")
        return saved_paths
    
    def optimize_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """优化图片以提高OCR识别率
        
        Args:
            image: 原始图片
            
        Returns:
            优化后的图片
        """
        try:
            # 转换为灰度图
            if image.mode != 'L':
                image = image.convert('L')
            
            # 如果图片太小，进行放大
            width, height = image.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.logger.debug(f"图片放大: {width}x{height} -> {new_width}x{new_height}")
            
            return image
            
        except Exception as e:
            self.logger.warning(f"图片优化失败: {e}，使用原图")
            return image
    
    def batch_convert_pdf(self, pdf_path: str, batch_size: int = 5) -> List[List[Image.Image]]:
        """批量转换PDF页面
        
        Args:
            pdf_path: PDF文件路径
            batch_size: 每批处理的页面数
            
        Returns:
            分批的图片列表
        """
        pdf_info = self.get_pdf_info(pdf_path)
        if not pdf_info:
            return []
        
        total_pages = pdf_info['total_pages']
        batches = []
        
        for start_page in range(1, total_pages + 1, batch_size):
            end_page = min(start_page + batch_size - 1, total_pages)
            
            try:
                batch_images = self.convert_pdf_to_images(
                    pdf_path, page_range=(start_page, end_page)
                )
                batches.append(batch_images)
                self.logger.info(f"完成批次: 页面 {start_page}-{end_page}")
                
            except FileProcessError as e:
                self.logger.error(f"批次处理失败: 页面 {start_page}-{end_page}, 错误: {e}")
                continue
        
        return batches