# PDF OCR 工具 - Windows 平台使用说明

## 概述

本文档详细说明如何在 Windows 平台上打包和使用 PDF OCR 文本提取工具。该工具支持中英文混合文档的 OCR 识别，可以将 PDF 文档转换为可编辑的文本格式。

## 系统要求

- **操作系统**: Windows 10/11 (64位)
- **架构**: AMD64 (x86_64)
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 500MB 可用空间

## 打包准备

### 1. 开发环境要求

在进行打包之前，确保开发机器上已安装：

- Python 3.8+ (推荐 3.10 或更高版本)
- pip 包管理器
- Git (可选，用于代码管理)

### 2. 安装 Python 依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装 PyInstaller
pip install pyinstaller
```

### 3. 下载 Windows 依赖

运行依赖下载脚本：

```bash
python download_windows_deps.py
```

该脚本会自动下载：
- Poppler Windows 版本（PDF 处理工具）
- 创建 Tesseract 目录结构

### 4. 手动安装 Tesseract OCR

由于 Tesseract 需要手动安装，请按以下步骤操作：

1. **下载 Tesseract**:
   - 访问: https://github.com/UB-Mannheim/tesseract/releases
   - 下载最新版本的 Windows 安装包 (例如: `tesseract-ocr-w64-setup-5.3.0.20221214.exe`)

2. **安装 Tesseract**:
   - 运行下载的安装包
   - 选择安装路径 (默认: `C:\Program Files\Tesseract-OCR`)
   - 确保安装中文语言包 (`Chinese - Simplified`)

3. **复制文件到项目**:
   ```bash
   # 将整个 Tesseract 安装目录复制到项目的 tesseract-win64 文件夹
   xcopy "C:\Program Files\Tesseract-OCR" "tesseract-win64" /E /I
   ```

## 打包过程

### 自动打包 (推荐)

运行批处理脚本进行自动打包：

```bash
build_windows.bat
```

该脚本会自动执行以下步骤：
1. 检查 Python 环境
2. 安装/检查 PyInstaller
3. 安装项目依赖
4. 验证 Tesseract 和 Poppler
5. 清理旧的构建文件
6. 执行 PyInstaller 打包
7. 测试生成的可执行文件

### 手动打包

如果需要手动控制打包过程：

```bash
# 清理旧文件
rmdir /s /q build dist

# 执行打包
pyinstaller pdf_ocr_windows.spec --clean --noconfirm
```

## 打包结果

成功打包后，会在 `dist` 目录下生成：

```
dist/
└── pdf_ocr.exe          # 主可执行文件 (约 40-60MB)
```

## 使用说明

### 基本用法

```bash
# 基本 OCR 转换
pdf_ocr.exe input.pdf

# 指定输出目录
pdf_ocr.exe input.pdf --output-dir ./output

# 保存中间图像文件 (用于调试)
pdf_ocr.exe input.pdf --save-images

# 指定图像保存目录
pdf_ocr.exe input.pdf --save-images --images-dir ./debug_images
```

### 语言设置

```bash
# 仅英文识别
pdf_ocr.exe input.pdf --lang eng

# 仅中文识别
pdf_ocr.exe input.pdf --lang chi_sim

# 中英文混合识别 (默认)
pdf_ocr.exe input.pdf --lang chi_sim+eng
```

### 输出格式

```bash
# 输出为 TXT 格式 (默认)
pdf_ocr.exe input.pdf --format txt

# 输出为 DOCX 格式
pdf_ocr.exe input.pdf --format docx

# 同时输出两种格式
pdf_ocr.exe input.pdf --format txt,docx
```

### 高级选项

```bash
# 设置 OCR 置信度阈值
pdf_ocr.exe input.pdf --confidence 60

# 设置 DPI (影响图像质量)
pdf_ocr.exe input.pdf --dpi 300

# 启用详细日志
pdf_ocr.exe input.pdf --verbose

