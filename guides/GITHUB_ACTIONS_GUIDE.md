# GitHub Actions 自动打包指南

## 概述

本项目配置了 GitHub Actions workflow，可以自动为多个平台构建和发布 PDF OCR 工具的可执行文件。

## 支持的平台

- **Linux (x64)**: Ubuntu 最新版本
- **Windows (x64)**: Windows 最新版本
- **macOS (Universal)**: 支持 Intel 和 Apple Silicon 芯片

## 触发条件

workflow 会在以下情况下自动运行：

1. **标签推送**: 当推送以 `v` 开头的标签时（如 `v1.0.0`）
2. **Pull Request**: 向 `main` 或 `master` 分支提交 PR 时
3. **手动触发**: 在 GitHub Actions 页面手动运行

## 自动构建流程

### 1. 环境准备
- 设置 Python 3.12 环境
- 安装平台特定的系统依赖

### 2. 依赖安装

#### Linux (Ubuntu)
```bash
sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim poppler-utils
sudo apt-get install -y libtesseract-dev libleptonica-dev
```

#### macOS
```bash
brew install tesseract tesseract-lang poppler
```

#### Windows
- 自动下载并安装 Tesseract OCR
- 自动下载并配置 Poppler
- 自动设置环境变量

### 3. 打包过程
- 使用 PyInstaller 创建单文件可执行程序
- 包含所有必要的依赖和配置文件
- 支持中文 OCR 功能

### 4. 测试验证
- 自动测试生成的可执行文件
- 验证基本功能是否正常

### 5. 发布流程
- 创建压缩包（Windows: .zip, Linux/macOS: .tar.gz）
- 上传构建产物到 GitHub Artifacts
- 自动创建 GitHub Release（仅限标签推送）

## 如何发布新版本

### 方法一：使用 Git 标签（推荐）

1. 确保代码已提交到主分支
2. 创建并推送标签：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions 会自动构建并创建 Release

### 方法二：手动触发

1. 访问 GitHub 仓库的 Actions 页面
2. 选择 "Build and Release PDF OCR Tool" workflow
3. 点击 "Run workflow" 按钮
4. 选择分支并运行

## 构建产物

每次构建会生成以下文件：

- `pdf-ocr-linux-x64.tar.gz`: Linux 版本
- `pdf-ocr-windows-x64.zip`: Windows 版本
- `pdf-ocr-macos-universal.tar.gz`: macOS 通用版本

每个压缩包包含：
- 可执行文件 (`pdf_ocr` 或 `pdf_ocr.exe`)
- 配置文件 (`config.json`)
- 说明文档 (`README.md`)

## 使用构建的可执行文件

### Linux/macOS
```bash
# 解压
tar -xzf pdf-ocr-linux-x64.tar.gz
cd pdf-ocr-linux-x64

# 运行
./pdf_ocr input.pdf
```

### Windows
```cmd
# 解压 pdf-ocr-windows-x64.zip
# 进入解压目录

# 运行
pdf_ocr.exe input.pdf
```

## 故障排除

### 构建失败

1. **依赖安装失败**: 检查 `requirements.txt` 文件
2. **系统依赖问题**: 确认 Tesseract 和 Poppler 安装正确
3. **PyInstaller 错误**: 检查 Python 版本兼容性

### 可执行文件问题

1. **权限错误**: Linux/macOS 需要添加执行权限
   ```bash
   chmod +x pdf_ocr
   ```

2. **依赖缺失**: 确保目标系统有必要的运行时库

3. **中文识别问题**: 确认 Tesseract 中文语言包已包含

## 自定义配置

如需修改构建配置，编辑 `.github/workflows/build-release.yml` 文件：

- 修改 Python 版本
- 调整 PyInstaller 参数
- 添加新的平台支持
- 更改触发条件

## 注意事项

1. **GitHub Token**: Release 功能需要 `GITHUB_TOKEN`，这是自动提供的
2. **构建时间**: 完整构建可能需要 10-20 分钟
3. **存储限制**: GitHub Actions 有存储和时间限制
4. **版本管理**: 建议使用语义化版本号（如 v1.0.0）
5. **Artifacts v4**: 本项目已升级到 actions/upload-artifact@v4 和 actions/download-artifact@v4，享受98%的性能提升

## 🆕 Artifacts v4 升级

本项目已完成 GitHub Actions Artifacts v4 升级：

### 主要改进
- **性能提升**: 上传/下载速度提升 98%
- **更好的并行处理**: 优化的并发机制
- **改进的压缩**: 减少存储空间和传输时间

### 升级变化
- 使用 `actions/upload-artifact@v4` 和 `actions/download-artifact@v4`
- 调整了 artifact 下载路径结构
- 优化了 Release 文件路径配置

详细信息请参考：[GitHub Actions v4 升级指南](./GITHUB_ACTIONS_V4_UPGRADE.md)

## 监控构建状态

- 访问仓库的 Actions 页面查看构建状态
- 构建失败时会收到邮件通知（如果启用）
- 可以下载构建日志进行调试

通过这个自动化流程，您可以轻松地为多个平台构建和分发 PDF OCR 工具，无需手动配置各种环境和依赖。