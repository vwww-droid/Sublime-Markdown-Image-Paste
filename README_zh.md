# Sublime Markdown Image Paste

> **⚠️ 仅支持 macOS**：此插件目前仅支持 macOS 系统。

一个强大的 Sublime Text 插件，用于在 Markdown 文件中无缝粘贴和插入图片。自动保存剪贴板图片并生成正确的 Markdown 图片链接，支持灵活的路径配置。

![插件演示](i/cmd-shift-p-screenshot.png)

## ✨ 功能特性

- 🖼️ **剪贴板图片粘贴**：直接将剪贴板中的图片粘贴到 Markdown 文件中
- 📁 **文件图片插入**：插入本地图片文件并自动复制
- 🗂️ **灵活路径配置**：支持相对路径、绝对路径和环境变量
- 🎯 **智能上下文检测**：仅在 Markdown 文件中激活
- ⚙️ **高度可配置**：自定义文件命名、存储位置和链接生成
- 🔧 **自动目录创建**：自动创建图片存储目录

## 🚀 快速开始

### 从剪贴板粘贴
1. 复制一张图片（截图、网页图片等）
2. 在 Markdown 文件中定位光标
3. 按 `Ctrl+Shift+V` 或使用命令面板 → "MarkdownImagePaste: Paste Image from Clipboard"

### 从文件插入
1. 在 Markdown 文件中定位光标
2. 按 `Ctrl+Shift+I` 或使用命令面板 → "MarkdownImagePaste: Insert Image from File"
3. 在输入框中输入完整的文件路径

## ⚙️ 配置

通过编辑 `MarkdownImagePaste.sublime-settings` 来配置插件：

```json
{
    // 图片存储路径配置
    // 相对路径：相对于当前 markdown 文件，例如 "images" 或 "../assets/images"
    // 绝对路径：完整路径，例如 "/Users/username/Documents/blog/images"
    // 支持环境变量，例如 "$HOME/Pictures/blog"
    "image_folder": "images",
    
    // 图片文件名前缀
    "image_prefix": "image",
    
    // 是否在文件名中包含时间戳
    "include_timestamp": true,
    
    // 是否在文件名中包含唯一ID
    "include_unique_id": true,
    
    // 图片默认的 alt 文本
    "default_alt_text": "Image",
    
    // 支持的图片格式
    "supported_formats": ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.webp"],
    
    // Markdown 链接中的路径类型
    // "relative": 相对路径（推荐，便于移植）
    // "absolute": 绝对路径
    // "same_as_storage": 与存储路径配置保持一致
    "link_path_type": "relative"
}
```

### 路径配置示例

**相对路径：**
- `"images"` - 在当前文件旁创建 images 文件夹
- `"../assets/images"` - 使用父目录的 assets/images 文件夹
- `"docs/images"` - 使用当前文件旁的 docs/images 文件夹

**绝对路径：**
- `"/Users/username/Documents/blog/images"` - 指定完整路径
- `"$HOME/Pictures/blog"` - 使用环境变量
- `"~/Documents/images"` - 使用主目录快捷方式

**链接路径类型：**
- `"relative"` - 在 Markdown 链接中生成相对路径（推荐）
- `"absolute"` - 在 Markdown 链接中生成绝对路径
- `"same_as_storage"` - 与存储路径配置匹配

## 📋 系统要求

- **Sublime Text 4**
- **macOS**（目前仅支持 macOS）
- **pngpaste 工具**：使用 `brew install pngpaste` 安装
- 使用插件前必须先保存 Markdown 文件

## 📦 安装

1. 克隆或下载此仓库
2. 将插件文件夹复制到 Sublime Text Packages 目录：
   ```
   ~/Library/Application Support/Sublime Text/Packages/
   ```
3. 重启 Sublime Text
4. 安装 pngpaste：`brew install pngpaste`

## 🔧 故障排除

如果插件无法工作：

1. **检查控制台**：按 `Ctrl+\`` 打开控制台查看错误信息
2. **文件权限**：确保对目标目录有写入权限
3. **保存文件**：必须先保存 Markdown 文件
4. **pngpaste**：确保已安装 pngpaste（`brew install pngpaste`）

## 📄 许可证

MIT License
