#!/usr/bin/env python3
"""从明确解压根检索普通日志; 区分缺失输入、无命中与读取失败。"""

import argparse
from pathlib import Path
import re
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--pattern', action='append', required=True,
                        help='相对解压根的 .log glob, 可重复')
    match = parser.add_mutually_exclusive_group(required=True)
    match.add_argument('--text', help='按字面量匹配')
    match.add_argument('--regex', help='使用 Python 正则匹配')
    parser.add_argument('--ignore-case', action='store_true')
    parser.add_argument('--limit', type=int, default=200)
    parser.add_argument('--max-bytes', type=int, default=20 * 1024,
                        help='stdout 字节上限, 默认 20 KiB')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir() or args.limit < 1 or args.max_bytes < 1:
        parser.error('root 必须是目录, limit 和 max-bytes 必须大于 0')
    try:
        expression = re.compile(args.regex if args.regex is not None else re.escape(args.text),
                                re.IGNORECASE if args.ignore_case else 0)
        files = set()
        for pattern in args.pattern:
            if Path(pattern).is_absolute() or '..' in Path(pattern).parts:
                parser.error('pattern 必须是根目录内的相对路径')
            for path in root.glob(pattern):
                if path.is_file() and path.suffix == '.log':
                    if not path.relative_to(root).parts[0].startswith('ecs.'):
                        parser.error('只检索所选 ecs.* 原始节点目录, 不混入 components 视图')
                    resolved = path.resolve()
                    if root not in resolved.parents:
                        parser.error('匹配路径超出日志根目录')
                    if not resolved.relative_to(root).parts[0].startswith('ecs.'):
                        parser.error('解析后的来源不是 ecs.* 原始节点目录')
                    files.add(resolved)
        if not files:
            parser.exit(2, '没有匹配的 .log 文件; 这是输入/采集缺口, 不是未发生事件\n')
        hits = 0
        output_bytes = 0
        output_lines = 0
        limited = False
        for path in sorted(files):
            with path.open(encoding='utf-8', errors='replace') as stream:
                for number, line in enumerate(stream, 1):
                    if expression.search(line):
                        hits += 1
                        record = '{}:{}:{}\n'.format(path.relative_to(root), number, line.rstrip())
                        if output_lines >= args.limit or output_bytes >= args.max_bytes:
                            limited = True
                            continue
                        available = args.max_bytes - output_bytes
                        encoded = record.encode('utf-8')
                        if len(encoded) > available:
                            # 只截断展示, 扫描仍继续; exit 3 明确证据未完整输出。
                            record = encoded[:available].decode('utf-8', errors='ignore')
                            limited = True
                        sys.stdout.write(record)
                        output_bytes += len(record.encode('utf-8'))
                        output_lines += 1
        if not hits:
            parser.exit(1, '已检索 {} 个文件, 未命中; 仅代表这些来源没有目标记录\n'.format(len(files)))
        if limited:
            parser.exit(3, '达到输出上限; 扫描已完成, 显示 {} / {} 条命中, 部分证据未完整展示, 请缩小范围\n'.format(output_lines, hits))
    except (OSError, ValueError, re.error) as error:
        parser.exit(2, '日志检索失败: {}\n'.format(error))
    return 0


if __name__ == '__main__':
    sys.exit(main())
