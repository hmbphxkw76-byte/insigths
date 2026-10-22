# -*- coding: utf-8 -*-
"""临时脚本：修复函数体在def之后缺少缩进的方法."""
import re

with open('src/prompt_runtime/__init__.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 对于def在行N的方法,其函数体应该是缩进8空格而非4空格
# 找到def行(以4空格+def _method_japan_开头),然后检查后续行
fixed = 0
method_pattern = re.compile(r'^    def _method_japan_')
method_pattern2 = re.compile(r'^    def _method_japanese_gen_account')

i = 0
while i < len(lines):
    line = lines[i]
    if method_pattern.match(line) or method_pattern2.match(line):
        # 找到了一个方法def,现在修复其函数体
        j = i + 1
        while j < len(lines):
            l = lines[j]
            # 如果遇到另一个def或class或空行后跟着非缩进行,结束
            if l.strip() == '':
                j += 1
                continue
            if l.startswith('    def ') or l.startswith('class '):
                break
            # 修复函数体行:如果以4空格开头(但不是8空格),添加4空格
            if l.startswith('    ') and not l.startswith('        '):
                lines[j] = '    ' + l
                fixed += 1
            j += 1
        print(f'Method starting at line {i+1}: fixed body indent')
    i += 1

with open('src/prompt_runtime/__init__.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'Total lines fixed: {fixed}')
