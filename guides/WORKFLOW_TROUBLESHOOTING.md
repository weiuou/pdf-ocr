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

### 3. Windows 网络下载问题

**问题描述：**
```
Invoke-WebRequest : The request was aborted: The connection was closed unexpectedly.
Error: Process completed with exit code 1.
```

**原因分析：**
- GitHub Actions 中的网络连接不稳定
- 下载大文件时连接超时
- DNS 解析问题或防火墙限制

**解决方案：**
1. **多重下载策略**：
   - 优先使用 Chocolatey 包管理器（更稳定）
   - 备用手动下载方案
   - 自动重试机制（最多3次）

2. **改进的错误处理**：
   - 增加下载超时时间（300秒）
   - 使用 `-UseBasicParsing` 参数避免IE依赖
   - 详细的错误日志输出

3. **网络优化**：
   - 设置适当的安全协议
   - 分步骤下载和安装
   - 非关键组件失败时继续执行

### 4. GitHub Release权限问题

**问题描述：**
创建GitHub release时出现403权限错误：
```
⚠️ GitHub release failed with status: 403
undefined
```

**原因分析：**
1. **缺少权限设置**: workflow文件没有明确声明所需的权限
2. **GITHUB_TOKEN权限不足**: 默认token权限可能不包括创建release
3. **仓库设置问题**: 仓库的Actions权限设置可能有限制

**解决方案：**

1. **添加权限声明**
   在workflow文件顶部添加：
   ```yaml
   permissions:
     contents: write
     packages: write
     actions: read
   ```

2. **检查仓库设置**
   - 进入仓库 Settings → Actions → General
   - 确保 "Workflow permissions" 设置为 "Read and write permissions"
   - 或者至少允许 "Allow GitHub Actions to create and approve pull requests"

3. **验证token权限**
   - 确保使用的是 `${{ secrets.GITHUB_TOKEN }}`
   - 如果问题持续，可以考虑创建个人访问令牌(PAT)

**权限说明：**
- `contents: write`: 允许创建和修改releases
- `packages: write`: 允许发布包（如果需要）
- `actions: read`: 允许读取workflow运行状态

### 5. 依赖安装改进

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

## 6. Windows Tesseract环境变量问题

### 问题描述
在Windows上运行PDF OCR工具时出现错误：
```
Error opening data file C:\software\Tesseract-OCR/eng.traineddata 
Please make sure the TESSDATA_PREFIX environment variable is set to your "tessdata" directory.
Failed loading language 'eng'
Tesseract couldn't load any languages!
```

### 原因分析
1. **TESSDATA_PREFIX环境变量未设置**：Tesseract无法找到语言数据文件
2. **PATH环境变量缺失**：系统无法找到tesseract.exe
3. **安装路径问题**：Tesseract安装在非标准路径
4. **语言包缺失**：缺少必要的语言数据文件

### 解决方案

#### 自动配置（推荐）
最新版本已包含自动配置功能，会尝试：
- 自动检测Tesseract安装路径
- 自动设置TESSDATA_PREFIX环境变量
- 支持多种常见安装路径

#### 手动配置
1. **设置系统环境变量**：
   - 按 `Win + R`，输入 `sysdm.cpl`
   - 点击"环境变量"
   - 添加 `TESSDATA_PREFIX` = `C:\Program Files\Tesseract-OCR\tessdata`
   - 添加 `C:\Program Files\Tesseract-OCR` 到 PATH

2. **验证配置**：
   ```cmd
   tesseract --version
   tesseract --list-langs
   ```

详细配置指南请参考：[Windows Tesseract配置指南](WINDOWS_TESSERACT_SETUP.md)

## 更新历史

### v1.4 (当前版本)
- 添加Windows Tesseract环境变量自动配置
- 创建详细的Windows配置指南
- 改进OCR引擎的路径检测功能
- 增加多种常见安装路径支持

### v1.3
- 修复GitHub Release权限问题
- 添加workflow权限声明
- 完善权限配置指南
- 增加仓库设置检查说明

### v1.2
- 修复 Windows 网络下载问题
- 添加 Chocolatey 包管理器支持
- 实现自动重试下载机制
- 改进 Windows 依赖安装的可靠性
- 增加中文语言包自动下载

### v1.1
- 添加 `requirements.txt` 自动检查和回退机制
- 添加 `config.json` 自动创建功能
- 改进跨平台兼容性
- 增强错误处理和调试输出

### v1.0 (初始版本)
- 基本的多平台构建支持
- 系统依赖自动安装
- GitHub Release 自动发布