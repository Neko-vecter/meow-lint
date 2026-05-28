import re
from registry import checker

@checker.define_rule
def rule_name(block):
    """
    规则说明（简洁说明检查什么）
    """
    line = block[5]
    if line is None:
        return None

    # 1. 允许列表（如有）
    allow_list = []
    if line in allow_list:
        return None

    # 2. 预处理（不要直接 strip 覆盖原始行）
    stripped = line.lstrip()
    leading_spaces = len(line) - len(stripped)

    # 3. 匹配逻辑
    match = None  # or regex.match(...)
    if match:
        col = leading_spaces + match.start() + 1

        reason = "short_error_reason_in_lowercase_snake_or_plain_phrase"
        return f"{reason} at column {col}."

    return None
