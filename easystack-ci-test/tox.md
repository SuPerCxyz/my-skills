# Running tox Commands

Use this file for the exact tox entry points after the Miniconda environment is active. If a command fails, switch to [auto-fix.md](auto-fix.md) rather than inventing a new loop.

> ⚠ **Must activate the Miniconda environment first.** Do not run `tox` directly - it
> may use the wrong Python or miss dependencies. Follow [setup.md](setup.md) to
> activate the confirmed project host environment first; verify each tox target separately.
>
> Miniconda is the distribution; `conda` is its CLI tool - so `conda activate` is the correct command:
> ```bash
> source /path/to/miniconda3/etc/profile.d/conda.sh
> conda activate easystack-<project>-py<version>
> ```

完整 tox 门禁先按 [setup.md](setup.md) 从所选 tox 环境映射 CI Python 2.7/3.9,
用独立 AUX_PYTHON 核对实际 CI_PYTHON。诊断时激活过目标 venv 后, 必须重新激活
已选 CI 环境、更新 CI_PYTHON 并重过门禁; 不沿用 PATH 里的另一解释器。

## pep8 Check 风格检查

```bash
# Activate Miniconda env first, then run tox
source <CONFIRMED_MINICONDA_BASE>/etc/profile.d/conda.sh
conda activate <CONFIRMED_CI_ENV>
# 重新取得 CI_PYTHON 并通过 setup.md 门禁后
"$CI_PYTHON" -m tox -e pep8
```

## Coverage Testing 覆盖率测试

```bash
# Activate Miniconda env first, then run tox
source <CONFIRMED_MINICONDA_BASE>/etc/profile.d/conda.sh
conda activate <CONFIRMED_CI_ENV>
# 重新取得 CI_PYTHON 并通过 setup.md 门禁后
"$CI_PYTHON" -m tox -e cover
```

## Running Individual Tests 单项测试

Useful for debugging during the fix loop:

```bash
. .tox/cover/bin/activate && stestr run <test_pattern>
```

Examples:

```bash
stestr run test_image_utils
stestr run privsep.test_cgroup
stestr run test_volume_utils.CopyVolumeTestCase.test_copy_volume_with_on_execute
```

## Isolate flake8 Errors 定位风格错误

```bash
. .tox/pep8/bin/activate && flake8 path/to/file.py
```

## External Commands 外部命令约束

If `tox -e pep8` fails with `is not allowed, use allowlist_externals`, treat it as a
tox configuration blocker. `flake8 .` may be used only to diagnose source lint errors;
it never replaces the final `tox -e pep8` gate.

Changing `tox.ini`, including adding `allowlist_externals`, changes the project test
environment. Show the exact proposed diff and impact, then wait for explicit user
approval before editing it. Without approval, stop and report the blocker. Do not mark
pep8 or the overall task as passed.
