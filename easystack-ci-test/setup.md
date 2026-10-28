# Environment Setup

按本次执行的 `cover` / `pep8` 及其继承配置读取 tox.ini 的明确 Python major:
**2 -> CI Python 2.7, 3 -> CI Python 3.9**。未知、动态引用或多个 major 冲突时报告来源并
停止, 不默认选择 3.9。保留 tox 显式 minor 目标和项目约束另行核验, 不擅改 tox.ini。

## Separate Interpreters 分离解释器

辅助脚本使用独立 Python 3; tox/CI 使用按 major 选择并激活的 CI 解释器。Python 2.7
不能直接执行本 skill 使用 pathlib/configparser 的 Python 3 辅助脚本。
激活 CI 环境前固定已核实的辅助解释器绝对路径, 后续不依赖切换后的 PATH:
`AUX_PYTHON` / `CI_PYTHON` 须在同一 shell 上下文使用, 或每次命令显式复用已核实的
绝对路径; 不假设不同 Agent 工具调用会保留变量或 conda 激活状态。

```bash
AUX_PYTHON=$(command -v python3)
case "$AUX_PYTHON" in
    /*) ;;
    *) echo '请提供已存在的辅助 Python 3 绝对路径' >&2; return 1 2>/dev/null || exit 1 ;;
esac
"$AUX_PYTHON" -I -S -B -c 'import sys; assert sys.version_info[0] == 3' || {
    echo '辅助解释器不是 Python 3, 停止准备 CI' >&2
    return 1 2>/dev/null || exit 1
}
```

辅助 Python 不决定 CI 版本。没有可用 Python 3 辅助工具或映射出的 CI 环境时报告缺项,
不自动安装, 不用另一版本代替。辅助入口统一使用 `-I -S -B`, 避免项目路径、PYTHONPATH
和 site 配置影响标准库导入, 不生成字节码; 不将 Python 3 的 `-I` 传给 CI 2.7。

## Discover Constraints 发现约束

从被测仓库根读取 tox.ini 的 envlist、basepython、commands、requires、constraints,
以及 setup.cfg / pyproject.toml 中的要求。先只读发现:

```bash
"$AUX_PYTHON" -I -S -B "<SKILL_DIR>/scripts/discover-python.py" --project "<PROJECT_ROOT>"
```

默认检查 cover 与 pep8; 本轮只执行其中一个时, 两次发现/门禁调用均加同一
`--env cover` 或 `--env pep8`。环境覆盖配置优先于 `[testenv]` 继承值。
`required_ci_version` 来自明确 major 的映射; `auxiliary_python` 只是辅助解释器。
未提供 `--ci-python` 时 `ready_for_ci=false`, 不代表已核实 CI 环境。
`ready_for_ci=true` 仅表示映射后的实际 CI 解释器版本门禁通过, 不代表 tox 目标解释器、
依赖或全部执行条件已准备完成; `target_notes` 和原项目约束仍须另行核验。

缺失、条件因子、变量引用或多 major 冲突会以非零退出并报告, 不从未选环境推断。
需要解析复杂 tox 配置时, 使用已安装版本实际支持的配置查看入口, 或取得已确认的解析
结果再继续; 不猜测参数或覆盖环境变量强行选择。显式目标如 python3.11 仍原样记录,
CI 按 major 映射为 3.9, 目标解释器及项目约束是否满足须另行核验。

## Activate And Check 激活与门禁

先定位实际 Miniconda 安装, 查看已有环境清单, 选择经核实的项目环境, 例如
`easystack-<project>-py27` 或 `easystack-<project>-py39`。名称不能代替真实版本检查。
缺少环境或兼容 tox 时报告缺项与影响, 按授权处理, 不改用另一版本继续。

```bash
source <CONFIRMED_MINICONDA_BASE>/etc/profile.d/conda.sh
conda env list
conda activate <CONFIRMED_CI_ENV>
CI_PYTHON=$(command -v python)
"$AUX_PYTHON" -I -S -B "<SKILL_DIR>/scripts/discover-python.py" --project "<PROJECT_ROOT>" \
    --ci-python "$CI_PYTHON" --check-ci-host || {
    echo 'CI 版本或配置门禁未通过, 不继续运行 tox' >&2
    return 1 2>/dev/null || exit 1
}
"$CI_PYTHON" -m tox --version
```

`--ci-python` 必须是实际 CI 解释器的绝对路径。辅助脚本通过无 shell 的 argv 调用它,
仅执行 Python 2.7/3 兼容的只读版本查询; 未指定、查询失败或实际版本不符合映射要求时
拒绝门禁。它不执行 tox、不创建环境, 不把辅助进程自身版本冒充 CI 版本。

核实该 CI 解释器下已安装的 tox 与目标环境兼容, 再检查实际解析与执行输出。条件
仍未解析、minor/项目约束或目标解释器存在未解决缺口时停止相关 CI 并报告, 不修改
配置或安装依赖制造通过。使用 `"$CI_PYTHON" -m tox` 执行完整 CI。

## Coverage Tools 覆盖率辅助工具

完整 diff 覆盖检查始终由固定的 `AUX_PYTHON` 执行, 可以读取 CI 2.7 环境产出的报告。
先核对现有 coverage 的报告能力; JSON/分支结构不支持时按 [coverage.md](coverage.md)
人工核验并记录缺口, 不为辅助脚本升级 tox/coverage。所有新增/修改可执行行及分支的
要求不变, 包括确认范围内未跟踪源码; 未改历史缺口仍为 baseline。
