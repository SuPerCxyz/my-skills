## Why

多个 skill 的脚本文件可能以没有执行位的形式同步或安装。文档、测试和执行合约若直接调用脚本路径, 会因权限位缺失失败; 使用显式解释器可以让调用方式在不同同步环境中保持一致。

## What Changes

- 所有 skill 中本地 `.sh` 脚本的文档、测试和脚本间调用统一使用 `bash <path> ...`。
- 所有 skill 中本地 `.py` 入口的手工命令统一使用 `python3 <path> ...`; 已使用 `sys.executable` 的内部调度保持不变。
- `easystack-test-executor` 的 `env_access` 合约只接受 `bash <path>/env-access.sh ...`, 禁止直接执行脚本路径。
- 保留 `source` 库脚本、远程 `bash -s`、Kubernetes 容器启动命令和历史设计文档的原有语义。

## Capabilities

### New Capabilities

- `explicit-script-execution`: 定义 skill 本地脚本的显式解释器调用规范。

### Modified Capabilities

无。

## Impact

- 影响各 skill 的执行示例、回归测试和脚本间调用。
- 影响 `easystack-test-executor` 的 action executable allowlist 及对应合约测试。
- 不引入依赖, 不改变脚本业务逻辑, 不修改文件执行权限。
