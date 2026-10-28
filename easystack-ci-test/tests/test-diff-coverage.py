"""完整 diff fixture 覆盖多文件、多 hunk、历史缺口、删除和注释。"""

import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    'diff_coverage', Path(__file__).parents[1] / 'scripts' / 'check-diff-coverage.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

DIFF = '''--- a/a.py
+++ b/a.py
@@ -1,0 +2,2 @@
+first = 1
+# comment
@@ -8 +10 @@
-old = 0
+second = 2
--- a/with space.py
+++ b/with space.py
@@ -0,0 +1 @@
+third = 3
'''


class DiffCoverageTests(unittest.TestCase):
    def coverage(self, files):
        for entry in files.values():
            for key in ('executed_lines', 'missing_lines', 'missing_branches'):
                entry.setdefault(key, [])
        return {'meta': {'branch_coverage': True}, 'files': files}

    def test_all_files_and_hunks_are_checked(self):
        report = self.coverage({
            'a.py': {'executed_lines': [2], 'missing_lines': [10, 99]},
            'with space.py': {'executed_lines': [], 'missing_lines': [1]},
        })
        result = MODULE.check(DIFF, report)
        self.assertEqual(3, result['checked_executable_lines'])
        self.assertEqual(['a.py', 'with space.py'], [v['file'] for v in result['failures']])
        self.assertEqual([10], result['failures'][0]['uncovered_lines'])

    def test_history_and_comment_do_not_inflate_scope(self):
        report = self.coverage({
            'a.py': {'executed_lines': [2, 10], 'missing_lines': [99]},
            'with space.py': {'executed_lines': [1], 'missing_lines': []},
        })
        self.assertEqual([], MODULE.check(DIFF, report)['failures'])

    def test_changed_branch_and_exclusion_fail(self):
        diff = '+++ b/a.py\n@@ -1 +1 @@\n-old\n+new\n'
        for fields in ({'executed_lines': [1], 'missing_branches': [[1, 9]]},
                       {'excluded_lines': [1]}):
            result = MODULE.check(diff, self.coverage({'a.py': fields}))
            self.assertTrue(result['failures'])

    def test_missing_report_is_not_success(self):
        self.assertEqual(2, len(MODULE.check(DIFF, self.coverage({}))['failures']))

    def test_deletion_does_not_create_executable_lines(self):
        diff = '+++ /dev/null\n@@ -1 +0,0 @@\n-only_deleted\n'
        self.assertEqual({}, MODULE.added_lines(diff))

    def test_untracked_new_file_checks_all_executable_lines(self):
        diff = '--- /dev/null\n+++ b/new.py\n@@ -0,0 +1,4 @@\n+first = 1\n+# comment\n+second = 2\n+third = 3\n'
        report = self.coverage({'new.py': {'executed_lines': [1, 4], 'missing_lines': [3]}})
        result = MODULE.check(diff, report)
        self.assertEqual(3, result['checked_executable_lines'])
        self.assertEqual([3], result['failures'][0]['uncovered_lines'])
        self.assertEqual('new.py', MODULE.check(diff, self.coverage({}))['failures'][0]['file'])

    def test_missing_branch_measurement_and_fields_cannot_pass(self):
        diff = '+++ b/a.py\n@@ -0,0 +1 @@\n+x = 1\n'
        report = self.coverage({'a.py': {'executed_lines': [1]}})
        report['meta']['branch_coverage'] = False
        self.assertTrue(MODULE.check(diff, report)['failures'])
        with self.assertRaisesRegex(ValueError, 'executed_lines'):
            MODULE.check(diff, {'files': {'a.py': {}}})

    def test_malformed_or_multiple_versions_are_rejected(self):
        for diff in ('not a diff', '+++ b/a.py\n@@ -0,0 +1,2 @@\n+x = 1\n',
                     '+++ b/a.py\n@@ -0,0 +1 @@\n+x = 1\n+++ b/a.py\n',
                     '+++ b/a.py\n@@@ -1,1 -1,1 +1,1 @@@\n++x = 1\n',
                     '+++ b/a.py\n',
                     '+++ b/a.py\n@@ -0,0 +1 @@\n+x = 1\n+++ b/unparsed.py\n'):
            with self.subTest(diff=diff):
                with self.assertRaises(ValueError):
                    MODULE.added_lines(diff)

    def test_source_line_looking_like_header_is_still_hunk_content(self):
        diff = '+++ b/a.py\n@@ -0,0 +1 @@\n+++ value\n'
        self.assertEqual({'a.py': {1}}, MODULE.added_lines(diff))


if __name__ == '__main__':
    unittest.main()
