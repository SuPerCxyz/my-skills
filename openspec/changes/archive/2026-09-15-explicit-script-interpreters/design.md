## Context

The repository contains shell and Python entrypoints across several skills. Most user-facing Python commands already use `python3`, while the environment-debugging tests and one helper call shell scripts directly. The test executor also retains a direct `env-access.sh` allowlist entry. See `proposal.md` for the motivation and `specs/explicit-script-execution/spec.md` for the behavior contract.

## Goals / Non-Goals

**Goals:**

- Make local script invocation independent of the synchronized file mode.
- Keep the interpreter choice visible at every user-facing or test invocation.
- Make the environment-access contract reject the direct form that can fail after synchronization.

**Non-Goals:**

- Do not change script business logic, shebangs, or tracked permission bits.
- Do not convert sourced shell libraries into standalone processes.
- Do not change remote command transport, Kubernetes startup commands, or archived design documents.

## Decisions

1. Use `bash <path>` for local shell scripts. This is the smallest change and works even when a copied script is `0644`; changing modes would depend on the receiving filesystem and Git checkout behavior.
2. Use `python3 <path>` for documented Python commands. Python scripts already use `sys.executable` for internal launchers, so those generated argv values remain explicit and do not need a behavioral change.
3. Remove direct `env-access.sh` from the executor allowlist and update its rule text and regression coverage. This aligns the executable contract with the safe invocation documented by the environment-debugging skill.
4. Leave `source` and remote `bash -s` intact. They are deliberate shell composition or transport mechanisms, not direct local entrypoint calls.

## Risks / Trade-offs

- [Compatibility] Existing plans that use direct `env-access.sh` become invalid → update the normalization rule and report the breaking contract clearly; valid plans already use `bash`.
- [Coverage] A future document could reintroduce a direct invocation → run a repository-wide targeted scan and the affected skill regression tests before completion.

## Migration Plan

Update local commands and the executor allowlist in one change, run static scans and relevant tests, then archive the completed OpenSpec change after the repository files and artifacts agree.
