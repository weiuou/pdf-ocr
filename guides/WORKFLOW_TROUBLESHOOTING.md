# GitHub Actions Workflow 故障排除指南

## 常见问题及解决方案

### 1. "Could not open requirements file" 错误

**问题描述：**
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
Error: Process completed with exit code 1.
```

**原因分析：**
- `requirements.txt` 文件未被正确提交到仓库
- 文件路径问题或工作目录不正确

**解决方案：**
1. 确保 `requirements.txt` 文件存在于项目根目录
2. 检查 `.gitignore` 文件，确保没有忽略 `requirements.txt`
3. Workflow 已添加自动回退机制，如果找不到 `requirements.txt`，会自动安装必需的依赖包

### 2. "config.json not found" 错误

**问题描述：**
PyInstaller 构建时找不到 `config.json` 文件

**解决方案：**
- Workflow 已添加自动检查和创建机制
- 如果 `config.json` 不存在，会自动创建默认配置文件
- 默认配置包含所有必需的设置项

### 3. 依赖安装改进

**新特性：**
- 跨平台兼容的 Python 脚本检查文件存在性
- 自动回退到手动安装关键依赖包
- 详细的调试输出，显示当前目录内容

**包含的依赖包：**
- PyMuPDF==1.23.14 (PDF处理)
- pdf2image==1.16.3 (PDF转图像)
- pytesseract==0.3.10 (OCR引擎)
- Pillow==10.1.0 (图像处理)
- python-docx==1.1.0 (Word文档生成)
- psutil==5.9.6 (系统监控)
- tqdm==4.66.1 (进度条)
- PyInstaller (打包工具)

## 使用建议

### 本地测试
在推送到 GitHub 之前，建议本地测试：

```bash
# 检查必需文件
ls -la requirements.txt config.json

# 测试依赖安装
pip install -r requirements.txt

# 测试构建
python build.py
```

### 调试 Workflow
如果 Workflow 仍然失败：

1. 检查 Actions 日志中的详细输出
2. 确认所有必需文件都已提交
3. 验证 Python 版本兼容性
4. 检查系统依赖安装是否成功

### 文件检查清单
确保以下文件存在于项目根目录：
- ✅ `requirements.txt`
- ✅ `config.json`
- ✅ `main.py`
- ✅ 所有 Python 模块文件

## 更新历史

### v1.1 (当前版本)
- 添加 `requirements.txt` 自动检查和回退机制
- 添加 `config.json` 自动创建功能
- 改进跨平台兼容性
- 增强错误处理和调试输出

### v1.0 (初始版本)
- 基本的多平台构建支持
- 系统依赖自动安装
- GitHub Release 自动发布