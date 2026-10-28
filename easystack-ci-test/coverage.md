# Fixing Coverage Gaps

Use this file when `tox -e cover` reports missing coverage or test failures related to the current change set. For command order and the full repair loop, start from [auto-fix.md](auto-fix.md).

## Scope 覆盖范围

覆盖报告可以包含整个项目, 本次门禁只检查已确认 diff 中新增或修改的可执行行及其
分支。touched file 中无关历史缺口记录为 baseline, 不因此扩展修改范围。
基线沿用 [SKILL.md](SKILL.md#code-scope-代码范围): Gerrit 使用确认的提交父节点,
本地分支使用用户确认的 base, 另合并 staged 与 unstaged 改动。

必须覆盖确认范围内**所有文件、所有 hunk 的全部新增/修改可执行行**。为避免 staged
和 unstaged 的行号错位, 最终使用确认基线到当前工作树的一份合并 diff, 而不是分别
解析三个版本后直接合并行号。先完整核对文件清单, 不选取部分文件代替完整范围:

```bash
# BASE 是已确认的 Gerrit HEAD 父节点或本地 base; 包含 committed、staged、unstaged
git diff --no-ext-diff --unified=0 <BASE> -- <CONFIRMED_SCOPE>
```

上述 diff 不含未跟踪文件。必须另用只读清单核对确认范围内的新源码, 不为生成报告擅自
`git add`。每个未跟踪文件按最终内容生成全新增 diff, 例如:

以下命令从被测仓库根执行, 新源码使用仓库相对路径, 与 coverage JSON 的文件名核对一致。

```bash
git ls-files --others --exclude-standard -- <CONFIRMED_SCOPE>
git diff --no-index --no-ext-diff --unified=0 -- /dev/null <UNTRACKED_SOURCE_FILE>
```

`git diff --no-index` 的 exit 1 表示存在差异, exit 0 表示无差异; 其他退出码才是失败。
安全保存每份 diff 并核对清单, 对未纳入或不支持的源码明确标记未验证, 不声称覆盖全部。
不要直接依赖 `set -e` 将正常的 exit 1 误作收集失败, 也不要用 `|| true` 隐藏真实错误。

将完整输出保存到本次结果路径, 用 [setup.md](setup.md) 在激活 CI 环境前固定的
独立 Python 3 辅助解释器, 检查与最终代码匹配的 coverage JSON。不要用 CI 2.7 运行该脚本:

```bash
"$AUX_PYTHON" -I -S -B "<SKILL_DIR>/scripts/check-diff-coverage.py" \
  --diff <FULL_TRACKED_FINAL_DIFF> --diff <UNTRACKED_FILE_DIFF> --coverage <COVERAGE_JSON>
```

没有未跟踪源码时省略第二个 `--diff`。同一文件只提供一份最终版本 diff, 不将 staged
和 unstaged 两个不同版本重复输入。分支未测量、报告字段缺失或不支持的 diff 格式会
报告失败, 不能以没有记录推定没有 `mis/par`。

该辅助检查覆盖 Python 文件, 根据 coverage 的可执行行与分支信息计算交集, 注释和
删除行不当作新增可执行行。缺少修改文件的报告会失败; 修改行的排除项不得静默跳过。
非 Python 执行代码、特殊 diff 格式或无法生成 JSON 的旧 coverage 仍需明确人工核验,
辅助脚本成功不等于全部项目和业务验收通过。

```bash
# List all modified files: current HEAD + uncommitted changes
git diff HEAD^ --name-only    # files changed in the current Gerrit change
git diff --name-only          # unstaged changes
git diff --cached --name-only # staged but not committed changes
```

先确认 HEAD 有父提交且属于本次 Gerrit change, 才使用上述 HEAD^ 示例。本地分支改用
`git diff <BASE>...HEAD --name-only`, 再合并未提交差异。用对应的 `--unified=0` diff
确定新增/修改行号, 不把文件列表误作行覆盖范围。纯删除行没有新的可执行行, 但相关
行为回归仍按风险执行。无 Change-Id 不阻止本地 CI; committed base 不明确时说明
定向覆盖率判断限制, 不猜测基线。

## Find Uncovered Lines 定位覆盖缺口

先从实际 tox/coverage 输出定位报告, 不假设一定是 `cover/`。支持 JSON report 的版本
可读取实际报告的 `files`、`executed_lines`、`missing_lines` 和分支信息, 再与 diff
行号求交集。生成报告前核对该版本 help 及已有输出, 不覆盖用户文件。
HTML 文件名可能采用以下布局, 以实际索引为准:

| File path | status.json key |
|-----------|-----------------|
| `cinder/privsep/cgroup.py` | `cinder_privsep_cgroup_py` |
| `cinder/volume/throttling.py` | `cinder_volume_throttling_py` |
| `cinder/tests/unit/test_cgroup.py` | `cinder_tests_unit_test_cgroup_py` |

`cover/status.json` 是 coverage 的内部缓存格式, 不依赖 `nums` 的固定位置解析。

## HTML Missing Lines 页面缺口

```bash
# Missing lines (never executed)
grep 'class="mis' cover/cinder_privsep_cgroup_py.html | grep -o 'id="t[0-9]*"' | grep -o '[0-9]*'

# Partially covered lines (some branches not taken)
grep 'class="par' cover/cinder_privsep_cgroup_py.html | grep -o 'id="t[0-9]*"' | grep -o '[0-9]*'
```

## Error Paths 异常路径

100% coverage requires testing **error paths**, not just the happy path:

- **`except` branches** - mock with `side_effect=OSError` or similar to trigger exception handlers
- **`partial` (par) lines** - both sides of an `if` condition must be exercised. If only the `true` branch runs, the `false` branch is partial. Write a separate test that flips the condition.

Example:

```python
def test_cgroup_limit_v2_os_error(self):
    with mock.patch.object(cgroup.os.path, 'isfile', return_value=True):
        with mock.patch('builtins.open',
                        side_effect=OSError('perm denied')):
            self.assertRaises(
                processutils.ProcessExecutionError,
                cgroup.cgroup_limit, 'mygroup', 'read', '253:0', 1024)
```

## Multiple File Reads 多文件模拟

`mock_open(read_data=...)` returns the same content for every file opened.
When the code opens multiple files expecting different content, use a custom function:

```python
def fake_open(path, mode='r', *args, **kwargs):
    file_map = {
        '/path/to/file_a.conf': mock.mock_open(read_data='content_a')(),
        '/path/to/file_b.conf': mock.mock_open(read_data='content_b')(),
    }
    return file_map.get(path, mock.mock_open()())

with mock.patch('builtins.open', fake_open):
    # code that opens file_a and file_b gets different content
```

## Targeted Unit Tests 定向测试

Write tests that cover the specific uncovered branches. See [privsep.md](privsep.md) for testing privsep-decorated functions.

## After Fixing 修复后验证

Re-run `tox -e cover` to verify. Once coverage is clean, run `tox -e pep8` to verify
lint. A direct `flake8` run may isolate an error, but cannot replace the tox gate.
