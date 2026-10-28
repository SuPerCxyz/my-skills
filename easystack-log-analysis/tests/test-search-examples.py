"""执行真实检索脚本与文档命令片段, 不访问环境。"""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SEARCH = ROOT / 'scripts' / 'search-logs.py'


class SearchExamplesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.log = self.root / 'ecs.node-1.20261027.0/openstack/nova/nova-compute.node-1.log'
        self.log.parent.mkdir(parents=True)
        self.log.write_text('vm-123 instance-00000001\nother instance-00000002\n', encoding='utf-8')

    def search(self, *extra):
        return subprocess.run([sys.executable, str(SEARCH), '--root', str(self.root),
                               *extra], input='', text=True, capture_output=True, timeout=5)

    def test_literal_uuid_search_is_bounded_to_matching_lines(self):
        result = self.search('--pattern', 'ecs.*/openstack/nova/*.log', '--text', 'vm-123')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('instance-00000001', result.stdout)
        self.assertNotIn('instance-00000002', result.stdout)

    def test_missing_files_and_no_hit_are_distinct(self):
        missing = self.search('--pattern', 'ecs.*/absent/*.log', '--text', 'vm-123')
        no_hit = self.search('--pattern', 'ecs.*/openstack/nova/*.log', '--text', 'missing')
        self.assertEqual(2, missing.returncode)
        self.assertEqual(1, no_hit.returncode)
        self.assertIn('输入/采集缺口', missing.stderr)
        self.assertIn('未命中', no_hit.stderr)

    def test_spaces_in_paths_and_output_limit(self):
        path = self.log.with_name('with space.log')
        path.write_text('vm-123\nvm-123\n', encoding='utf-8')
        result = self.search('--pattern', 'ecs.*/openstack/nova/with space.log',
                             '--text', 'vm-123', '--limit', '1')
        self.assertEqual(3, result.returncode)
        self.assertEqual(1, len(result.stdout.splitlines()))
        self.assertIn('上限', result.stderr)

    def test_component_view_is_not_an_authoritative_input(self):
        path = self.root / 'components/nova.log'
        path.parent.mkdir()
        path.write_text('vm-123\n', encoding='utf-8')
        self.assertEqual(2, self.search('--pattern', 'components/*.log', '--text', 'vm-123').returncode)

    def test_symlink_cannot_disguise_component_view_as_node_source(self):
        copy = self.root / 'components/copy.log'
        copy.parent.mkdir()
        copy.write_text('vm-123\n', encoding='utf-8')
        link = self.log.with_name('disguised.log')
        link.symlink_to(copy)
        result = self.search('--pattern', 'ecs.*/openstack/nova/disguised.log', '--text', 'vm-123')
        self.assertEqual(2, result.returncode)
        self.assertIn('来源不是 ecs.*', result.stderr)

    def test_single_long_line_respects_byte_budget(self):
        self.log.write_text('vm-123 ' + '数' * 30000 + '\n', encoding='utf-8')
        result = self.search('--pattern', 'ecs.*/openstack/nova/*.log', '--text', 'vm-123',
                             '--max-bytes', '1024')
        self.assertEqual(3, result.returncode)
        self.assertLessEqual(len(result.stdout.encode('utf-8')), 1024)
        self.assertIn('.log:1:', result.stdout)
        self.assertIn('未完整展示', result.stderr)

    def test_invalid_regex_and_escape_fail(self):
        for extra in [('--pattern', '../*.log', '--text', 'x'),
                      ('--pattern', '**/*.log', '--regex', '[')]:
            self.assertEqual(2, self.search(*extra).returncode)

    def test_documented_boot_expression_matches_real_alternatives(self):
        text = (ROOT / 'search-patterns.md').read_text(encoding='utf-8')
        command = next(line for line in text.splitlines()
                       if line.startswith('grep -E "Reached target'))
        expression = re.search(r'grep -E "([^"]+)"', command).group(1)
        result = subprocess.run(['grep', '-E', expression],
                                input='Reached target Multi-User\nReached target Graphical\n',
                                text=True, capture_output=True, timeout=5)
        self.assertEqual(0, result.returncode)
        self.assertEqual(2, len(result.stdout.splitlines()))

    def test_documented_chrony_glob_finds_fixture(self):
        path = self.root / 'ecs.node-1.20261027.0/os/chrony.node-1.log'
        path.parent.mkdir()
        path.write_text('system clock offset\n', encoding='utf-8')
        text = (ROOT / 'search-patterns.md').read_text(encoding='utf-8')
        command = next(line.strip() for line in text.splitlines()
                       if 'grep -i "system clock"' in line)
        result = subprocess.run(['bash', '-c', 'set -o pipefail; d="$1"; ' + command,
                                 'fixture', str(path.parent.parent)],
                                text=True, capture_output=True, timeout=5)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('system clock offset', result.stdout)


if __name__ == '__main__':
    unittest.main()
