# Feature Parity

证据驱动的功能对齐与复刻 skill: 将参考项目视为可执行行为规范, 在目标项目中复现其可观察功能与行为, 而非表面相似。

## 功能列表

- 参考/目标仓库 revision 冻结与范围界定 (Phase 0)
- 参考项目侦察与注册面扫描 (Phase 1)
- 功能树递归分解到原子可测试叶子 `F-001.1a` (Phase 2)
- 证据图与 parity matrix 全流程追踪 (Phase 3)
- 三阶段门禁: Gate A (证据齐全才开工) / Gate B (代码存在不等于完成) / Gate C (无未解释缺口)
- 差分黑盒优先的行为验证与逆向遗漏审计 (Phase 6-7)
- Compact / Full 双执行模式, 支持并行子代理发现
- `parity_audit.py` 矩阵结构审计

## 文件说明

| 需要做什么 | 阅读 |
|------------|------|
| 范围 / revision / 证据层级定义 | [references/00-scope-and-evidence.md](references/00-scope-and-evidence.md) |
| 参考项目侦察与注册面扫描 | [references/01-discovery.md](references/01-discovery.md) |
| 功能分解与原子叶子测试 | [references/02-feature-decomposition.md](references/02-feature-decomposition.md) |
| parity matrix 状态语义与不变量 | [references/03-parity-matrix.md](references/03-parity-matrix.md) |
| 实施纪律与避免假对齐 | [references/04-implementation.md](references/04-implementation.md) |
| 行为验证方法 | [references/05-verification.md](references/05-verification.md) |
| UI 对齐维度 | [references/06-ui-parity.md](references/06-ui-parity.md) |
| 子代理编排规则 | [references/07-subagent-orchestration.md](references/07-subagent-orchestration.md) |
| 产物模板 | [templates/](templates/) |
| 矩阵结构审计脚本 | [scripts/parity_audit.py](scripts/parity_audit.py) |

## 快速开始

1. 冻结参考与目标仓库 revision, 确认范围与 parity 维度 (Phase 0)
2. 侦察参考项目表面, 递归建立功能树 (Phase 1-2)
3. 建立 EVIDENCE_MAP 与 PARITY_MATRIX, 通过 Gate A (Phase 3)
4. 按纵向切片实现, 逐片更新证据与状态, 通过 Gate B (Phase 4-5)
5. 差分 / 黑盒验证, 逆向遗漏审计, 通过 Gate C 后出具报告 (Phase 6-8)

每次更新 `PARITY_MATRIX.md` 后运行:

```bash
python3 scripts/parity_audit.py <matrix-path>
```

仅在退出码为 0 时继续下一阶段; 非 0 先修复矩阵再重跑。
