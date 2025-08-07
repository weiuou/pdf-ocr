#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows平台专用配置文件
处理Windows平台的路径和依赖问题
"""

import os
import sys
from pathlib import Path

class WindowsConfig:
    """Windows平台配置类"""
    
    def __init__(self):
        self.base_dir = self._get_base_dir()
        self.tesseract_path = self._get_tesseract_path()
        self.poppler_path = self._get_poppler_path()
    
    def _get_base_dir(self):
        """获取程序基础目录"""
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            return Path(sys.executable).parent
        else:
            # 开发环境
            return Path(__file__).parent
    
    def _get_tesseract_path(self):
        """获取Tesseract路径"""
        # 打包后的路径
        bundled_path = self.base_dir / "tesseract" / "tesseract.exe"
        if bundled_path.exists():
            return str(bundled_path)
        
        # 开发环境路径
        dev_path = self.base_dir / "tesseract-win64" / "tesseract.exe"
        if dev_path.exists():
            return str(dev_path)
        
        # 系统安装路径
        system_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\tesseract\tesseract.exe",
        ]
        
        for path in system_paths:
            if Path(path).exists():
                return path
        
        # 从PATH环境变量查找
        import shutil
        tesseract_cmd = shutil.which("tesseract")
        if tesseract_cmd:
            return tesseract_cmd
        
        raise FileNotFoundError("未找到Tesseract OCR引擎，请确保已正确安装")
    
    def _get_poppler_path(self):
        """获取Poppler路径"""
        # 打包后的路径
        bundled_path = self.base_dir / "poppler" / "bin"
        if bundled_path.exists():
            return str(bundled_path)
        
        # 开发环境路径
        dev_path = self.base_dir / "poppler-win64" / "Library" / "bin"
        if dev_path.exists():
            return str(dev_path)
        
        # 备用路径
        alt_dev_path = self.base_dir / "poppler-win64" / "bin"
        if alt_dev_path.exists():
            return str(alt_dev_path)
        
        return None
    
    def setup_environment(self):
        """设置环境变量"""
        # 设置Tesseract路径
        os.environ['TESSERACT_CMD'] = self.tesseract_path
        
        # 设置Poppler路径
        if self.poppler_path:
            current_path = os.environ.get('PATH', '')
            if self.poppler_path not in current_path:
                os.environ['PATH'] = f"{self.poppler_path};{current_path}"
        
        # 设置tessdata路径
        tessdata_paths = [
            self.base_dir / "tesseract" / "tessdata",
            self.base_dir / "tesseract-win64" / "tessdata",
            Path(self.tesseract_path).parent / "tessdata",
        ]
        
        for tessdata_path in tessdata_paths:
            if tessdata_path.exists():
                os.environ['TESSDATA_PREFIX'] = str(tessdata_path.parent)
                break
    
    def get_config(self):
        """获取配置信息"""
        return {
            'base_dir': str(self.base_dir),
            'tesseract_path': self.tesseract_path,
            'poppler_path': self.poppler_path,
            'tessdata_prefix': os.environ.get('TESSDATA_PREFIX', ''),
        }
    
    def validate_dependencies(self):
        """验证依赖是否正确安装"""
        errors = []
        
        # 检查Tesseract
        if not Path(self.tesseract_path).exists():
            errors.append(f"Tesseract未找到: {self.tesseract_path}")
        
        # 检查Poppler
        if not self.poppler_path or not Path(self.poppler_path).exists():
            errors.append(f"Poppler未找到: {self.poppler_path}")
        
        # 检查tessdata
        tessdata_prefix = os.environ.get('TESSDATA_PREFIX')
        if tessdata_prefix:
            tessdata_dir = Path(tessdata_prefix) / "tessdata"
            if not tessdata_dir.exists():
                errors.append(f"Tessdata目录未找到: {tessdata_dir}")
            else:
                # 检查语言文件
                required_files = ['eng.traineddata', 'chi_sim.traineddata']
                for lang_file in required_files:
                    lang_path = tessdata_dir / lang_file
                    if not lang_path.exists():
                        errors.append(f"语言文件未找到: {lang_path}")
        
        return errors

def setup_windows_environment():
    """设置Windows环境"""
    if sys.platform == 'win32':
        config = WindowsConfig()
        config.setup_environment()
        
        # 验证依赖
        errors = config.validate_dependencies()
        if errors:
            print("依赖验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("Windows环境配置成功:")
        for key, value in config.get_config().items():
            print(f"  {key}: {value}")
        
        return True
    
    return True

if __name__ == "__main__":
    setup_windows_environment()