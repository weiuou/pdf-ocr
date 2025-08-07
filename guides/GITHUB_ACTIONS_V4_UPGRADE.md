# GitHub Actions Artifacts v4 升级指南

## 📋 升级概述

根据GitHub官方通知，从2025年1月30日开始，GitHub Actions将不再支持`actions/upload-artifact`和`actions/download-artifact`的v3版本。本项目已完成v4升级。

## 🔄 主要变化

### 1. 版本更新
- `actions/upload-artifact@v3` → `actions/upload-artifact@v4`
- `actions/download-artifact@v3` → `actions/download-artifact@v4`

### 2. 下载行为变化
**v3行为**：
```yaml
- name: Download all artifacts
  uses: actions/download-artifact@v3
# 直接下载到当前目录
```

**v4行为**：
```yaml
- name: Download all artifacts
  uses: actions/download-artifact@v4
  with:
    path: artifacts
# 下载到指定的artifacts目录
```

### 3. 文件路径调整
**v3路径**：
```yaml
files: |
  pdf-ocr-linux-x64/*
  pdf-ocr-windows-x64/*
  pdf-ocr-macos-universal/*
```

**v4路径**：
```yaml
files: |
  artifacts/pdf-ocr-linux-x64/*
  artifacts/pdf-ocr-windows-x64/*
  artifacts/pdf-ocr-macos-universal/*
```

## ⚡ 性能提升

v4版本带来的改进：
- **上传/下载速度提升98%**
- 更好的并行处理能力
- 减少网络传输时间
- 优化的压缩算法

## 🔧 升级后的配置

### Upload Artifact配置
```yaml
- name: Upload build artifacts
  uses: actions/upload-artifact@v4
  with:
    name: pdf-ocr-${{ matrix.platform }}-${{ matrix.arch }}
    path: |
      pdf-ocr-${{ matrix.platform }}-${{ matrix.arch }}.*
```

### Download Artifact配置
```yaml
- name: Download all artifacts
  uses: actions/download-artifact@v4
  with:
    path: artifacts
```

## ✅ 兼容性检查

升级后需要验证的功能：
- [ ] 多平台构建正常
- [ ] Artifact上传成功
- [ ] Release创建正确
- [ ] 文件路径访问正常

## 🚨 注意事项

1. **路径变化**：所有引用artifact的路径都需要添加`artifacts/`前缀
2. **下载目录**：v4默认不会创建artifact名称的子目录结构
3. **并发限制**：v4对并发上传有新的限制机制
4. **存储配额**：新版本有更严格的存储配额管理

## 📚 参考资源

- [GitHub Actions Artifacts v4 官方文档](https://github.com/actions/upload-artifact)
- [迁移指南](https://github.com/actions/upload-artifact/blob/main/docs/MIGRATION.md)
- [v4新功能说明](https://github.blog/changelog/2023-12-14-github-actions-artifacts-v4-is-now-generally-available/)

## 🔍 故障排除

### 常见问题

**问题1：找不到artifact文件**
```
Error: No files were found with the provided path
```
**解决方案**：检查文件路径是否包含`artifacts/`前缀

**问题2：下载失败**
```
Error: Unable to download artifact
```
**解决方案**：确认artifact名称和路径配置正确

**问题3：Release文件缺失**
```
Error: No files found for release
```
**解决方案**：验证download-artifact的path配置和files路径匹配

---

*最后更新：2025年1月*