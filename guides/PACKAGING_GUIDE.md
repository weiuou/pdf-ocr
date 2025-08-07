# PDF OCR工具 - 打包指南

## 快速开始

### 自动打包（推荐）

```bash
# 一键打包，自动检测当前平台
python build_cross_platform.py
```

## 平台特定打包

### macOS打包

```bash
# 生成macOS可执行文件
pyinstaller pdf_ocr_macos.spec --clean --noconfirm
```

**输出位置**: `dist/pdf-ocr-tool-macos/`

### Windows打包

⚠️ **注意**: 只能在Windows系统上打包Windows可执行文件

```bash
# 1. 下载Windows依赖（仅首次需要）
python download_windows_deps.py

# 2. 打包
pyinstaller pdf_ocr_windows.spec --clean --noconfirm
```

**输出位置**: `dist/pdf-ocr-tool-windows/`

## 架构兼容性说明

| 开发平台 | 目标平台 | 支持状态 |
|---------|---------|----------|
| macOS ARM64 | macOS ARM64 | ✅ 支持 |
| macOS ARM64 | macOS x86_64 | ❌ 不支持 |
| macOS ARM64 | Windows | ❌ 不支持 |
| Windows x86_64 | Windows x86_64 | ✅ 支持 |
| Windows x86_64 | macOS | ❌ 不支持 |
| Linux x86_64 | Linux x86_64 | ✅ 支持 |

## 跨平台解决方案

如果需要为其他平台打包，推荐以下方案：

### 1. 使用GitHub Actions

创建 `.github/workflows/build.yml`：

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: python build_cross_platform.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: pdf-ocr-${{ matrix.os }}
        path: dist/
```

### 2. 使用Docker

```dockerfile
# Dockerfile.windows
FROM python:3.11-windowsservercore

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install pyinstaller
RUN python download_windows_deps.py
RUN pyinstaller pdf_ocr_windows.spec --clean --noconfirm

CMD ["echo", "Build complete"]
```

### 3. 使用虚拟机

- **VirtualBox**: 免费的虚拟化解决方案
- **VMware**: 商业虚拟化软件
- **Parallels Desktop**: macOS上的虚拟化软件

## 故障排除

### 常见错误

#### 1. 架构不兼容错误

```
IncompatibleBinaryArchError: ... is incompatible with target arch x86_64 (has arch: arm64)
```

**解决方案**: 使用 `python build_cross_platform.py` 自动检测架构

#### 2. 依赖缺失

```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**: 
```bash
pip install -r requirements.txt
```

#### 3. Tesseract未找到

```
TesseractNotFoundError
```

**解决方案**: 确保已安装Tesseract OCR引擎

## 打包后的使用

1. 进入 `dist/` 目录
2. 找到对应平台的文件夹
3. 运行可执行文件：

```bash
# macOS/Linux
./pdf_ocr input.pdf

# Windows
pdf_ocr.exe input.pdf
```

## 分发说明

- 可执行文件包含所有依赖，无需安装Python
- 文件大小约30-50MB
- 支持离线使用
- 可以复制到其他同架构的电脑直接运行