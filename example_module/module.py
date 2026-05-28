import re
from registry import checker

@checker.define_rule
def check_invalid_x_placeholder(line):
    pattern = re.compile(r'^##\s+(\d+\.[xXlL]).*')
    match = pattern.match(line)
    
    if match:
        # 获取整个正则匹配的起始和结束位置（因为有 ^，start 通常是 0）
        line_start = match.start() 
        
        # 获取第一个括号捕获组 (\d+\.[xXlL]) 在字符串中的具体列位置
        col_start = match.start(1)  # 错误标识开始的列号
        col_end = match.end(1)    # 错误标识结束的列号
        reason = "报错原因"
        # 
        return f"{reason} '{match.group(1)}' at columns {col_start}-{col_end}"
        
    return None
