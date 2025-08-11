# auto-novel-epub-fix-tool

本工具用于自动修复从轻小说机翻机器人网站 [n.novelia.cc](https://n.novelia.cc/)（对应 GitHub 项目：[auto-novel/auto-novel](https://github.com/auto-novel/auto-novel)）导出的 EPUB 文件中图片无法显示的问题。

## 功能简介
- 自动检测 EPUB 文件中缺失或损坏的图片链接
- 从原网站自动下载缺失图片
- 更新 EPUB 内容，确保图片在阅读器中正常显示

## 使用场景
适用于使用轻小说机翻机器人网站导出 EPUB 格式小说时，遇到图片无法显示的问题。

## 安装依赖
请先确保已安装 Python 3.7 及以上版本。

在项目根目录下运行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法
1. 将需要修复的 EPUB 文件（如 `input.epub`）准备好。
2. 在命令行中运行如下命令：

	```bash
	python image_fixer.py input.epub output.epub
	```

	其中 `input.epub` 为待修复的文件，`output.epub` 为修复后的输出文件。
3. 工具会自动修复图片问题，生成修复后的 EPUB 文件。

## 依赖说明
- requests
- beautifulsoup4
- pillow

## 相关链接
- 轻小说机翻机器人网站：[https://n.novelia.cc/](https://n.novelia.cc/)
- 相关 GitHub 项目：[https://github.com/auto-novel/auto-novel](https://github.com/auto-novel/auto-novel)

## 许可证
本项目遵循 MIT License。
