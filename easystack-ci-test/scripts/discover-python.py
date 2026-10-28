#!/usr/bin/env python3
"""用独立 Python 3 读取 tox.ini, 按 major 映射并核验指定 CI 解释器。"""

import argparse
import configparser
import json
from pathlib import Path
import re
import subprocess
import sys


# 只使用内建 sys, 防止 cwd 的 json.py 等项目模块伪造版本; 兼容 Python 2.7/3。
VERSION_QUERY = ("import sys; sys.stdout.write('%d.%d.%d\\n' % sys.version_info[:3]); "
                 "sys.stdout.write(sys.executable)")


def require_ci_host(required, actual):
    if required is None:
        raise ValueError('tox Python major 未确认, 停止执行 CI, 不默认选择版本')
    if tuple(actual[:2]) != tuple(required):
        expected = '.'.join(str(value) for value in required)
        raise ValueError('CI requires Python {}; 实际解释器不符合, 停止执行 CI'.format(expected))


def inspect_ci_python(executable):
    path = Path(executable)
    if not path.is_absolute() or not path.is_file():
        raise ValueError('--ci-python 必须是已存在解释器的绝对路径, 不自动安装')
    result = subprocess.run([str(path), '-B', '-E', '-s', '-S', '-c', VERSION_QUERY],
                            shell=False, capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise ValueError('CI 解释器版本查询失败, exit {}'.format(result.returncode))
    version, separator, actual_executable = result.stdout.partition('\n')
    if not separator or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version) or not actual_executable:
        raise ValueError('CI 解释器版本字段无效')
    return {'requested_executable': str(path), 'version': [int(part) for part in version.split('.')],
            'executable': actual_executable}


def discover(project_root, envs=('cover', 'pep8')):
    root = Path(project_root)
    config = configparser.RawConfigParser(interpolation=None)
    tox_path = root / 'tox.ini'
    if not tox_path.is_file():
        raise ValueError('未找到 tox.ini; 先确认项目实际测试入口')
    config.read(tox_path, encoding='utf-8')
    targets = {}
    issues = []
    for env in envs:
        section = 'testenv:' + env
        source = section if config.has_option(section, 'basepython') else 'testenv'
        value = config.get(source, 'basepython', fallback='').strip()
        # 不解析条件因子或变量引用; 保留原值, 不从其它环境猜测。
        plain = value and not any(char in value for char in '\n\r{}:')
        match = re.fullmatch(r'python([23])(?:\.(\d+))?', Path(value).name) if plain else None
        major = int(match.group(1)) if match else None
        minor = int(match.group(2)) if match and match.group(2) is not None else None
        targets[env] = {'source': source if value else None, 'basepython': value or None,
                        'major': major, 'minor': minor,
                        'status': 'resolved_major' if match else 'needs_resolution'}
        if major is None:
            issues.append('{}: Python major 未解析 ({})'.format(env, value or '缺少 basepython'))
    majors = {entry['major'] for entry in targets.values() if entry['major'] is not None}
    if len(majors) > 1:
        issues.append('所选 tox 环境有多个 Python major, 停止选择 CI 环境')
    required = None
    if not issues and len(majors) == 1:
        required = [2, 7] if majors == {2} else [3, 9]
    notes = []
    for env, entry in targets.items():
        if required and entry['minor'] is not None and [entry['major'], entry['minor']] != required:
            notes.append('{}: 保留 tox 显式目标 {}, 与映射 CI 版本分开核验, 不改 tox.ini'.format(
                env, entry['basepython']))

    metadata = configparser.RawConfigParser(interpolation=None)
    metadata.read(root / 'setup.cfg', encoding='utf-8')
    constraints = {}
    if metadata.has_option('options', 'python_requires'):
        constraints['setup.cfg:options.python_requires'] = metadata.get('options', 'python_requires').strip()
    pyproject = root / 'pyproject.toml'
    if pyproject.is_file():
        section = re.search(r'(?ms)^\[project\]\s*\n(.*?)(?=^\[|\Z)', pyproject.read_text(encoding='utf-8'))
        if section:
            requirement = re.search(
                r'''(?m)^requires-python\s*=\s*(["'])([^\n]*?)\1\s*(?:#.*)?$''', section.group(1))
            if requirement:
                constraints['pyproject.toml:project.requires-python'] = requirement.group(2)
    return {'ci_host_requirement': 'Python ' + '.'.join(map(str, required)) if required else None,
            'required_ci_version': required, 'mapping_status': 'resolved' if required else 'needs_resolution',
            'auxiliary_python': {'executable': sys.executable, 'version': sys.version.split()[0]},
            'ci_python': None, 'ready_for_ci': False, 'targets': targets,
            'issues': issues, 'target_notes': notes, 'project_constraints': constraints}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default='.', help='含 tox.ini 的项目目录')
    parser.add_argument('--env', action='append', choices=('cover', 'pep8'),
                        help='本次实际执行的 tox 环境, 可重复; 默认 cover 和 pep8')
    parser.add_argument('--ci-python', help='激活 CI 环境后取得的实际 Python 绝对路径')
    parser.add_argument('--check-ci-host', action='store_true', help='按 tox major 映射检查实际 CI 解释器')
    args = parser.parse_args()
    try:
        result = discover(args.project, tuple(dict.fromkeys(args.env or ('cover', 'pep8'))))
        if result['issues']:
            raise ValueError('; '.join(result['issues']))
        if args.check_ci_host and not args.ci_python:
            raise ValueError('CI 门禁必须提供 --ci-python, 不能把辅助 Python 当作 CI 解释器')
        if args.ci_python:
            result['ci_python'] = inspect_ci_python(args.ci_python)
            matches = tuple(result['ci_python']['version'][:2]) == tuple(result['required_ci_version'])
            result['ready_for_ci'] = matches
            if args.check_ci_host:
                require_ci_host(result['required_ci_version'], result['ci_python']['version'])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, configparser.Error, subprocess.SubprocessError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
