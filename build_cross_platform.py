#!/usr/bin/env python3
"""
跨平台打包脚本
自动检测当前平台并选择合适的打包配置
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_platform_info():
    """获取平台信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print(f"操作系统: {system}")
    print(f"架构: {machine}")
    print(f"Python版本: {sys.version}")
    
    return system, machine

def build_for_current_platform():
    """为当前平台构建可执行文件"""
    system, machine = get_platform_info()
    
    # 选择合适的spec文件
    if system == 'darwin':  # macOS
        spec_file = 'pdf_ocr_macos.spec'
        print("\n使用macOS配置进行打包...")
    elif system == 'windows':
        spec_file = 'pdf_ocr_windows.spec'
        print("\n使用Windows配置进行打包...")
    elif system == 'linux':
        spec_file = 'pdf_ocr_linux.spec'
        print("\n使用Linux配置进行打包...")
    else:
        print(f"\n不支持的平台: {system}")
        return False
    
    # 检查spec文件是否存在
    if not Path(spec_file).exists():
        print(f"错误: 配置文件 {spec_file} 不存在")
        return False
    
    # 执行PyInstaller
    try:
        print(f"\n开始打包，使用配置文件: {spec_file}")
        cmd = ['pyinstaller', spec_file, '--clean', '--noconfirm']
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("\n打包成功!")
        print("输出:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        print("错误输出:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("\n错误: 未找到pyinstaller命令")
        print("请先安装PyInstaller: pip install pyinstaller")
        return False

def main():
    """主函数"""
    print("PDF OCR工具 - 跨平台打包脚本")
    print("=" * 40)
    
    # 检查是否在项目根目录
    if not Path('main.py').exists():
        print("错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 开始打包
    success = build_for_current_platform()
    
    if success:
        print("\n✅ 打包完成!")
        print("\n可执行文件位置:")
        
        # 查找生成的可执行文件
        dist_dir = Path('dist')
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                if item.is_dir():
                    print(f"  📁 {item}")
                    exe_files = list(item.glob('pdf_ocr*'))
                    for exe in exe_files:
                        print(f"    🚀 {exe}")
        
        print("\n使用说明:")
        print("1. 进入dist目录中的对应文件夹")
        print("2. 运行可执行文件进行OCR处理")
        print("3. 可以将整个文件夹复制到其他电脑使用")
    else:
        print("\n❌ 打包失败")
        sys.exit(1)

if __name__ == '__main__':
    main()