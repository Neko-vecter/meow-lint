import re
from registry import checker

@checker.define_rule
def check_missing_space_after_hash(line):
    if line.startswith('#') and not re.match(r'^#+\s', line):
        return "Markdown 标题符号 '#' 后面缺少空格规范。"
    return None
