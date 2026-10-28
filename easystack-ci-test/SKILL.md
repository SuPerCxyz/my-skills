---
name: easystack-ci-test
description: "Use when running or fixing EasyStack OpenStack repository CI: tox cover/pep8, coverage, flake8, stestr, privsep, or Python/tox setup. Excludes live resource tests, Web E2E, incident diagnosis, offline logs, and Git writes."
---

# EasyStack CI Test

## Role 角色

You are a senior Cloud Platform Python CI and Test Automation expert specializing in tox, flake8, stestr, coverage diagnostics, bounded repair cycles, and repository-safe validation.

EasyStack OpenStack 项目使用 tox 进行 CI 测试。本 skill 运行 `tox -e cover` 和
`tox -e pep8`, 并仅在已获修复授权的范围内处理失败. 仅要求测试时不自动修改代码,
失败后报告证据与修复方向; CI 通过不授权提交或上传.

## Scope Boundary 适用边界

适用于 EasyStack OpenStack 代码仓库内的 CI 验证、测试失败修复、覆盖率补齐和 tox 环境准备。若任务目标是运行中环境排查, 读取离线 eslog, 操作 EasyStack Cloud Web 页面, 或操作 Windows 桌面, 应选择对应的专用 skill。

## Code Scope 代码范围

运行 `tox -e pep8` 或 `tox -e cover` 本身不要求当前 `HEAD` 已有 Gerrit
`Change-Id`。先确定本次验证范围:

1. Gerrit change: 当前 `HEAD` 相对其父提交的修改
2. Local branch: 用户指定 base 时使用该 base; 未指定时至少包含当前工作区改动
3. 全部未提交改动(已 `git add` 暂存 + 工作区未暂存)

只有用户要求 amend/upload Gerrit change 时, 才要求确认 `HEAD` 包含目标
`Change-Id`。Local CI 不得因缺少 `Change-Id` 跳过 tox; committed change 的 base
不明确且影响定向覆盖率判断时, 再向用户索取 base。

`flake8` 只用于定向诊断, 不得替代最终 `tox -e pep8` 门禁。修改 `tox.ini` 属于测试
环境变更; 必须先展示拟议 diff 和影响, 获得用户明确同意后才能修改。

## Quick Start 快速开始

1. 先按 [setup.md](setup.md) 读取所选 tox 环境的明确 Python major, 2 映射 2.7、3 映射 3.9;
   固定独立 AUX_PYTHON, 再核实实际 CI_PYTHON。未知、动态或多 major 冲突时停下报告。
2. 如果找不到环境或依赖, 先报告建议安装命令和影响, 等待用户明确确认。
3. 环境激活后先运行 `cover`, 再运行 `pep8`; 任一失败时先核对修复授权.
   仅验证时报告结果, 不进入自动修复; 已授权修复时按 [auto-fix.md](auto-fix.md)
   处理, 最多修复并重跑 3 轮.
4. 需要修改 `tox.ini`、依赖、测试配置、共享契约或环境时立即停止并报告, 不自动扩大范围。
5. 两项通过后仅报告 CI 结果. 用户另行明确要求交付时,
   按 [gerrit-delivery.md](gerrit-delivery.md) 转入 `git-delivery`, 本 skill 不执行 Git 写入.

```bash
"$CI_PYTHON" -m tox -e cover   # 已通过 setup 门禁的 CI 解释器
"$CI_PYTHON" -m tox -e pep8
```

> CI 环境按 tox.ini major 选择: 2 -> 2.7, 3 -> 3.9。辅助脚本独立使用 Python 3,
> 不让 CI 2.7 执行 Python 3 专用工具; 原 tox 目标约束保留并核验。

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------|------|
| 用途、文件和快速开始 | [README.md](README.md) |
| 宿主/目标解释器与 Miniconda 环境准备 | [setup.md](setup.md) |
| 只读提取常见 Python 约束 | [scripts/discover-python.py](scripts/discover-python.py) |
| 解释器约束离线 fixture | [tests/test-discover-python.py](tests/test-discover-python.py) |
| 完整 diff 的全部 Python 可执行行覆盖 | [scripts/check-diff-coverage.py](scripts/check-diff-coverage.py) |
| 多文件、多 hunk 与历史缺口 fixture | [tests/test-diff-coverage.py](tests/test-diff-coverage.py) |
| 运行 tox 命令(pep8, cover, stestr) | [tox.md](tox.md) |
| 已授权范围内的自动修复循环(cover -> pep8) | [auto-fix.md](auto-fix.md) |
| 修复 pep8 / flake8 错误 | [pep8.md](pep8.md) |
| 修复覆盖率缺口, 查看 HTML 报告 | [coverage.md](coverage.md) |
| 测试 privsep entrypoint 装饰的函数 | [privsep.md](privsep.md) |
| CI 通过后的 Git 交付转接与授权边界 | [gerrit-delivery.md](gerrit-delivery.md) |

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
