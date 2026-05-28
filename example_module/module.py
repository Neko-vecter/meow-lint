import re
from registry import checker

@checker.define_rule
def check_invalid_x_placeholder(block):
    # 把block 转换成行 目标行是 5
    # 0-4 是上面5行
    # 6-10 是下面5行
    # 如果上下没额外行会返回 None
    line = block[5]

    if line is None: 
        return None

    pattern = re.compile(r'')
    match = pattern.match(line)
    
    if match:
        all_hashes = match.group(1)
        col_missing = match.end(1)

        if len(line.strip()) == len(all_hashes):
            return None
            
        reason = "是由上面规则导致的报错"
        return f"❌ {reason} at column {col_missing}."
        
    return None
