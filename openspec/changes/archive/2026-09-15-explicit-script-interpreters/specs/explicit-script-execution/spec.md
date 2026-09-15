## Purpose

为 skill 的本地脚本提供不依赖文件执行权限的统一调用方式, 确保同步或安装后仍可稳定执行并让调用方契约保持可验证。

## ADDED Requirements

### Requirement: Local shell scripts use an explicit Bash interpreter

Skill documentation, tests and local helper scripts MUST invoke local `.sh` entrypoints through `bash <path> ...` rather than relying on a direct executable path.

#### Scenario: Shell script has no executable bit

- **WHEN** a local skill `.sh` file is invoked from a documented command or regression test without the executable bit
- **THEN** the invocation uses `bash <path> ...` and does not fail because of the file mode

### Requirement: Local Python entrypoints use an explicit Python interpreter

Skill documentation and manual execution examples MUST invoke local `.py` entrypoints through `python3 <path> ...` or an equivalent explicit interpreter selected by the runtime, rather than relying on the shebang executable bit.

#### Scenario: Python entrypoint is not executable

- **WHEN** a local skill `.py` entrypoint is invoked from a documented command
- **THEN** the command supplies `python3` or another explicit interpreter before the script path

### Requirement: Environment access actions use Bash

An `env_access` execution action MUST use `bash <path>/env-access.sh ...`; a direct `env-access.sh` executable is not a valid action command.

#### Scenario: Bash-wrapped environment access action

- **WHEN** an `env_access` action starts with `bash` and its next argument is `env-access.sh`
- **THEN** the action passes executable validation

#### Scenario: Direct environment access script action

- **WHEN** an `env_access` action starts directly with `env-access.sh`
- **THEN** the action is rejected by executable validation
