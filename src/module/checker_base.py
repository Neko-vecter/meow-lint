import re
from registry import checker

@checker.define_rule
def check_invalid_title_format(block):
    line = block[5]
    if line is None: 
        return None

    pattern = re.compile(r'^(#+)([^\s#].*)$')
    match = pattern.match(line)
    
    if match:
        all_hashes = match.group(1)
        col_missing = match.end(1)

        if len(line.strip()) == len(all_hashes):
            return None
            
        reason = "mdx 标题错误"
        return f"{reason} at column {col_missing}."
        
    return None

@checker.define_rule
def check_invalid_title_space(block):
    line = block[5]
    if not line: 
        return None

    # 修改正则：允许匹配标准的标题（# 后有空格），或者直接用 startswith
    if not line.startswith('#'):
        return None

    # 判定前后是否真的有文本（排除换行符的影响）
    has_text_above = block[4] is not None and block[4].strip() != ""
    has_text_below = block[6] is not None and block[6].strip() != ""

    if has_text_above or has_text_below:
        return "标题行前后必须有空行隔开."
        
    return None

@checker.define_rule
def check_invalid_spaces_and_unicode(block):
    """
    检查：文件是否包含隐藏的 UTF-8 空格 (emsp, 0x00A0) 或非显性 Unicode 符号。
    """
    line = block[5]
    if line is None:
        return None

    # \u200b: 零宽空格, \u200c: 零宽非连接符, \u200d: 零宽连接符, \ufeff: BOM, \u00a0: 不换行空格
    invalid_chars = {
        '\u200b': "零宽空格 (\\u200b)",
        '\u200c': "零宽非连接符 (\\u200c)",
        '\u200d': "零宽连接符 (\\u200d)",
        '\ufeff': "BOM 标记 (\\ufeff)",
        '\u00a0': "不换行空格 (\\u00a0 / 0x00A0)"
    }

    for char, name in invalid_chars.items():
        if char in line:
            col = line.index(char) + 1
            return f"❌ 包含隐藏/非显性 Unicode 字符: [{name}]，位置在第 {col} 列。请使用 Prettier 格式化修复。"
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

    # 匹配不在代码块内的顶层 import 或 export
    if re.match(r'^(import\s+.+from|export\s+const\s+)', line.strip()):
        return "禁止在文档内导入非规范库或编写 JSX 风格的 `import` / `export const`。"
    return None

@checker.define_rule
def check_admonition_spacing(block):
    """
    检查：::: 上下没有空行。
    block[4] 是上一行block[5] 是当前行block[6] 是下一行
    """
    line = block[5]
    if line is None:
        return None

    # 识别 :::info[xxx] 或 ::: 结尾
    if line.strip().startswith(':::'):
        prev_line = block[4]
        next_line = block[6]
        
        # 如果是开头的 :::，检查上一行是否为空行（除非是文件开头）
        if prev_line is not None and prev_line.strip() != "":
            # 排除连续闭合的情况，只有在上方有正文内容时才报错
            if not prev_line.strip().startswith(':::'):
                return "❌ Admonitions 语法错误：`:::` 上方必须留有一个空行。"
                
        # 如果是结尾的 :::，检查下一行是否为空行（除非是文件结尾）
        if next_line is not None and next_line.strip() != "":
            if not next_line.strip().startswith(':::'):
                return "❌ Admonitions 语法错误：`:::` 下方必须留有一个空行。"
                
    return None

@checker.define_rule
def check_invalid_br_tag(block):
    """
    检查：使用了不规范的 </br>。
    规范：如果必须使用换行，应使用 <br> 或 <br/>。
    """
    line = block[5]
    if line is None:
        return None

    if '</br>' in line.lower():
        return "❌ 错误的换行标签：使用了 `</br>`。请直接敲回车换行，或使用 `<br>` / `<br/>`。"
    return None

