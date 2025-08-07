@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo PDF OCR Windows 打包脚本
echo ========================================
echo.

:: 检查Python环境
echo [1/6] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请确保Python已安装并添加到PATH环境变量
    pause
    exit /b 1
)
echo ✓ Python环境检查通过
echo.

:: 检查PyInstaller
echo [2/6] 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误: PyInstaller安装失败
        pause
        exit /b 1
    )
)
echo ✓ PyInstaller检查通过
echo.

:: 检查依赖
echo [3/6] 检查项目依赖...
if not exist "requirements.txt" (
    echo 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)

echo 正在安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 警告: 部分依赖安装可能失败，继续打包过程...
)
echo ✓ 依赖检查完成
echo.

:: 检查Tesseract
echo [4/6] 检查Tesseract OCR...
set "TESSERACT_FOUND=0"

:: 检查打包目录中的Tesseract
if exist "tesseract-win64\tesseract.exe" (
    echo ✓ 找到开发环境Tesseract: tesseract-win64\tesseract.exe
    set "TESSERACT_FOUND=1"
) else (
    :: 检查系统安装的Tesseract
    tesseract --version >nul 2>&1
    if not errorlevel 1 (
        echo ✓ 找到系统安装的Tesseract
        set "TESSERACT_FOUND=1"
    ) else (
        echo 警告: 未找到Tesseract OCR引擎
        echo 请确保:
        echo   1. 已运行 python download_windows_deps.py
        echo   2. 已手动安装Tesseract并复制到 tesseract-win64 目录
        echo   3. 或者系统已安装Tesseract OCR
        echo.
        echo 是否继续打包? (y/N)
        set /p "continue=请输入选择: "
        if /i not "!continue!"=="y" (
            echo 打包已取消
            pause
            exit /b 1
        )
    )
)
echo.

:: 检查Poppler
echo [5/6] 检查Poppler...
if exist "poppler-win64" (
    echo ✓ 找到Poppler: poppler-win64
else (
    echo 警告: 未找到Poppler工具
    echo 请运行: python download_windows_deps.py
)
echo.

:: 清理旧的构建文件
echo [6/6] 清理旧的构建文件...
if exist "build" (
    echo 删除旧的build目录...
    rmdir /s /q "build"
)
if exist "dist" (
    echo 删除旧的dist目录...
    rmdir /s /q "dist"
)
echo ✓ 清理完成
echo.

:: 开始打包
echo ========================================
echo 开始打包...
echo ========================================
echo.

echo 使用PyInstaller打包...
pyinstaller pdf_ocr_windows.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ❌ 打包失败!
    echo 请检查错误信息并重试
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成!
echo ========================================
echo.

:: 检查输出文件
if exist "dist\pdf_ocr.exe" (
    echo ✓ 可执行文件已生成: dist\pdf_ocr.exe
    
    :: 获取文件大小
    for %%A in ("dist\pdf_ocr.exe") do (
        set "size=%%~zA"
        set /a "sizeMB=!size!/1024/1024"
        echo   文件大小: !sizeMB! MB
    )
    
    echo.
    echo 使用方法:
    echo   dist\pdf_ocr.exe input.pdf
    echo   dist\pdf_ocr.exe input.pdf --save-images
    echo   dist\pdf_ocr.exe input.pdf --lang chi_sim+eng
    echo.
    
    echo 是否现在测试可执行文件? (y/N)
    set /p "test=请输入选择: "
    if /i "!test!"=="y" (
        echo.
        echo 测试可执行文件...
        "dist\pdf_ocr.exe" --help
        if not errorlevel 1 (
            echo ✓ 可执行文件测试通过
        ) else (
            echo ❌ 可执行文件测试失败
        )
    )
else (
    echo ❌ 未找到生成的可执行文件
    echo 请检查打包过程中的错误信息
)

echo.
echo 打包脚本执行完成
pause