# 查看帮助信息
pdf_ocr.exe --help
```

## 输出文件说明

处理完成后，会生成以下文件：

```
output/
├── input.txt           # 主要文本内容
├── input_report.txt    # 处理报告和统计信息
└── input.docx          # Word 文档 (如果指定)
```

### 处理报告内容

`*_report.txt` 文件包含：
- 处理时间统计
- 页面数量和尺寸信息
- OCR 置信度统计
- 识别的文本语言分布
- 可能的问题和建议

## 故障排除

### 常见问题

1. **"找不到 Tesseract" 错误**
   - 确保已正确安装 Tesseract
   - 检查 `tesseract-win64` 目录是否包含完整文件
   - 验证 `tesseract.exe` 文件是否存在

2. **"找不到 Poppler" 错误**
   - 重新运行 `python download_windows_deps.py`
   - 检查 `poppler-win64` 目录是否存在

3. **OCR 识别率低**
   - 使用 `--save-images` 选项检查转换的图像质量
   - 尝试提高 DPI 设置 (`--dpi 300` 或更高)
   - 确保 PDF 文档质量良好

4. **中文识别失败**
   - 确保安装了中文语言包
   - 检查 `tesseract-win64/tessdata/chi_sim.traineddata` 文件是否存在
   - 使用 `--lang chi_sim` 强制中文识别

5. **程序启动失败**
   - 检查是否缺少 Visual C++ 运行库
   - 下载并安装 Microsoft Visual C++ Redistributable

### 调试模式

启用详细日志进行问题诊断：

```bash
pdf_ocr.exe input.pdf --verbose --save-images
```

这会输出详细的处理信息和保存中间图像文件。

## 性能优化

### 提高处理速度

1. **降低 DPI**: 对于文本清晰的 PDF，可以使用较低的 DPI (150-200)
2. **限制页面**: 对于大文档，可以先处理部分页面进行测试
3. **使用 SSD**: 将输入和输出文件放在 SSD 上

### 提高识别准确度

1. **提高 DPI**: 对于模糊或小字体的 PDF，使用更高的 DPI (300-600)
2. **预处理**: 确保 PDF 文档质量良好，避免扫描件
3. **语言设置**: 根据文档内容选择合适的语言组合

## 分发说明

### 单文件分发

生成的 `pdf_ocr.exe` 是一个独立的可执行文件，包含所有必要的依赖，可以直接在目标 Windows 系统上运行，无需安装 Python 或其他依赖。

### 系统兼容性

- **Windows 10**: 完全支持
- **Windows 11**: 完全支持
- **Windows 8.1**: 可能需要额外的运行库
- **Windows 7**: 不推荐，可能存在兼容性问题

### 安全说明

- 该工具不会连接网络
- 所有处理都在本地完成
- 不会收集或传输任何用户数据
- 可以在离线环境中使用

## 技术支持

如果遇到问题，请提供以下信息：

1. Windows 版本和架构
2. 错误信息的完整输出
3. 使用的命令行参数
4. PDF 文档的基本信息 (页数、大小、类型)
5. 使用 `--verbose` 选项的详细日志

## 跨平台打包说明

### ⚠️ 重要提示

由于架构限制，**无法在ARM64 macOS上直接打包x86_64 Windows可执行文件**。

### 推荐的打包方案

#### 方案1: 使用跨平台打包脚本（推荐）

```bash
# 自动检测当前平台并打包
python build_cross_platform.py
```

这个脚本会：
- 自动检测当前操作系统和架构
- 选择合适的打包配置
- 生成适合当前平台的可执行文件

#### 方案2: 手动选择平台配置

**在macOS上打包（生成macOS可执行文件）：**
```bash
pyinstaller pdf_ocr_macos.spec --clean --noconfirm
```

**在Windows上打包（生成Windows可执行文件）：**
```bash
# 1. 下载Windows依赖
python download_windows_deps.py

# 2. 使用Windows配置打包
pyinstaller pdf_ocr_windows.spec --clean --noconfirm
```

#### 方案3: 使用虚拟机或云服务

如果需要在macOS上生成Windows可执行文件：
1. 使用Windows虚拟机
2. 使用GitHub Actions等CI/CD服务
3. 使用云端Windows环境

## 更新说明

要更新工具到新版本：

1. 下载新的源代码
2. 重新运行打包过程
3. 替换旧的 `pdf_ocr.exe` 文件

配置文件和依赖通常向后兼容，但建议重新下载依赖以获得最新版本。