import re
from registry import checker

@checker.define_rule
def check_invalid_title_format(block):
    """
    Check: Validate Markdown heading format correctness.
    """
    line = block[5]
    if line is None:
        return None

    pattern = re.compile(r'^(#+)([^\s#].*)$')
    match = pattern.match(line)
    if not match:
        return None

    hashes = match.group(1)

    # allow headings that contain only hashes (edge case)
    if len(line.strip()) == len(hashes):
        return None

    prev_line = block[4]
    next_line = block[6]

    if (prev_line is not None and prev_line.lstrip().startswith("# ")) or \
       (next_line is not None and next_line.lstrip().startswith("# ")):
        return None

    col = len(hashes) + 1  # first character after '#'

    return f"invalid_markdown_heading_format at column {col}."

@checker.define_rule
def check_invalid_title_space(block):
    """
    Check: Heading lines must be surrounded by blank lines.
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return None

    prev_line = block[4]
    next_line = block[6]

    if (prev_line is not None and prev_line.lstrip().startswith("# ")) or \
       (next_line is not None and next_line.lstrip().startswith("# ")):
        return None

    # check above
    if prev_line is not None and prev_line.strip() != "":
        col = 1
        return f"missing_blank_line_before_heading at column {col}."

    # check below
    if next_line is not None and next_line.strip() != "":
        col = 1
        return f"missing_blank_line_after_heading at column {col}."

    return None

@checker.define_rule
def check_markdown_numbered_heading_invalid(block):
    """
    Check: Disallow numbered headings like '# 1', '## 1.1', etc.
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    match = re.match(r'^(#{1,6})\s+(\d+(?:\.\d+)*\.?)', stripped)
    if not match:
        return None

    hashes = match.group(1)
    number = match.group(2)

    idx = stripped.index(number)
    col = leading_spaces + idx + 1  # 1-based column

    return f"invalid_numbered_heading_not_allowed at column {col}."

@checker.define_rule
def check_invalid_spaces_and_unicode(block):
    """
    检查：文件是否包含隐藏的 UTF-8 空格 (emsp, 0x00A0) 或非显性 Unicode 符号。
    """
    line = block[5]
    if line is None:
        return None

    invalid_chars = {
        '\u200b': "zero-width space (\\u200b)",
        '\u200c': "zero-width non-joiner (\\u200c)",
        '\u200d': "zero-width joiner (\\u200d)",
        '\ufeff': "BOM (\\ufeff)",
        '\u00a0': "non-breaking space (\\u00a0 / 0x00A0)"
    }

    for char, name in invalid_chars.items():
        if char in line:
            col = line.index(char) + 1
            reason = f"invalid unicode character [{name}]"
            return f"{reason} at column {col}."

    return None

@checker.define_rule
def check_forbidden_jsx_imports(block):
    """
    检查：文档中是否包含了不允许的 import 或 export const 编写 JSX。
    """
    line = block[5]
    if line is None:
        return None

    allow_list = [
        'import Tabs from "@theme/Tabs";',
        'import TabItem from "@theme/TabItem";'
    ]

    if line in allow_list:
        return None

    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    match = re.match(r'^(import\s+.+from|export\s+const\s+)', stripped)
    if match:
        col = leading_spaces + match.start() + 1
        reason = "forbidden import or JSX-style export in document"
        return f"{reason} at column {col}."

    return None

@checker.define_rule
def check_admonition_spacing(block):
    """
    检查 ::: 上下是否有空行
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    if not stripped.startswith(":::"):
        return None

    leading_spaces = len(line) - len(stripped)
    col = line.index(":::") + 1  # 1-based column

    prev_line = block[4]
    next_line = block[6]

    # 1. 检查上方是否为空行
    if prev_line is not None:
        prev_stripped = prev_line.strip()
        if prev_stripped != "" and not prev_stripped.startswith(":::"):
            return f"missing_blank_line_above_admonition at column {col}."

    # 2. 检查下方是否为空行
    if next_line is not None:
        next_stripped = next_line.strip()
        if next_stripped != "" and not next_stripped.startswith(":::"):
            return f"missing_blank_line_below_admonition at column {col}."

    return None

@checker.define_rule
def check_invalid_br_tag(block):
    """
    检查：不允许使用 </br>
    """
    line = block[5]
    if line is None:
        return None

    lowered = line.lower()
    if "</br>" not in lowered:
        return None

    # column 计算
    idx = lowered.index("</br>")
    col = idx + 1  # 1-based

    return f"invalid_line_break_tag_use_br_or_br_self_closing at column {col}."

@checker.define_rule
def check_latex_special_characters(block):
    """
    检查：不应直接输入特殊物理/数学符号，应使用 LaTeX
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    forbidden_symbols = ["℃", "±", "×", "÷", "Ω", "°"]

    for sym in forbidden_symbols:
        if sym in line:
            idx = line.index(sym)
            col = leading_spaces + idx + 1  # 1-based

            return f"forbidden_special_character_use_latex at column {col}."

    return None

