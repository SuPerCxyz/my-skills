## 1. Inventory and invocation updates

- [x] 1.1 Replace direct local shell-script calls in skill tests and helper scripts with `bash <path> ...`.
- [x] 1.2 Normalize documented local Python entrypoint commands to `python3 <path> ...` and add explicit interpreter guidance where needed.
- [x] 1.3 Update shell-script references that are written as executable commands, while preserving source, remote, and Kubernetes command semantics.

## 2. Contract enforcement

- [x] 2.1 Remove direct `env-access.sh` from the `easystack-test-executor` executable allowlist.
- [x] 2.2 Update the environment-access normalization rule and add regression coverage for accepted Bash-wrapped and rejected direct forms.

## 3. Verification

- [x] 3.1 Run syntax checks and relevant shell/Python tests through explicit interpreters.
- [x] 3.2 Re-scan skill docs and scripts for direct local `.sh` or `.py` entrypoint execution, inspect remaining matches, and verify no unrelated files changed.