@checker.define_rule
def check_latex_special_characters(block):
    """
    检查：温度、电压、数学运算符等特殊字符是否直接打出。
    规范：这类字符需要使用 LaTeX 标记以增加可读性和兼容性
    这里主要针对常见的特殊符号做提示，可根据业务灵活增加。
    """
    line = block[5]
    if line is None:
        return None

    # 匹配直接输入的 ℃，以及常用于数学或物理的非 ASCII 符号
    # 注意：需排除在 Markdown 语法如 [^1] 或代码块内的情况（这里做简易判断）
    forbidden_symbols = [r'℃', r'±', r'×', r'÷', r'Ω']
    for sym in forbidden_symbols:
        if sym in line:
            return f"❌ 包含特殊字符 `{sym}`：请使用 LaTeX 进行标记（例如使用 $...$ 包含符号），不要使用输入法直打。"
    return None

@checker.define_rule
def check_forbidden_aside_or_quote(block):
    """
    检查：重要信息/note/info/tip 是否错误使用了 `>` 引用。
    规范：必须使用 :::info[xxx] 这种格式。
    """
    line = block[5]
    if line is None:
        return None

    # 检查是否以 `>` 开头，且紧跟了 "备注", "注意", "提示", "Note", "Tip"
    stripped = line.strip()
    if stripped.startswith('>'):
        if re.search(r'>\s*(备注|注意|提示|Note|Tip|info|tip|note)[:：]', stripped, re.IGNORECASE):
            return "❌ 格式错误：请勿使用 `>` 来标记重要提示。请改用 `:::info[标题]` 块级语法。"
    return None

@checker.define_rule
def check_bold_in_headings(block):
    """
    检查：在标题行（如 ##）中使用了 **xxx** 加粗。
    """
    line = block[5]
    if line is None:
        return None

    # 匹配以 # 开头的标题行中是否包含 **
    if line.strip().startswith('#') and '**' in line:
        return "❌ 标题行格式错误：请勿在标题行内使用 `**xxx**` 进行加粗。"
    return None

@checker.define_rule
def check_invalid_list_punctuation(block):
    """
    检查：
    1. 在普通语句中使用顿号 `、` 会导致翻译困难。
    2. 使用了 `1、xxx` 形式的错误列表。
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.strip()
    # 1. 检查数字加顿号的错误列表：例如 1、 2、
    if re.match(r'^\d+、', stripped):
        return "❌ 列表序号格式错误：使用了 `1、`。请修改为标准 Markdown 格式：`1. `（数字 + 点 + 空格）。"
    
    # 2. 检查单行文本里误用顿号（这会让翻译引擎难以处理）
    # 注：此规则可根据文档实际需求开启，若专业词汇必须用顿号，可调整此正则
    if '、' in line:
        # 如果不是在代码块内，抛出警告
        return "字符 `、`。在多语言翻译中顿号难以识别，建议改用逗号或标准列表格式。"
    return None

@checker.define_rule
def check_non_english_quotes(block):
    """
    检查输入中是否包含非英文引号（弯引号/全角引号），例如：
    “ ” ‘ ’ « »
    这些字符在部分解析/翻译场景中可能导致不一致或无法识别。
    """
    line = block[5]
    if line is None:
        return None

    stripped = line.strip()

    # 检测常见非英文引号
    if re.search(r'[“”‘’«»]', stripped):
        return "非英文引号（如 “ ” ‘ ’ « »）。建议统一替换为标准英文引号：\" 或 '。"

    return None

@checker.define_rule
def check_invalid_html_anchor(block):
    """
    检查：使用 <a> 作为链接引用（例如 <a id="xxx"></a>），这会破坏 md 引用关系。
    """
    line = block[5]
    if line is None:
        return None

    if re.search(r'<a\s+id=', line, re.IGNORECASE):
        return "链接引用错误：禁止使用 `<a id=\"...\">` 标签，容易出现编译不确定性。"
    return None


@checker.define_rule
def check_nested_numeric_list(block):
    """
    检查：不规范使用数字列表（例如 `- 1.xxx` 这种把数字写在无序列表里的写法）。
    """
    line = block[5]
    if line is None:
        return None

    if re.match(r'^-\s+\d+\.', line.strip()):
        return "嵌套数字列表不规范：请勿使用 `- 1. xxx`。请直接使用标准的 `1. xxx` 格式。"
    return None
