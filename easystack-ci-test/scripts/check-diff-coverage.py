#!/usr/bin/env python3
"""检查完整最终 diff 的全部新增/修改 Python 可执行行及分支。"""

import argparse
import ast
import json
from pathlib import Path
import re
import sys


def added_lines(diff):
    result = {}
    current = None
    seen = set()
    remaining = None
    saw_header = False
    file_had_hunk = False

    def finish_hunk():
        if remaining is not None and remaining != [0, 0]:
            raise ValueError('diff hunk 行数不完整或格式不支持')

    def finish_file():
        finish_hunk()
        if current is not None and not file_had_hunk:
            raise ValueError('diff 文件头缺少可解析的 hunk: ' + current)

    for line in diff.splitlines():
        if line.startswith('diff --git '):
            finish_file()
            current = None
            remaining = None
            file_had_hunk = False
        elif line.startswith('+++ ') and remaining in (None, [0, 0]):
            finish_file()
            current = line[4:].split('\t', 1)[0]
            if current.startswith('"'):
                current = ast.literal_eval(current)
            current = current[2:] if current.startswith('b/') else current
            if current != '/dev/null' and current in seen:
                raise ValueError('同一文件出现多个 diff; 请提供其最终工作树版本')
            seen.add(current)
            remaining = None
            saw_header = True
            file_had_hunk = False
        elif line.startswith('--- ') and remaining in (None, [0, 0]):
            finish_file()
            current = None
            remaining = None
            file_had_hunk = False
        elif line.startswith('@@ '):
            finish_hunk()
            match = re.fullmatch(r'@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*', line)
            if current is None or not match:
                raise ValueError('无法解析 diff hunk')
            old_count, start, new_count = match.groups()
            number = int(start)
            remaining = [int(old_count) if old_count is not None else 1,
                         int(new_count) if new_count is not None else 1]
            file_had_hunk = True
        elif line.startswith('@@'):
            raise ValueError('不支持 combined 或其他 diff hunk 格式')
        elif line.startswith('\\ No newline at end of file'):
            continue
        elif remaining is not None and line[:1] in ('+', '-', ' '):
            marker = line[0]
            if marker != '+':
                remaining[0] -= 1
            if marker != '-':
                if marker == '+' and current != '/dev/null':
                    result.setdefault(current, set()).add(number)
                number += 1
                remaining[1] -= 1
            if min(remaining) < 0:
                raise ValueError('diff hunk 行数超出声明范围')
        elif line.startswith(('Binary files ', 'GIT binary patch')):
            raise ValueError('二进制 diff 不支持行覆盖, 需单独核验')
    finish_file()
    if diff.strip() and not saw_header:
        raise ValueError('非空输入不是支持的 unified diff')
    return result


def check(diff, coverage):
    if not isinstance(coverage, dict):
        raise ValueError('coverage JSON 必须是对象')
    files = coverage.get('files')
    if not isinstance(files, dict):
        raise ValueError('coverage JSON 缺少 files')
    changes = added_lines(diff)
    failures = []
    checked = 0
    if any(name.endswith('.py') for name in changes):
        metadata = coverage.get('meta', {})
        if not isinstance(metadata, dict) or metadata.get('branch_coverage') is not True:
            failures.append({'reason': 'coverage 未确认启用分支测量, 不能证明没有 par'})
    for name, lines in changes.items():
        if not name.endswith('.py'):
            continue
        entry = files.get(name)
        if entry is None:
            failures.append({'file': name, 'reason': 'coverage 未报告修改文件, 需核验收集范围'})
            continue
        if not isinstance(entry, dict):
            raise ValueError('coverage 文件条目必须是对象')
        for key in ('executed_lines', 'missing_lines', 'missing_branches'):
            if key not in entry or not isinstance(entry[key], list):
                raise ValueError('coverage 文件缺少有效 ' + key + ': ' + name)
        for key in ('executed_lines', 'missing_lines', 'excluded_lines'):
            if not isinstance(entry.get(key, []), list) or any(
                    type(number) is not int or number < 1 for number in entry.get(key, [])):
                raise ValueError('coverage 行号格式无效: ' + name)
        if any(not isinstance(branch, list) or len(branch) != 2
               or any(type(value) is not int for value in branch)
               for branch in entry['missing_branches']):
            raise ValueError('coverage 分支格式无效: ' + name)
        missing = set(entry['missing_lines'])
        excluded = set(entry.get('excluded_lines', []))
        executable = set(entry['executed_lines']) | missing | excluded
        changed = lines & executable
        checked += len(changed)
        uncovered = sorted(changed & (missing | excluded))
        branches = [branch for branch in entry['missing_branches'] if branch[0] in changed]
        if uncovered or branches:
            failures.append({'file': name, 'uncovered_lines': uncovered,
                             'missing_branches': branches})
    return {'checked_executable_lines': checked, 'failures': failures,
            'non_python_files': sorted(name for name in changes if not name.endswith('.py'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diff', action='append', required=True, help='确认基线到最终工作树的完整 --unified=0 diff')
    parser.add_argument('--coverage', required=True, help='匹配最终代码版本的 coverage JSON')
    args = parser.parse_args()
    try:
        diff = '\n'.join(Path(path).read_text(encoding='utf-8') for path in args.diff)
        result = check(diff, json.loads(Path(args.coverage).read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError, KeyError, IndexError, SyntaxError) as error:
        parser.exit(2, str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['failures'] else 0


if __name__ == '__main__':
    sys.exit(main())
