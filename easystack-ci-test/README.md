# EasyStack CI 测试

运行 EasyStack OpenStack 仓库 CI, 在授权范围内定向修复失败。需要 Git 交付时转交
专用交付能力, 本 skill 不执行 commit、amend 或上传。

## Features 功能

- `tox -e cover` 覆盖率检查
- `tox -e pep8` flake8 代码风格检查
- CI 环境按 tox.ini major 映射 2 -> 2.7、3 -> 3.9, 未知/动态/冲突时停下报告
- 辅助 Python 3 与实际 CI 解释器分离, 保留 tox 显式目标约束核验
- `flake8` 只用于诊断, 最终必须通过 tox; 修改 `tox.ini` 前需用户明确同意
- 自动修复循环:cover -> pep8 -> 定向修复, 达到停止条件时报告阻塞
- 覆盖率缺口修复指导
- privsep 函数测试处理
- CI 通过后按实际授权转交 Git 交付, 不从测试权限推导上传权限

## Quick Start 快速开始

先按 [setup.md](setup.md) 激活 Miniconda 环境。缺少环境或依赖时, 获得用户确认后
再安装。环境已激活后运行:

```bash
"$CI_PYTHON" -m tox -e cover   # 已通过 setup 门禁
"$CI_PYTHON" -m tox -e pep8
```

任一失败后按 [自动修复循环](auto-fix.md) 工作流处理。两项通过且用户明确要求上传
时, 再按 [Gerrit 续提交流程](gerrit-delivery.md) 更新当前 change。

## Files 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口,快速参考 |
| [setup.md](setup.md) | 宿主/目标解释器约束及已有 Miniconda 环境发现 |
| [scripts/discover-python.py](scripts/discover-python.py) | 读取 tox major 并核验指定 CI 解释器, 与辅助 Python 分离 |
| [tests/test-discover-python.py](tests/test-discover-python.py) | Python 2/3、minor、条件配置和缺项离线 fixture |
| [scripts/check-diff-coverage.py](scripts/check-diff-coverage.py) | 确认范围全部修改 Python 可执行行与分支检查 |
| [tests/test-diff-coverage.py](tests/test-diff-coverage.py) | 多文件、多 hunk、历史缺口、删除和注释 fixture |
| [tox.md](tox.md) | tox 命令参考(pep8、cover、stestr) |
| [pep8.md](pep8.md) | pep8/flake8 错误修复指南 |
| [coverage.md](coverage.md) | 覆盖率修复与 HTML 报告查看 |
| [auto-fix.md](auto-fix.md) | 自动修复循环工作流(cover → pep8 循环直到通过) |
| [privsep.md](privsep.md) | privsep entrypoint-decorated 函数测试指南 |
| [gerrit-delivery.md](gerrit-delivery.md) | CI 结束后的交付转接与授权边界 |
