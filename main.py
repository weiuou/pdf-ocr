#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR 文字提取工具
主程序入口，负责命令行参数解析和流程控制
"""

import argparse
import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional

# Windows平台支持
if sys.platform == 'win32':
    try:
        from config_windows import setup_windows_environment
        setup_windows_environment()
    except ImportError:
        pass

# 导入自定义模块
from config import config
from utils import (
    setup_logging, validate_file_path, ensure_directory, 
    generate_output_filename, format_time, cleanup_directory,
    OCRError, FileProcessError, ConfigError
)
from pdf_processor import PDFProcessor
from ocr_engine import OCREngine
from text_formatter import TextFormatter


class PDFOCRTool:
    """PDF OCR工具主类"""
    
    def __init__(self):
        """初始化OCR工具"""
        self.logger = setup_logging()
        self.pdf_processor = PDFProcessor()
        self.ocr_engine = OCREngine()
        self.text_formatter = TextFormatter()
        
    def process_pdf(self, pdf_path: str, output_path: str = None, 
                   output_format: str = None, language: str = None,
                   dpi: int = None, page_range: str = None, 
                   save_images: bool = False, images_dir: str = None) -> bool:
        """处理PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出文件路径
            output_format: 输出格式
            language: OCR语言
            dpi: 图片DPI
            page_range: 页面范围 (如: "1-5" 或 "3")
            save_images: 是否保存转换后的图片
            images_dir: 图片保存目录
            
        Returns:
            处理是否成功
        """
        start_time = time.time()
        self.logger.info(f"参数如下：")
        self.logger.info(f"- PDF文件: {pdf_path}")
        self.logger.info(f"- 输出路径: {output_path or '默认'}")
        self.logger.info(f"- 输出格式: {output_format or config.output_format}")
        self.logger.info(f"- OCR语言: {language or config.ocr_language}")
        self.logger.info(f"- DPI: {dpi or config.ocr_dpi}")
        self.logger.info(f"- 页面范围: {page_range or '全部'}")
        try:
            # 验证输入文件
            if not validate_file_path(pdf_path, ['.pdf']):
                self.logger.error(f"无效的PDF文件: {pdf_path}")
                return False
            
            # 获取PDF信息
            self.logger.info(f"开始处理PDF文件: {pdf_path}")
            pdf_info = self.pdf_processor.get_pdf_info(pdf_path)
            if not pdf_info:
                self.logger.error("无法获取PDF文件信息")
                return False
            
            self.logger.info(f"PDF信息: {pdf_info['total_pages']} 页, {pdf_info['file_size_mb']} MB")
            
            # 解析页面范围
            page_range_tuple = self._parse_page_range(page_range, pdf_info['total_pages'])
            
            # 转换PDF为图片
            self.logger.info("正在转换PDF为图片...")
            images = self.pdf_processor.convert_pdf_to_images(
                pdf_path, dpi=dpi, page_range=page_range_tuple
            )
            
            if not images:
                self.logger.error("PDF转换失败")
                return False
            
            # 保存原始图片（如果需要）
            if save_images:
                if not images_dir:
                    images_dir = os.path.join(config.output_directory, "images")
                
                self.logger.info(f"正在保存转换后的图片到: {images_dir}")
                pdf_name = Path(pdf_path).stem
                saved_image_paths = self.pdf_processor.save_images_to_directory(
                    images, images_dir, prefix=f"{pdf_name}_page"
                )
                self.logger.info(f"已保存 {len(saved_image_paths)} 张图片")
            
            # 优化图片
            self.logger.info("正在优化图片...")
            optimized_images = [
                self.pdf_processor.optimize_image_for_ocr(img) for img in images
            ]
            
            # OCR识别
            self.logger.info("开始OCR文字识别...")
            ocr_results = self.ocr_engine.batch_extract_text(
                optimized_images, language=language
            )
            
            if not ocr_results:
                self.logger.error("OCR识别失败")
                return False
            
            # 格式化文本
            self.logger.info("正在格式化文本...")
            formatted_text = self.text_formatter.format_ocr_results(ocr_results)
            
            # 生成输出路径
            if not output_path:
                output_path = generate_output_filename(
                    pdf_path, config.output_directory, output_format or config.output_format
                )
            
            # 保存结果
            self.logger.info(f"正在保存结果到: {output_path}")
            success = self.text_formatter.save_text(
                formatted_text, output_path, output_format
            )
            
            if not success:
                self.logger.error("保存文件失败")
                return False
            
            # 生成处理报告
            processing_time = time.time() - start_time
            # 生成报告文件路径，确保不会覆盖正文文件
            base_name = os.path.splitext(output_path)[0]
            report_path = f"{base_name}_report.txt"
            self.text_formatter.create_summary_report(
                ocr_results, report_path, processing_time
            )
            
            # 显示统计信息
            self._print_statistics(ocr_results, processing_time, output_path)
            
            # 清理临时文件
            if config.cleanup_temp:
                cleanup_directory(config.temp_directory)
            
            return True
            
        except (OCRError, FileProcessError, ConfigError) as e:
            self.logger.error(f"处理失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"未知错误: {e}")
            return False
    
    def _parse_page_range(self, page_range: str, total_pages: int) -> Optional[tuple]:
        """解析页面范围
        
        Args:
            page_range: 页面范围字符串
            total_pages: 总页数
            
        Returns:
            页面范围元组 (start, end) 或 None
        """
        if not page_range:
            return None
        
        try:
            if '-' in page_range:
                start, end = map(int, page_range.split('-'))
                start = max(1, start)
                end = min(total_pages, end)
                return (start, end)
            else:
                page = int(page_range)
                page = max(1, min(total_pages, page))
                return (page, page)
        except ValueError:
            self.logger.warning(f"无效的页面范围: {page_range}，将处理所有页面")
            return None
    
    def _print_statistics(self, ocr_results: list, processing_time: float, output_path: str):
        """打印统计信息
        
        Args:
            ocr_results: OCR结果列表
            processing_time: 处理时间
            output_path: 输出文件路径
        """
        stats = self.ocr_engine.get_ocr_statistics(ocr_results)
        
        print("\n" + "=" * 60)
        print("PDF OCR 处理完成")
        print("=" * 60)
        print(f"处理时间: {format_time(processing_time)}")
        print(f"总页数: {stats.get('total_pages', 0)}")
        print(f"总字符数: {stats.get('total_characters', 0):,}")
        print(f"总词数: {stats.get('total_words', 0):,}")
        print(f"平均置信度: {stats.get('average_confidence', 0):.2f}%")
        print(f"成功率: {stats.get('success_rate', 0):.2f}%")
        
        if stats.get('low_confidence_pages'):
            print(f"低置信度页面: {', '.join(map(str, stats['low_confidence_pages']))}")
        
        if stats.get('error_pages'):
            print(f"错误页面: {', '.join(map(str, stats['error_pages']))}")
        
        print(f"\n输出文件: {output_path}")
        print("=" * 60)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器
    
    Returns:
        参数解析器
    """
    parser = argparse.ArgumentParser(
        description="PDF OCR 文字提取工具 - 将图片格式的PDF转换为可编辑文字",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""使用示例:
  %(prog)s input.pdf                          # 使用默认设置处理PDF
  %(prog)s input.pdf -o output.txt            # 指定输出文件
  %(prog)s input.pdf -f docx                  # 输出为DOCX格式
  %(prog)s input.pdf -l chi_sim               # 仅使用中文识别
  %(prog)s input.pdf -d 600                   # 使用600 DPI
  %(prog)s input.pdf -p 1-5                   # 仅处理第1-5页
  %(prog)s input.pdf --save-images            # 保存转换后的图片
  %(prog)s input.pdf --save-images --images-dir ./pics  # 保存图片到指定目录
  %(prog)s input.pdf --no-format              # 不保持格式
  %(prog)s --list-languages                   # 列出可用语言
"""
    )
    
    # 位置参数
    parser.add_argument(
        'input_pdf',
        nargs='?',
        help='输入的PDF文件路径'
    )
    
    # 输出选项
    parser.add_argument(
        '-o', '--output',
        help='输出文件路径（默认在output目录下生成）'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['txt', 'docx'],
        default=config.output_format,
        help=f'输出格式 (默认: {config.output_format})'
    )
    
    # OCR选项
    parser.add_argument(
        '-l', '--language',
        default=config.ocr_language,
        help=f'OCR识别语言 (默认: {config.ocr_language})'
    )
    
    parser.add_argument(
        '-d', '--dpi',
        type=int,
        default=config.ocr_dpi,
        help=f'图片转换DPI (默认: {config.ocr_dpi})'
    )
    
    parser.add_argument(
        '-c', '--confidence',
        type=int,
        default=config.confidence_threshold,
        help=f'置信度阈值 (默认: {config.confidence_threshold})'
    )
    
    # 页面选项
    parser.add_argument(
        '-p', '--pages',
        help='页面范围，如 "1-5" 或 "3"（默认处理所有页面）'
    )
    
    # 格式选项
    parser.add_argument(
        '--no-format',
        action='store_true',
        help='不保持原文档格式'
    )
    
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='不清理临时文件'
    )
    
    parser.add_argument(
        '--save-images',
        action='store_true',
        help='保存PDF转换后的图片文件'
    )
    
    parser.add_argument(
        '--images-dir',
        help='图片保存目录（默认为output/images）'
    )
    
    # 信息选项
    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='列出可用的OCR语言'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='PDF OCR Tool v1.0'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(log_level)
    
    try:
        # 创建OCR工具实例
        ocr_tool = PDFOCRTool()
        
        # 列出可用语言
        if args.list_languages:
            languages = ocr_tool.ocr_engine.get_available_languages()
            print("可用的OCR语言:")
            for lang in sorted(languages):
                print(f"  {lang}")
            return 0
        
        # 检查输入文件
        if not args.input_pdf:
            parser.print_help()
            return 1
        
        if not os.path.exists(args.input_pdf):
            print(f"错误: 文件不存在: {args.input_pdf}")
            return 1
        
        # 更新配置
        if args.no_format:
            config.set('output', 'preserve_formatting', False)
        
        if args.no_cleanup:
            config.set('processing', 'cleanup_temp', False)
        
        if args.confidence != config.confidence_threshold:
            config.set('ocr', 'confidence_threshold', args.confidence)
        
        # 确保输出目录存在
        ensure_directory(config.output_directory)
        
        # 处理PDF
        success = ocr_tool.process_pdf(
            pdf_path=args.input_pdf,
            output_path=args.output,
            output_format=args.format,
            language=args.language,
            dpi=args.dpi,
            page_range=args.pages,
            save_images=args.save_images,
            images_dir=args.images_dir
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"程序异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())