---
name: feature-parity
description: "Use when asked to reproduce, port, synchronize, imitate, or achieve feature parity with functionality from another codebase. Deeply discover reference behavior, decompose subfeatures, track evidence-backed parity, implement missing behavior, and verify against the pinned reference revision."
license: MIT
compatibility: Requires source access to the reference and target projects. Git and normal project test/runtime tooling are strongly recommended.
metadata:
  tags: feature-parity, reverse-engineering, codebase-analysis, reimplementation, migration, porting, verification
---

# Feature Parity

Treat the reference project as an executable behavioral specification. Reproduce requested observable behavior with evidence; do not settle for superficial similarity.

Do **not** use this skill for architecture explanation, general codebase exploration, or comparison when the user is not asking to reproduce/synchronize behavior.

## Core rules

1. **Research before implementation.** No implementation until discovery, feature inventory, and an initial parity matrix exist.
2. **Code/runtime are primary evidence.** Docs and screenshots are discovery aids unless stronger evidence is unavailable.
3. **Decompose recursively.** Each final leaf must be independently implementable and verifiable.
4. **No evidence, no parity claim.** `Implemented` requires target evidence; `Partial` never counts as done.
5. **Preserve target-native architecture** unless parity requires change. Reproduce behavior, not accidental internal structure.
6. **Default to behavioral clean-room reimplementation.** Reuse reference code only on explicit request with compatible licensing/provenance.
7. **Verify outside-in.** Prefer observable behavior, contracts, state, persistence, UI interaction, and tests over structural similarity.
8. **Reverse-audit omissions before completion.** Never shrink scope silently; use explicit statuses and reasons.

## Execution mode

Choose the smallest mode that preserves all reasoning gates:

- **Compact:** one narrow, low-risk, low-coupling feature. `PARITY_MATRIX.md` is still mandatory and must be persisted as a file; inventory/evidence/plan/verification may be embedded in it or task notes, but notes must not replace the matrix.
- **Full:** multiple features, cross-module behavior, complex state/persistence/API/UI/integration work, or broad subsystem/product parity. Produce all standard artifacts.

Compact mode may reduce artifacts, **not** discovery, evidence, parity tracking, verification, or completion gates.

## Workflow

### Phase 0 — Freeze scope and revisions

Record the exact reference repository + branch/tag + commit SHA and target repository + branch + baseline commit. The pinned reference revision defines this parity run. If it changes, revalidate affected evidence; only re-baseline automatically when the user explicitly asks to follow upstream/latest.

Identify requested scope, relevant parity dimensions, constraints, and allowed divergences. Read `references/00-scope-and-evidence.md`.

### Phase 1 — Reference reconnaissance

Map architecture and feature surfaces before deep analysis: UI/routes, API/CLI registration, config/flags, schemas/migrations, jobs/events, integrations/plugins, tests/fixtures, and error/recovery paths.

Read `references/01-discovery.md`.

### Phase 2 — Build the feature tree

Create/maintain a feature inventory. Recursively decompose each feature across entry, inputs, states, side effects, outputs, auth, config, failures, lifecycle, async behavior, integrations, and edge cases.

Stop only at independently testable leaves. Read `references/02-feature-decomposition.md`.

### Phase 3 — Build evidence and parity matrix

Give every leaf a stable ID (`F-001`, `F-001.1`, ...), reference evidence, target evidence, status, verification state, and notes.

Statuses: `Missing`, `Partial`, `Implemented`, `Blocked`, `Out-of-scope`, `Intentional divergence`.

`Partial` may be a temporary work state. Before verification completion, split it further if multiple independently testable behaviors remain; an unresolved `Partial` never passes a completion gate.

**Gate A:** implementation may start only when every in-scope leaf has an ID + reference evidence and the target has been assessed.

Read `references/03-parity-matrix.md`.

### Phase 4 — Plan implementation

Plan dependency-aware vertical slices tied to feature IDs, acceptance criteria, target-native components, tests, and compatibility/migration concerns. In Compact mode the plan may be inline; Full mode uses `IMPLEMENTATION_PLAN.md`.

Read `references/04-implementation.md`.

### Phase 5 — Implement and reconcile

For each slice: re-read reference evidence, implement the smallest coherent change, add/run tests, exercise behavior when feasible, update target evidence/status, and inspect adjacent reference behavior for coupled requirements.

Newly discovered behavior gets a new feature leaf; never hide it inside an existing row.

**Gate B:** code presence alone never moves a feature to completed parity.

### Phase 6 — Verify behavior

Use the strongest available method from `references/05-verification.md` (differential/black-box first; inspection only when execution is impossible). For UI-heavy work also read `references/06-ui-parity.md`.

Record verification per leaf and any remaining difference.

### Phase 7 — Reverse omission audit

Re-scan the reference independently of current matrix categories: UI/menu/route trees, API/CLI registration, config/flags, schema/migrations, jobs/events, provider registries, tests/fixtures, errors/recovery, docs/examples/changelog clues.

Any unmatched in-scope behavior becomes a new row and reopens implementation.

**Gate C:** zero unexplained in-scope `Missing`/`Partial` leaves; every `Blocked` row must record blocker, consequence, and required resolution. `Blocked` is incomplete and does not count toward full parity.

### Phase 8 — Final parity report

Report counts by status and material divergences. Never claim full parity unless every in-scope leaf has evidence, every non-divergence leaf is verified `Implemented`, no `Blocked` remains, and the reverse omission audit is complete.

A user-accepted blocked difference must be reclassified as `Intentional divergence`; never treat `Blocked` itself as accepted completion.

## Matrix audit protocol

Resolve `scripts/parity_audit.py` relative to the directory containing this `SKILL.md`, not the target repository working directory. Pass the actual persisted `PARITY_MATRIX.md` path explicitly. Run the audit:

```bash
python3 scripts/parity_audit.py <matrix-path>
```

- after creating the initial matrix;
- after a batch of structural/status changes;
- before Gate B, Gate C, and final completion.

A gate may reuse the most recent successful audit if the matrix has not changed since that audit. Exit `0` passes. Exit `1` means matrix consistency errors; exit `2` means the matrix path is unavailable. On non-zero exit, fix the problem and rerun before crossing the gate.

## Sub-agents

Use parallel/sub-agents only to reduce blind spots or context pressure; the main agent owns scope, stable IDs, authoritative matrix, synthesis, and final decisions. Read `references/07-subagent-orchestration.md`.

## Artifacts

Full mode uses templates under `templates/`:
- `FEATURE_INVENTORY.md`
- `EVIDENCE_MAP.md`
- `PARITY_MATRIX.md`
- `IMPLEMENTATION_PLAN.md`
- `VERIFICATION_REPORT.md`

Compact mode may consolidate these, but must preserve equivalent fields and a machine-auditable parity matrix.

## Completion standard

A feature is complete only when its observable contract matches the pinned reference revision within declared scope/constraints and has verification evidence. Similar names, similar UI, corresponding functions, or happy-path-only code are not parity.

## Execution Feedback 执行反馈

If this workflow encounters unclear instructions, repeated failed attempts, tool/permission blockers, invalid paths, or required workarounds, report the trigger point, symptom, impact, workaround, and improvement suggestion at task end. Do not emit an empty feedback section when no issue occurred; redact credentials and sensitive user data.
