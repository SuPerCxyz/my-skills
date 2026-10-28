# Fixing pep8 Errors

Use this file when `tox -e pep8`, flake8, or a direct pep8 environment run reports style errors. It is only the pep8 repair reference; use [auto-fix.md](auto-fix.md) for the full cover/pep8 loop.

## Find Errors 定位错误

```bash
. .tox/pep8/bin/activate && flake8 path/to/file.py
```

Refer to the flake8 output for exact error codes and line numbers. Fix each reported issue (line length, import order, docstring formatting, etc.).

## After Fixing 修复后验证

Re-run `tox -e pep8` to verify. New errors may appear - fix those too. See the [auto-fix loop](auto-fix.md) for the full cycle.
