#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR工具打包脚本
使用PyInstaller将OCR工具打包成独立可执行文件
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def get_system_info():
    """获取系统信息"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    return system, arch

def find_tesseract():
    """查找Tesseract安装路径"""
    tesseract_cmd = shutil.which('tesseract')
    if not tesseract_cmd:
        print("错误: 未找到Tesseract，请先安装Tesseract OCR")
        return None, None
    
    print(f"找到Tesseract: {tesseract_cmd}")
    
    # 查找tessdata目录
    possible_tessdata_paths = [
        '/opt/homebrew/share/tessdata',  # macOS Homebrew
        '/usr/share/tesseract-ocr/4.00/tessdata',  # Ubuntu
        '/usr/share/tesseract-ocr/tessdata',  # 其他Linux
        'C:\\Program Files\\Tesseract-OCR\\tessdata',  # Windows
        'C:\\Program Files (x86)\\Tesseract-OCR\\tessdata'  # Windows 32位
    ]
    
    tessdata_path = None
    for path in possible_tessdata_paths:
        if os.path.exists(path):
            tessdata_path = path
            break
    
    if not tessdata_path:
        # 尝试通过tesseract命令获取
        try:
            result = subprocess.run([tesseract_cmd, '--print-parameters'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'tessdata' in line and 'prefix' in line:
                    # 解析tessdata路径
                    parts = line.split()
                    for part in parts:
                        if 'tessdata' in part:
                            tessdata_path = part
                            break
        except Exception as e:
            print(f"警告: 无法自动检测tessdata路径: {e}")
    
    if tessdata_path:
        print(f"找到tessdata: {tessdata_path}")
    else:
        print("警告: 未找到tessdata目录")
    
    return tesseract_cmd, tessdata_path

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def run_pyinstaller():
    """运行PyInstaller打包"""
    print("开始PyInstaller打包...")
    
    try:
        # 运行PyInstaller
        cmd = ['pyinstaller', 'pdf_ocr.spec', '--clean']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("PyInstaller打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except FileNotFoundError:
        print("错误: 未找到PyInstaller，请先安装: pip install pyinstaller")
        return False

def copy_additional_files():
    """复制额外的文件到dist目录"""
    # 检查是否是单文件可执行文件
    exe_file = Path('dist/pdf_ocr')
    if exe_file.is_file():
        # 创建目录并移动可执行文件
        dist_dir = Path('dist/pdf_ocr_package')
        dist_dir.mkdir(exist_ok=True)
        
        # 移动可执行文件到新目录
        new_exe_path = dist_dir / 'pdf_ocr'
        if exe_file.exists():
            shutil.move(str(exe_file), str(new_exe_path))
            print(f"移动可执行文件到: {new_exe_path}")
    else:
        dist_dir = Path('dist/pdf_ocr')
        if not dist_dir.exists():
            print("错误: dist目录不存在")
            return False
    
    # 复制配置文件
    files_to_copy = [
        'config.json',
        'README.md'
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"复制文件: {file_name}")
    
    # 创建示例目录
    examples_dir = dist_dir / 'examples'
    examples_dir.mkdir(exist_ok=True)
    
    # 如果有示例PDF文件，复制它
    if os.path.exists('input.pdf'):
        shutil.copy2('input.pdf', examples_dir / 'sample.pdf')
        print("复制示例PDF文件")
    
    return True

def create_run_scripts():
    """创建运行脚本"""
    # 使用正确的dist目录
    dist_dir = Path('dist/pdf_ocr_package') if Path('dist/pdf_ocr_package').exists() else Path('dist/pdf_ocr')
    system, _ = get_system_info()
    
    if system == 'windows':
        # Windows批处理脚本
        bat_content = '''@echo off
echo PDF OCR工具
echo 使用方法: pdf_ocr.exe input.pdf [options]
echo.
pdf_ocr.exe %*
pause
'''
        with open(dist_dir / 'run.bat', 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print("创建Windows运行脚本: run.bat")
    else:
        # Unix shell脚本
        sh_content = '''#!/bin/bash
echo "PDF OCR工具"
echo "使用方法: ./pdf_ocr input.pdf [options]"
echo
./pdf_ocr "$@"
'''
        script_path = dist_dir / 'run.sh'
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(sh_content)
        # 设置执行权限
        os.chmod(script_path, 0o755)
        print("创建Unix运行脚本: run.sh")

def test_executable():
    """测试可执行文件"""
    # 使用正确的dist目录
    dist_dir = Path('dist/pdf_ocr_package') if Path('dist/pdf_ocr_package').exists() else Path('dist/pdf_ocr')
    system, _ = get_system_info()
    
    if system == 'windows':
        exe_path = dist_dir / 'pdf_ocr.exe'
    else:
        exe_path = dist_dir / 'pdf_ocr'
    
    if not exe_path.exists():
        print(f"错误: 可执行文件不存在: {exe_path}")
        return False
    
    print(f"测试可执行文件: {exe_path}")
    
    try:
        # 测试帮助信息
        result = subprocess.run([str(exe_path), '--help'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ 可执行文件测试通过")
            return True
        else:
            print(f"✗ 可执行文件测试失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ 可执行文件测试超时")
        return False
    except Exception as e:
        print(f"✗ 可执行文件测试出错: {e}")
        return False

def create_package_info():
    """创建打包信息文件"""
    # 使用正确的dist目录
    dist_dir = Path('dist/pdf_ocr_package') if Path('dist/pdf_ocr_package').exists() else Path('dist/pdf_ocr')
    system, arch = get_system_info()
    
    info_content = f'''PDF OCR工具 - 打包信息

构建时间: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}
系统平台: {system}
系统架构: {arch}
Python版本: {sys.version}

使用说明:
1. 将PDF文件放在同一目录下
2. 运行: ./pdf_ocr input.pdf (Unix) 或 pdf_ocr.exe input.pdf (Windows)
3. 查看输出文件

支持的选项:
--help          显示帮助信息
--language      设置OCR语言 (eng, chi_sim, chi_tra等)
--output-dir    设置输出目录
--format        设置输出格式 (txt, docx)
--save-images   保存中间图片文件
--confidence    设置置信度阈值

示例:
./pdf_ocr sample.pdf --language chi_sim+eng --format docx
'''
    
    with open(dist_dir / 'PACKAGE_INFO.txt', 'w', encoding='utf-8') as f:
        f.write(info_content)
    print("创建打包信息文件")

def main():
    """主函数"""
    print("=== PDF OCR工具打包脚本 ===")
    print()
    
    # 检查当前目录
    if not os.path.exists('main.py'):
        print("错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 获取系统信息
    system, arch = get_system_info()
    print(f"系统平台: {system} ({arch})")
    
    # 查找Tesseract
    tesseract_cmd, tessdata_path = find_tesseract()
    if not tesseract_cmd:
        sys.exit(1)
    
    # 清理构建目录
    clean_build_dirs()
    
    # 运行PyInstaller
    if not run_pyinstaller():
        sys.exit(1)
    
    # 复制额外文件
    if not copy_additional_files():
        sys.exit(1)
    
    # 创建运行脚本
    create_run_scripts()
    
    # 创建打包信息
    create_package_info()
    
    # 测试可执行文件
    if test_executable():
        print()
        print("🎉 打包完成！")
        package_dir = 'dist/pdf_ocr_package' if Path('dist/pdf_ocr_package').exists() else 'dist/pdf_ocr'
        print(f"可执行文件位置: {package_dir}/")
        print(f"系统平台: {system} ({arch})")
        print()
        print("下一步:")
        print("1. 测试可执行文件功能")
        print(f"2. 将整个 {package_dir} 目录复制到目标机器")
        print("3. 在目标机器上运行测试")
    else:
        print("❌ 打包失败，请检查错误信息")
        sys.exit(1)

if __name__ == '__main__':
    main()