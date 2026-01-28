import os
import re
import pymupdf  # PyMuPDF 核心库
import pymupdf4llm  # 用于将PDF转为高质量Markdown的库

# ======== 改这里 ========
# 请修改为你的PDF文件路径
PDF_PATH = r"path/to/your/prospectus.pdf"
# 请修改为输出目录路径
OUTPUT_DIR = r"path/to/output"
# =========================

# 表格检测策略配置
# "lines_strict" - 严格模式，只检测明确的网格线（默认）
# "lines" - 宽松模式，使用所有矢量图形检测
# "text" - 文本模式，用于无网格线的表格
TABLE_STRATEGY = "lines"  # 推荐使用 "lines" 以获得更好的表格检测

os.makedirs(OUTPUT_DIR, exist_ok=True)
FULL_MD = os.path.join(OUTPUT_DIR, "full.md")
CHAPTER_DIR = os.path.join(OUTPUT_DIR, "chapters")
os.makedirs(CHAPTER_DIR, exist_ok=True)


def extract_toc_from_pdf(pdf_path):
    """
    从 PDF 中提取内置目录（书签）
    返回: [(level, title, page_number), ...]
    """
    doc = pymupdf.open(pdf_path)
    toc = doc.get_toc()  # 获取目录，返回 [[level, title, page], ...]
    doc.close()
    return toc


def extract_pages_markdown(pdf_path, table_strategy="lines"):
    """
    逐页提取 PDF 内容为 Markdown
    返回: {page_number: markdown_text, ...} (页码从1开始)
    """
    print("  逐页提取 Markdown...")
    
    try:
        # 使用 page_chunks=True 获取每页的独立内容
        chunks = pymupdf4llm.to_markdown(
            pdf_path,
            table_strategy=table_strategy,
            force_text=True,
            ignore_graphics=False,
            show_progress=True,
            ignore_code=False,
            page_chunks=True,  # 关键：按页返回
        )
        
        # chunks 是一个列表，每个元素是一个字典，包含 "text" 和 "metadata"
        pages_md = {}
        for chunk in chunks:
            page_num = chunk["metadata"]["page"]  # 1-based page number
            pages_md[page_num] = chunk["text"]
        
        return pages_md
        
    except Exception as e:
        print(f"  提取失败: {e}")
        return None


def enhance_table_markdown(md_text):
    """
    后处理 Markdown 中的表格，修复常见问题
    """
    lines = md_text.split('\n')
    result_lines = []
    in_table = False
    table_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        is_table_line = stripped.startswith('|') and stripped.endswith('|')
        
        if is_table_line:
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
        else:
            if in_table:
                processed_table = process_table_block(table_lines)
                result_lines.extend(processed_table)
                result_lines.append("")
                in_table = False
                table_lines = []
            result_lines.append(line)
    
    if in_table and table_lines:
        processed_table = process_table_block(table_lines)
        result_lines.extend(processed_table)
    
    return '\n'.join(result_lines)


def process_table_block(table_lines):
    """处理一个表格块，修复格式问题"""
    if len(table_lines) < 2:
        return table_lines
    
    has_separator = False
    for i, line in enumerate(table_lines):
        if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
            has_separator = True
            break
    
    if not has_separator and len(table_lines) >= 1:
        first_row = table_lines[0]
        col_count = first_row.count('|') - 1
        if col_count > 0:
            separator = "| " + " | ".join(["---"] * col_count) + " |"
            table_lines.insert(1, separator)
    
    return table_lines


def split_by_toc(pages_md, toc, chapter_dir):
    """
    根据 PDF 目录按章节拆分文档
    
    参数:
        pages_md: {page_number: markdown_text} 字典
        toc: [(level, title, page), ...] 目录列表
        chapter_dir: 输出目录
    """
    if not toc:
        print("警告：PDF 没有内置目录，将使用备用方案。")
        return False
    
    print(f"\n从 PDF 目录中读取到 {len(toc)} 个章节:")
    
    # 只处理顶级章节（level=1）或者全部章节
    # 先分析目录结构
    levels = set(item[0] for item in toc)
    min_level = min(levels)
    
    # 筛选主要章节（使用最小层级，通常是1）
    main_chapters = [(i, item) for i, item in enumerate(toc) if item[0] == min_level]
    
    print(f"  - 目录层级: {sorted(levels)}")
    print(f"  - 主要章节数: {len(main_chapters)}")
    
    # 显示目录结构
    print("\n目录结构:")
    for level, title, page in toc[:20]:  # 只显示前20个
        indent = "  " * (level - 1)
        print(f"  {indent}[{level}] {title} (第{page}页)")
    if len(toc) > 20:
        print(f"  ... 共 {len(toc)} 个条目")
    
    # 按页码拆分章节
    print(f"\nStep 3: 按章节拆分...")
    
    total_pages = max(pages_md.keys()) if pages_md else 0
    
    for idx, (toc_idx, (level, title, start_page)) in enumerate(main_chapters):
        # 确定结束页码
        if idx + 1 < len(main_chapters):
            end_page = main_chapters[idx + 1][1][2] - 1
        else:
            end_page = total_pages
        
        # 收集该章节的所有页面内容
        chapter_content = []
        chapter_content.append(f"# {title}\n\n")
        
        for page_num in range(start_page, end_page + 1):
            if page_num in pages_md:
                page_text = pages_md[page_num]
                # 增强表格格式
                page_text = enhance_table_markdown(page_text)
                chapter_content.append(page_text)
                chapter_content.append(f"\n\n---\n<!-- Page {page_num} -->\n\n")
        
        # 生成安全的文件名
        safe_title = re.sub(r'[\\/:*?"<>|\n#]', '', title).strip()
        safe_title = safe_title[:50]  # 限制长度
        fname = f"{str(idx + 1).zfill(2)}_{safe_title}.md"
        fpath = os.path.join(chapter_dir, fname)
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(chapter_content))
        
        print(f"  -> {fname} (第{start_page}-{end_page}页)")
    
    return True


