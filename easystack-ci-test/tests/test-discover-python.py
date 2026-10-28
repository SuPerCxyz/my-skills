"""执行真实发现/门禁入口, 版本查询只在缺少对应解释器时 mock I/O。"""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / 'scripts' / 'discover-python.py'
SPEC = importlib.util.spec_from_file_location('discover_python', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write_tox('python3')

    def write_tox(self, value):
        (self.root / 'tox.ini').write_text('[testenv]\nbasepython = ' + value + '\n')

    def invoke(self, *args):
        output = io.StringIO()
        error = io.StringIO()
        with mock.patch.object(sys, 'argv', ['discover-python.py', '--project', str(self.root), *args]), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            try:
                MODULE.main()
                status = 0
            except SystemExit as exited:
                status = exited.code
        return status, output.getvalue(), error.getvalue()

    def version_result(self, version):
        return subprocess.CompletedProcess([], 0, '.'.join(map(str, version)) + '\n/fixture/ci/python', '')

    def test_major_two_maps_to_27(self):
        for value in ('python2', 'python2.7', '/opt/ci/bin/python2.7'):
            with self.subTest(value=value):
                self.write_tox(value)
                result = MODULE.discover(self.root)
                self.assertEqual([2, 7], result['required_ci_version'])
                self.assertEqual(value, result['targets']['cover']['basepython'])
                self.assertFalse(result['ready_for_ci'])
                self.assertIsNone(result['ci_python'])

    def test_major_three_maps_to_39_and_keeps_explicit_minor(self):
        for value in ('python3', 'python3.9', 'python3.11'):
            with self.subTest(value=value):
                self.write_tox(value)
                result = MODULE.discover(self.root)
                self.assertEqual([3, 9], result['required_ci_version'])
                self.assertEqual(value, result['targets']['pep8']['basepython'])
                if value == 'python3.11':
                    self.assertTrue(result['target_notes'])

    def test_selected_env_and_inheritance_are_respected(self):
        (self.root / 'tox.ini').write_text(
            '[testenv]\nbasepython = python2\n[testenv:pep8]\nbasepython = python3\n')
        result = MODULE.discover(self.root, ('cover',))
        self.assertEqual([2, 7], result['required_ci_version'])
        self.assertEqual('testenv', result['targets']['cover']['source'])
        self.assertEqual([3, 9], MODULE.discover(self.root, ('pep8',))['required_ci_version'])
        mixed = MODULE.discover(self.root)
        self.assertIsNone(mixed['required_ci_version'])
        self.assertIn('多个 Python major', '; '.join(mixed['issues']))

    def test_dynamic_missing_and_mixed_constraints_fail_before_version_query(self):
        inputs = [
            '[tox]\nenvlist = cover,pep8\n',
            '[testenv]\nbasepython = {env:TARGET_PYTHON:python3.9}\n',
            '[testenv]\nbasepython =\n    py27: /opt/python2.7\n    py39: python3.9\n',
            '[testenv]\nbasepython = python2\n[testenv:pep8]\nbasepython = python3\n',
        ]
        for text in inputs:
            with self.subTest(text=text):
                (self.root / 'tox.ini').write_text(text)
                with mock.patch.object(MODULE.subprocess, 'run') as query:
                    status, output, error = self.invoke('--check-ci-host', '--ci-python', sys.executable)
                self.assertEqual(2, status)
                self.assertFalse(output)
                self.assertTrue('未解析' in error or '多个 Python major' in error)
                query.assert_not_called()

    def test_check_requires_explicit_ci_python(self):
        status, _, error = self.invoke('--check-ci-host')
        self.assertEqual(2, status)
        self.assertIn('必须提供 --ci-python', error)

    def test_auxiliary_python_three_can_check_ci_27_via_real_argv_path(self):
        self.write_tox('python2')
        with mock.patch.object(MODULE.subprocess, 'run', return_value=self.version_result([2, 7, 18])) as query:
            status, output, _ = self.invoke('--ci-python', sys.executable, '--check-ci-host')
        self.assertEqual(0, status)
        result = json.loads(output)
        self.assertTrue(result['ready_for_ci'])
        self.assertEqual([2, 7, 18], result['ci_python']['version'])
        self.assertEqual(sys.executable, result['auxiliary_python']['executable'])
        argv = query.call_args.args[0]
        self.assertEqual(sys.executable, argv[0])
        self.assertEqual(['-B', '-E', '-s', '-S', '-c'], argv[1:6])
        self.assertEqual(MODULE.VERSION_QUERY, argv[-1])
        self.assertFalse(query.call_args.kwargs['shell'])

    def test_actual_version_must_match_mapped_requirement(self):
        for configured, actual in [('python2', [3, 9, 25]), ('python3', [2, 7, 18]),
                                   ('python3', [3, 11, 9])]:
            with self.subTest(configured=configured, actual=actual):
                self.write_tox(configured)
                with mock.patch.object(MODULE.subprocess, 'run', return_value=self.version_result(actual)):
                    status, _, error = self.invoke('--check-ci-host', '--ci-python', sys.executable)
                self.assertEqual(2, status)
                self.assertIn('实际解释器不符合', error)

    def test_real_interpreter_query_uses_selected_ci_executable(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--project', str(self.root),
                                 '--check-ci-host', '--ci-python', sys.executable],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(0 if sys.version_info[:2] == (3, 9) else 2, result.returncode)
        if not result.returncode:
            self.assertEqual(list(sys.version_info[:3]), json.loads(result.stdout)['ci_python']['version'])

    def test_project_json_module_cannot_spoof_actual_ci_version(self):
        marker = self.root / 'json-imported'
        (self.root / 'json.py').write_text(
            'open(' + repr(str(marker)) + ', "w").close()\n'
            'def dumps(value):\n    return \'{"version": [3, 9, 25], "executable": "spoofed"}\'\n')
        result = subprocess.run([sys.executable, '-I', '-S', '-B', str(SCRIPT),
                                 '--project', str(self.root), '--check-ci-host',
                                 '--ci-python', sys.executable], cwd=self.root,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(0 if sys.version_info[:2] == (3, 9) else 2, result.returncode)
        self.assertFalse(marker.exists())
        if not result.returncode:
            self.assertEqual(list(sys.version_info[:3]), json.loads(result.stdout)['ci_python']['version'])

    def test_bad_or_missing_ci_executable_and_bad_version_payload_fail(self):
        for executable in ('python', str(self.root / 'missing-python')):
            status, _, error = self.invoke('--check-ci-host', '--ci-python', executable)
            self.assertEqual(2, status)
            self.assertIn('绝对路径', error)
        for result in (subprocess.CompletedProcess([], 1, '', 'failure'),
                       subprocess.CompletedProcess([], 0, 'not json', ''),
                       subprocess.CompletedProcess([], 0, '{"version": [2, true, 0]}', '')):
            with mock.patch.object(MODULE.subprocess, 'run', return_value=result):
                self.assertEqual(2, self.invoke('--check-ci-host', '--ci-python', sys.executable)[0])

    def test_project_constraints_are_reported_without_changing_mapping(self):
        (self.root / 'setup.cfg').write_text('[options]\npython_requires = >=3.10\n')
        (self.root / 'pyproject.toml').write_text('[project]\nrequires-python = ">=3.11"\n')
        result = MODULE.discover(self.root)
        self.assertEqual([3, 9], result['required_ci_version'])
        self.assertEqual('>=3.11', result['project_constraints']['pyproject.toml:project.requires-python'])

    def test_documented_gate_and_tox_use_the_same_ci_python(self):
        self.write_tox('python2')
        text = (SCRIPT.parent.parent / 'setup.md').read_text()
        block = next(value for value in re.findall(r'```bash\n(.*?)```', text, re.S)
                     if '--ci-python "$CI_PYTHON"' in value)
        block = block[block.index('"$AUX_PYTHON"'):]
        block = block.replace('<SKILL_DIR>', str(SCRIPT.parent.parent))
        block = block.replace('<PROJECT_ROOT>', str(self.root))
        ci = self.root / 'mock ci python'
        marker = self.root / 'mock-tox-called'
        shadow_modules = self.root / 'aux-shadow-modules'
        shadow_modules.mkdir()
        imported = self.root / 'aux-json-imported'
        (shadow_modules / 'json.py').write_text(
            'open(' + repr(str(imported)) + ', "w").close()\nraise RuntimeError("fixture json shadow")\n')
        for version, expected_status in (([2, 7, 18], 0), ([3, 9, 25], 1)):
            with self.subTest(version=version):
                if marker.exists():
                    marker.unlink()
                payload = '.'.join(map(str, version)) + '\n' + str(ci)
                ci.write_text('#!/bin/sh\nif [ "$1" = "-m" ]; then\n'
                              '  printf MOCK_TOX > ' + shlex.quote(str(marker)) + '\n'
                              '  exit 0\nfi\nprintf %s ' + shlex.quote(payload) + '\n')
                ci.chmod(0o700)
                environment = os.environ.copy()
                environment.update(AUX_PYTHON=sys.executable, CI_PYTHON=str(ci),
                                   PYTHONPATH=str(shadow_modules))
                result = subprocess.run(['bash', '-c', block], env=environment,
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(expected_status, result.returncode, result.stderr)
                self.assertEqual(expected_status == 0, marker.exists())
                self.assertFalse(imported.exists())

    def test_missing_tox_is_an_error(self):
        (self.root / 'tox.ini').unlink()
        with self.assertRaisesRegex(ValueError, 'tox.ini'):
            MODULE.discover(self.root)


if __name__ == '__main__':
    unittest.main()
