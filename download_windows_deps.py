#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows依赖下载脚本
用于下载Windows版本的Tesseract OCR和Poppler工具
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_file(url, filename):
    """下载文件"""
    print(f"正在下载: {filename}")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"下载完成: {filename}")
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """解压ZIP文件"""
    print(f"正在解压: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"解压完成: {extract_to}")
        return True
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def download_tesseract():
    """下载Tesseract OCR Windows版本"""
    print("\n=== 下载Tesseract OCR Windows版本 ===")
    
    # Tesseract 5.3.0 Windows版本
    tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221214/tesseract-ocr-w64-setup-5.3.0.20221214.exe"
    tesseract_portable_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221214/tesseract-ocr-w64-setup-5.3.0.20221214.exe"
    
    # 创建目录
    tesseract_dir = Path("tesseract-win64")
    tesseract_dir.mkdir(exist_ok=True)
    
    # 下载便携版（如果有的话）
    print("注意: Tesseract需要手动安装")
    print(f"请从以下链接下载Tesseract Windows版本:")
    print(f"  {tesseract_url}")
    print(f"安装后，请将安装目录复制到: {tesseract_dir.absolute()}")
    print("典型安装路径: C:\\Program Files\\Tesseract-OCR\\")
    
    return True

def download_poppler():
    """下载Poppler Windows版本"""
    print("\n=== 下载Poppler Windows版本 ===")
    
    # Poppler Windows版本
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.01.0-0/Release-23.01.0-0.zip"
    poppler_zip = "poppler-windows.zip"
    poppler_dir = Path("poppler-win64")
    
    # 下载Poppler
    if download_file(poppler_url, poppler_zip):
        # 解压
        if extract_zip(poppler_zip, "."):
            # 重命名目录
            extracted_dir = Path("poppler-23.01.0")
            if extracted_dir.exists():
                if poppler_dir.exists():
                    shutil.rmtree(poppler_dir)
                extracted_dir.rename(poppler_dir)
                print(f"Poppler已安装到: {poppler_dir.absolute()}")
            
            # 清理下载文件
            os.remove(poppler_zip)
            return True
    
    return False

def create_tesseract_structure():
    """创建Tesseract目录结构"""
    print("\n=== 创建Tesseract目录结构 ===")
    
    tesseract_dir = Path("tesseract-win64")
    tesseract_dir.mkdir(exist_ok=True)
    
    # 创建基本目录结构
    (tesseract_dir / "tessdata").mkdir(exist_ok=True)
    
    # 创建说明文件
    readme_content = """Tesseract OCR Windows版本安装说明

1. 从以下链接下载Tesseract Windows版本:
   https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221214/tesseract-ocr-w64-setup-5.3.0.20221214.exe

2. 安装Tesseract到默认位置 (C:\\Program Files\\Tesseract-OCR\\)

3. 将以下文件复制到此目录:
   - tesseract.exe (从安装目录复制)
   - tessdata文件夹 (包含语言数据文件)

4. 确保包含以下语言文件:
   - eng.traineddata (英文)
   - chi_sim.traineddata (简体中文)
   - chi_tra.traineddata (繁体中文，可选)

目录结构应该是:
tesseract-win64/
├── tesseract.exe
└── tessdata/
    ├── eng.traineddata
    ├── chi_sim.traineddata
    └── osd.traineddata
"""
    
    with open(tesseract_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"说明文件已创建: {tesseract_dir / 'README.txt'}")
    return True

def main():
    """主函数"""
    print("Windows依赖下载工具")
    print("=" * 50)
    
    # 检查操作系统
    if sys.platform != "win32":
        print("警告: 此脚本用于下载Windows依赖，当前系统不是Windows")
        print("继续执行以准备Windows打包所需的文件...")
    
    # 创建Tesseract目录结构
    create_tesseract_structure()
    
    # 下载Tesseract（需要手动安装）
    download_tesseract()
    
    # 下载Poppler
    if download_poppler():
        print("\n✅ Poppler下载完成")
    else:
        print("\n❌ Poppler下载失败")
    
    print("\n=== 下载完成 ===")
    print("请按照说明完成Tesseract的手动安装和配置")
    print("完成后可以运行Windows打包脚本")

if __name__ == "__main__":
    main()