def split_by_regex_fallback(full_md, chapter_dir):
    """
    备用方案：使用正则表达式匹配章节标题
    """
    print("\n使用正则表达式匹配章节（备用方案）...")
    
    # 港股招股书常见章节标题
    CHAPTER_TITLES = [
        "警告", "重要提示", "目录", "概要", "释义", "技术词汇表", "前瞻性陈述",
        "风险因素", "豁免及免除", "有关本文件及编纂的资料", "董事及参与编纂的各方",
        "公司资料", "行业概览", "监管概览", "历史、重组及公司架构", "业务",
        "董事及高级管理层", "与控股股东的关系", "关联交易", "主要股东", "股本",
        "财务资料", "未来计划及编纂用途", "编纂的架构", "如何申请编纂",
        "附录一", "附录二", "附录三", "附录四", "附录五",
        "综合损益表", "综合资产负债表", "综合权益变动表", "综合现金流量表",
        "财务报表附注", "独立核数师报告", "会计师报告",
        "SUMMARY", "DEFINITIONS", "RISK FACTORS", "BUSINESS", "FINANCIAL INFORMATION",
        "WARNING", "IMPORTANT", "CONTENTS", "GLOSSARY"
    ]
    
    # 更宽松的正则匹配
    # 匹配行首的章节标题（可能有 # 号或者大写字母开头）
    pattern_str = r"(?m)^#{1,4}\s*(" + "|".join(map(re.escape, CHAPTER_TITLES)) + r")\s*$"
    
    matches = list(re.finditer(pattern_str, full_md, re.IGNORECASE))
    
    if not matches:
        # 尝试更宽松的匹配
        pattern_str = r"(?m)^[#\s]*(" + "|".join(map(re.escape, CHAPTER_TITLES)) + r").*$"
        matches = list(re.finditer(pattern_str, full_md, re.IGNORECASE))
    
    if not matches:
        print("警告：未能匹配到任何章节标题。")
        print("建议检查 PDF 是否有内置目录，或者章节标题格式是否标准。")
        return False
    
    print(f"共识别到 {len(matches)} 个章节节点。")
    
    for i, m in enumerate(matches):
        core_title = m.group(1)
        start_idx = m.start()
        
        if i + 1 < len(matches):
            end_idx = matches[i + 1].start()
        else:
            end_idx = len(full_md)
        
        section_content = full_md[start_idx:end_idx]
        
        safe_title = re.sub(r'[\\/:*?"<>|\n#]', '', core_title).strip()
        fname = f"{str(i + 1).zfill(2)}_{safe_title}.md"
        fpath = os.path.join(chapter_dir, fname)
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(section_content)
        
        print(f"  -> {fname}")
    
    return True


def process_pdf_with_enhanced_tables():
    """
    使用增强的表格处理功能处理 PDF
    """
    print("=" * 60)
    print("招股书 PDF 转 Markdown 工具 (增强表格版 v2)")
    print("=" * 60)
    
    print(f"\n输入文件: {PDF_PATH}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"表格策略: {TABLE_STRATEGY}")
    
    # Step 1: 提取 PDF 目录
    print("\nStep 1: 读取 PDF 内置目录...")
    toc = extract_toc_from_pdf(PDF_PATH)
    
    if toc:
        print(f"  成功读取 {len(toc)} 个目录项")
    else:
        print("  PDF 没有内置目录，将使用正则匹配")
    
    # Step 2: 提取每页的 Markdown
    print("\nStep 2: 提取 PDF 内容...")
    pages_md = extract_pages_markdown(PDF_PATH, TABLE_STRATEGY)
    
    if not pages_md:
        print("提取失败！")
        return
    
    print(f"  成功提取 {len(pages_md)} 页")
    
    # 保存全量文件
    full_content = []
    for page_num in sorted(pages_md.keys()):
        page_text = enhance_table_markdown(pages_md[page_num])
        full_content.append(f"<!-- Page {page_num} -->\n\n{page_text}")
    
    full_md = "\n\n---\n\n".join(full_content)
    
    with open(FULL_MD, "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"  全量文件已保存 -> {FULL_MD}")
    
    # Step 3: 按章节拆分
    if toc:
        success = split_by_toc(pages_md, toc, CHAPTER_DIR)
    else:
        success = split_by_regex_fallback(full_md, CHAPTER_DIR)
    
    if not success:
        print("\n章节拆分失败，但全量文件已保存。")
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"  - 全量文件: {FULL_MD}")
    print(f"  - 章节目录: {CHAPTER_DIR}")
    print("=" * 60)


# 运行主程序
if __name__ == "__main__":
    process_pdf_with_enhanced_tables()