@checker.define_rule
def check_forbidden_aside_or_quote(block):
    """
    Check: Do not use '>' blockquotes for admonitions like note/tip/info.
    Use :::info[title] instead.
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    if not stripped.startswith(">"):
        return None

    leading_spaces = len(line) - len(stripped)
    idx = line.index(">")

    if re.search(r'\s*(备注|注意|提示|Note|Tip|info|note)\s*[:：]', stripped, re.IGNORECASE):
        col = leading_spaces + idx + 1
        return f"forbidden_blockquote_for_admonition_use_admonition_block at column {col}."

    return None

@checker.define_rule
def check_bold_in_headings(block):
    """
    Check: Do not use bold syntax (**text**) inside heading lines.
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    if not stripped.startswith("#"):
        return None

    if "**" not in line:
        return None

    idx = line.index("**")
    leading_spaces = len(line) - len(stripped)
    col = leading_spaces + idx + 1

    return f"invalid_bold_in_heading_line at column {col}."

@checker.define_rule
def check_invalid_list_punctuation(block):
    """
    Check:
    1. Do not use '1、' as list numbering format.
    2. Avoid using the punctuation '、' in normal text for readability and translation consistency.
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    # 1. invalid ordered list format: 1、xxx
    match = re.match(r'^(\d+)、', stripped)
    if match:
        col = leading_spaces + match.start(1) + len(match.group(1)) + 1
        return f"invalid_ordered_list_format_use_dot_instead at column {col}."

    # 2. general punctuation check for '、'
    if '、' in line:
        idx = line.index('、')
        col = leading_spaces + idx + 1
        return f"invalid_punctuation_use_comma_or_list_format at column {col}."

    return None

@checker.define_rule
def check_non_english_quotes(block):
    """
    Check: Disallow non-ASCII quotation marks for consistency in parsing and translation.
    """
    line = block[5]
    if line is None:
        return None

    # detect full line content (do not strip for indexing accuracy)
    forbidden_quotes = "“”‘’«»"

    for ch in forbidden_quotes:
        if ch in line:
            idx = line.index(ch)
            col = idx + 1  # 1-based column

            return f"non_ascii_quote_used_use_ascii_quotes_instead at column {col}."

    return None

@checker.define_rule
def check_invalid_html_anchor(block):
    """
    Check: Disallow HTML anchor tags (<a id="...">) that break Markdown reference consistency.
    """
    line = block[5]
    if line is None:
        return None

    match = re.search(r'<a\s+id\s*=', line, re.IGNORECASE)
    if not match:
        return None

    idx = match.start()
    col = idx + 1  # 1-based column

    return f"invalid_html_anchor_tag_use_markdown_link_instead at column {col}."

@checker.define_rule
def check_nested_numeric_list(block):
    """
    Check: Disallow nested ordered list inside unordered list (e.g., "- 1. xxx").
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    match = re.match(r'^[-*]\s+(\d+)\.', stripped)
    if not match:
        return None

    idx = match.start(1)
    col = leading_spaces + idx + 1  # 1-based column

    return f"invalid_nested_ordered_list_use_flat_numbering_at_top_level at column {col}."

@checker.define_rule
def check_img_element_usage(block):
    """
    Not Use <img> 
    """
    line = block[5]
    if line is None:
        return None

    allow_list = []
    if line in allow_list:
        return None

    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    # 匹配 <img ...>
    pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    match = pattern.search(line)

    if match:
        col = leading_spaces + match.start() + 1
        reason = "use_imageview_instead_of_img"
        return f"{reason} at column {col}."

    return None
