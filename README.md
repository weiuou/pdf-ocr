# PDF OCR 文字提取工具

一个基于 Python 的 PDF OCR 文字提取工具，支持将图像型 PDF 文档转换为可编辑的文本格式。

## 功能特性

- 🔍 **智能OCR识别**：基于 Tesseract 引擎，支持中英文混合识别
- 📄 **多格式输出**：支持 TXT、DOCX 格式输出
- 🎯 **高精度转换**：可调节 DPI 和置信度阈值
- 📊 **批量处理**：支持多页 PDF 批量转换
- 🔧 **灵活配置**：支持页面范围选择和自定义参数
- 📈 **处理统计**：提供详细的处理报告和统计信息

## 系统要求

- Python 3.7+
- Tesseract OCR 引擎
- poppler-utils（用于 PDF 转图像）

## 安装说明

### 1. 安装系统依赖

**macOS (推荐使用 Homebrew):**
```bash
# 安装 Tesseract OCR 引擎
brew install tesseract
# 安装 poppler (PDF 处理工具)
brew install poppler
```

**macOS (使用 Conda):**
```bash
# 如果 Homebrew 网络有问题，可以使用 conda
conda install -c conda-forge poppler
conda install -c conda-forge tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

**Windows:**
- 下载并安装 [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- 下载并安装 [poppler](https://blog.alivate.com.au/poppler-windows/)
- 确保将安装路径添加到系统 PATH 环境变量

### 2. 安装中文语言包（可选）

**macOS:**
```bash
brew install tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr-chi-sim tesseract-ocr-chi-tra
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 验证安装

验证 Tesseract 和 poppler 是否正确安装：

```bash
# 检查 Tesseract
tesseract --version
tesseract --list-langs

# 检查 poppler
pdfinfo --help
pdftoppm --help
```

如果命令执行成功，说明依赖已正确安装。

## 使用方法

### 基本用法

```bash
python main.py input.pdf
```

### 高级用法

```bash
# 指定输出格式和语言
python main.py input.pdf --output-format docx --language chi_sim+eng

# 设置 DPI 和置信度
python main.py input.pdf --dpi 300 --confidence 60

# 指定页面范围
python main.py input.pdf --pages 1-5,10,15-20

# 指定输出目录
python main.py input.pdf --output-dir ./output

# 显示详细统计信息
python main.py input.pdf --stats
```

### 命令行参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `input_pdf` | 输入的 PDF 文件路径 | 必需 |
| `--output-format` | 输出格式 (txt/docx) | txt |
| `--output-dir` | 输出目录 | ./output |
| `--language` | OCR 语言 | chi_sim+eng |
| `--dpi` | 图像 DPI | 300 |
| `--confidence` | OCR 置信度阈值 | 60 |
| `--pages` | 页面范围 | 全部页面 |
| `--max-workers` | 最大并发数 | 4 |
| `--stats` | 显示统计信息 | False |
| `--keep-temp` | 保留临时文件 | False |

## 配置文件

可以通过修改 `config.py` 来调整默认配置：

```python
class Config:
    # OCR 设置
    OCR_LANGUAGE = "chi_sim+eng"  # 支持的语言
    OCR_DPI = 300                 # 图像分辨率
    OCR_CONFIDENCE = 60           # 置信度阈值
    
    # 输出设置
    OUTPUT_FORMAT = "txt"         # 默认输出格式
    OUTPUT_DIR = "./output"       # 默认输出目录
    
    # 处理设置
    MAX_WORKERS = 4               # 最大并发数
    KEEP_TEMP_FILES = False       # 是否保留临时文件
```

## 支持的语言

工具支持 Tesseract 的所有语言包，常用语言代码：

- `eng`：英文
- `chi_sim`：简体中文
- `chi_tra`：繁体中文
- `jpn`：日文
- `kor`：韩文
- `fra`：法文
- `deu`：德文
- `spa`：西班牙文

可以使用 `+` 组合多种语言，如：`chi_sim+eng`

## 输出格式

### TXT 格式
- 纯文本格式
- 保留基本的段落结构
- 文件小，兼容性好

### DOCX 格式
- Microsoft Word 格式
- 保留更多格式信息
- 支持标题识别和样式
- 包含处理元数据

## 性能优化建议

1. **DPI 设置**：
   - 一般文档：200-300 DPI
   - 高质量文档：300-400 DPI
   - 低质量扫描：400-600 DPI

2. **并发处理**：
   - CPU 密集型：设置为 CPU 核心数
   - 内存受限：适当减少并发数

3. **页面范围**：
   - 大文档建议分批处理
   - 使用页面范围参数提高效率

## 故障排除

### 常见问题

**1. Tesseract 未找到**
```
TesseractNotFoundError: tesseract is not installed
```
解决方案：确保 Tesseract 已正确安装并添加到 PATH

**2. 语言包缺失**
```
TesseractError: (2, 'Error opening data file')
```
解决方案：安装对应的语言包

**3. PDF 转换失败**
```
PDFProcessingError: Failed to convert PDF
Unable to get page count. Is poppler installed and in PATH?
```
解决方案：
- 确保 poppler 已正确安装
- macOS: `brew install poppler` 或 `conda install -c conda-forge poppler`
- Ubuntu: `sudo apt-get install poppler-utils`
- 检查 PDF 文件是否损坏或加密

**4. 内存不足**
```
MemoryError: Unable to allocate array
```
解决方案：降低 DPI 或减少并发数

### 调试模式

启用详细日志输出：

```bash
python main.py input.pdf --stats --keep-temp
```

## 项目结构

```
pdf-ocr-auto/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── utils.py             # 工具函数
├── pdf_processor.py     # PDF 处理模块
├── ocr_engine.py        # OCR 引擎
├── text_formatter.py    # 文本格式化
├── requirements.txt     # 依赖配置
├── README.md           # 使用说明
└── output/             # 输出目录
    ├── temp/           # 临时文件
    └── results/        # 结果文件
```

## 开发说明

### 扩展功能

1. **添加新的输出格式**：
   - 在 `text_formatter.py` 中添加新的格式化方法
   - 更新 `Config` 类中的支持格式列表

2. **优化 OCR 算法**：
   - 在 `ocr_engine.py` 中调整图像预处理
   - 实验不同的 Tesseract 配置参数

3. **添加 GUI 界面**：
   - 可以基于 tkinter 或 PyQt 开发图形界面
   - 保持核心逻辑不变，只需要包装调用接口

### 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的 PDF OCR 功能
- 支持中英文识别
- 支持 TXT 和 DOCX 输出格式

---

如有问题或建议，请提交 Issue 或联系开发者。