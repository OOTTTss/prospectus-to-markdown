# Prospectus to Markdown Converter / 招股书转Markdown工具

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

A professional PDF prospectus to Markdown converter, specially optimized for table recognition and chapter splitting.

### ✨ Features

- 📄 **High-quality PDF parsing**: Uses `pymupdf4llm` for layout restoration
- 📊 **Enhanced table detection**: Supports multiple table detection strategies, optimized for financial statements
- 📑 **Smart chapter splitting**: Automatically splits chapters based on PDF built-in table of contents
- 🌍 **Hong Kong prospectus optimized**: Specially optimized for Hong Kong prospectus format
- 🔄 **Fallback solution**: Uses regex matching when PDF has no table of contents

### 🚀 Quick Start

#### Installation

```bash
pip install pymupdf pymupdf4llm
```

#### Usage

1. Modify the path configuration in `1.py`:

```python
PDF_PATH = r"path/to/your/prospectus.pdf"  # Your PDF file path
OUTPUT_DIR = r"path/to/output"              # Output directory path
```

2. Run the program:

```bash
python 1.py
```

3. Check the output:

- `output/full.md` - Complete Markdown document
- `output/chapters/` - Chapter-split files

### 📋 Table Detection Strategies

The program supports three table detection strategies:

- `"lines_strict"` - Strict mode, only detects clear gridlines (default)
- `"lines"` - Loose mode, uses all vector graphics for detection (recommended)
- `"text"` - Text mode, for tables without gridlines

You can modify the `TABLE_STRATEGY` variable in the code to switch strategies.

### 📁 Output Structure

```
output/
├── full.md              # Complete document
└── chapters/            # Chapter-split files
    ├── 01_警告.md
    ├── 02_重要提示.md
    ├── 03_目录.md
    └── ...
```

### 🔧 Technical Implementation

- **PDF Parsing**: PyMuPDF (pymupdf)
- **Markdown Conversion**: pymupdf4llm
- **Table Processing**: Custom table format optimization algorithm
- **Chapter Splitting**: Based on PDF TOC (Table of Contents) or regex matching

### 📝 Supported Chapter Types

The program includes built-in common Hong Kong prospectus chapter titles, including:
- Warnings, Important Notices, Table of Contents, Summary
- Risk Factors, Business, Financial Information
- Appendix I to Appendix V
- And more...

### ⚠️ Notes

1. **PDF Requirements**: PDF files with built-in table of contents (bookmarks) are recommended for best results
2. **File Size**: Large files may take longer to process
3. **Table Recognition**: Complex tables may require adjusting the `TABLE_STRATEGY` parameter

### 🤝 Contributing

Issues and Pull Requests are welcome!

### 📄 License

This project is licensed under the MIT License.

### 🙏 Acknowledgments

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - Powerful PDF processing library
- [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) - PDF to Markdown conversion tool

---

<a name="中文"></a>
## 中文

一个专业的PDF招股书转Markdown工具，特别优化了表格识别和章节拆分功能。

### ✨ 功能特点

- 📄 **高质量PDF解析**：使用 `pymupdf4llm` 进行版面还原
- 📊 **增强表格检测**：支持多种表格检测策略，特别优化财务报表识别
- 📑 **智能章节拆分**：基于PDF内置目录自动拆分章节
- 🌍 **港股招股书优化**：针对香港招股书格式特别优化
- 🔄 **备用方案**：当PDF无目录时，使用正则表达式匹配章节标题

### 🚀 快速开始

#### 安装依赖

```bash
pip install pymupdf pymupdf4llm
```

#### 使用方法

1. 修改 `1.py` 中的路径配置：

```python
PDF_PATH = r"path/to/your/prospectus.pdf"  # 你的PDF文件路径
OUTPUT_DIR = r"path/to/output"              # 输出目录路径
```

2. 运行程序：

```bash
python 1.py
```

3. 查看输出：

- `output/full.md` - 完整的Markdown文档
- `output/chapters/` - 按章节拆分的文件

### 📋 表格检测策略

程序支持三种表格检测策略：

- `"lines_strict"` - 严格模式，只检测明确的网格线（默认）
- `"lines"` - 宽松模式，使用所有矢量图形检测（推荐）
- `"text"` - 文本模式，用于无网格线的表格

可在代码中修改 `TABLE_STRATEGY` 变量来切换策略。

### 📁 输出结构

```
output/
├── full.md              # 完整文档
└── chapters/            # 按章节拆分
    ├── 01_警告.md
    ├── 02_重要提示.md
    ├── 03_目录.md
    └── ...
```

### 🔧 技术实现

- **PDF解析**：PyMuPDF (pymupdf)
- **Markdown转换**：pymupdf4llm
- **表格处理**：自定义表格格式优化算法
- **章节拆分**：基于PDF TOC（Table of Contents）或正则匹配

### 📝 支持的章节类型

程序内置了港股招股书常见章节标题，包括：
- 警告、重要提示、目录、概要
- 风险因素、业务、财务资料
- 附录一至附录五
- 以及更多...

### ⚠️ 注意事项

1. **PDF要求**：建议使用有内置目录（书签）的PDF文件，效果最佳
2. **文件大小**：大文件处理可能需要较长时间
3. **表格识别**：复杂表格可能需要调整 `TABLE_STRATEGY` 参数

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 📄 许可证

本项目采用 MIT 许可证。

### 🙏 致谢

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - 强大的PDF处理库
- [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) - PDF转Markdown工具
