## MODIFIED Requirements

### Requirement: Route development by task and implementation type

The workflow SHALL route backend, frontend, review-only, testing-only and delivery tasks
to the relevant references and available capabilities without forcing unrelated stages.
Completion gates MUST match the selected task; pure tests MUST NOT imply code repair authorization.

#### Scenario: Backend implementation request
- **WHEN** a user requests a backend behavior change
- **THEN** the workflow selects backend development and verification guidance and follows
  the confirmed requirements and actual affected callers

#### Scenario: Review-only request
- **WHEN** a user requests only a review of an explicit patch
- **THEN** the workflow preserves that target and does not modify files or post reviews

#### Scenario: Testing-only request fails CI
- **WHEN** a user requests only test execution and a check fails
- **THEN** the workflow reports evidence and repair guidance without modifying code or starting a repair loop

### Requirement: Separate CI from runtime acceptance

The workflow MUST distinguish repository CI, targeted unit or functional tests, live resource
acceptance, frontend E2E and deployment verification. It SHALL select only relevant supported
entrypoints, record the tested version and report failure, skipped checks and environmental limits.
Acceptance scope MUST follow the confirmed changed behavior rather than capabilities inferred from labels.

#### Scenario: Unit tests pass without a live environment
- **WHEN** local repository tests pass but the relevant live resource behavior cannot be exercised
- **THEN** the workflow reports CI success and runtime verification gaps separately

#### Scenario: Backup testing is requested
- **WHEN** the behavior involves backup but the selected executor excludes that domain
- **THEN** the workflow verifies a supported authorized path and does not silently reuse unsupported Cinder cases

#### Scenario: Deployment version is unknown
- **WHEN** an existing deployment cannot be tied to the changed code
- **THEN** its successful behavior is not used as proof that the new change works

#### Scenario: Only a frontend label changes
- **WHEN** a patch changes only displayed text without changing an operation or its contract
- **THEN** acceptance checks the changed display and applicable static/version evidence, without requiring resource creation as a new acceptance condition

### Requirement: Preserve review and frontend contracts

The workflow MUST preserve the user's complete issue-, function- and evidence-driven
review analysis, P0/P1/P2/P3 severity and concise reporting without hiding important defects
or verification gaps. Existing frontend conventions and real business-effect acceptance MUST remain available.
Read-only review MUST prevent temporary file, cache, resource and Git writes before running validation;
cleaning up after a write MUST NOT be described as read-only execution.

#### Scenario: Concise report with missing cross-project evidence
- **WHEN** no confirmed defect is found but critical issue or compatibility evidence is unavailable
- **THEN** the review reports NEEDS VERIFICATION and the relevant gaps without shortening its analysis

#### Scenario: A proposed reproduction command generates caches
- **WHEN** review validation would import code or run a tool that can write caches or artifacts
- **THEN** the reviewer uses a verified no-write mechanism or leaves the check unexecuted and reports the gap

## ADDED Requirements

### Requirement: Load company policy before unified delivery

EasyStack delivery tasks SHALL load the confirmed company defaults before entering the shared
Git delivery workflow, including the default review site and new Author/Committer email.
Defaults MUST NOT replace the actual repository remote or authorize configuration or history changes.
CI SHALL hand off delivery instead of maintaining a separate amend/upload sequence.

#### Scenario: Delivery is the first task
- **WHEN** the user requests EasyStack delivery checks without prior development steps
- **THEN** the workflow reads its existing company policy, reports the confirmed defaults and separately verifies the real remote, identity, target branch and action authorization

#### Scenario: CI checks have passed
- **WHEN** the user separately authorizes Git delivery after CI
- **THEN** the workflow enters git-delivery and resolves both the real remote and target branch before an authorized upload

### Requirement: Generalize authorized runtime code debugging

The workflow SHALL support authorized code debugging after development through the existing
environment-debugging capability, without requiring a preexisting incident. It MUST discover
the target environment, workload, runtime version, effective files, mounts, management source,
scheduling coverage and rollback baseline before choosing an injection and activation method.
The method MUST distinguish temporary runtime overlays from reproducible delivery and verify
both the active changed version and the relevant behavior. Examples MUST NOT prescribe one
environment, service, node count, replica count, language path or injection mechanism for all tasks.

#### Scenario: The target service differs from the historical example
- **WHEN** another environment or a compiled service is selected
- **THEN** the workflow discovers its actual artifacts, startup and deployment mechanisms instead of applying Cinder Python paths or assuming hostPath exists

#### Scenario: A host-local overlay can be rescheduled
- **WHEN** code is supplied from node-local storage
- **THEN** all possible execution targets have the intended version or an explicitly authorized and verified scheduling restriction applies, even when only one replica runs

#### Scenario: Runtime debugging is authorized
- **WHEN** the user authorizes specific environment changes and a verification path
- **THEN** the workflow reuses the unified access capability, applies only those changes, verifies file/runtime/behavior evidence and records rollback or remaining overlays separately from full regression results

#### Scenario: Rollback restores the recorded baseline
- **WHEN** temporary debugging changes are rolled back
- **THEN** only the task's changes are reversed, original recorded settings are restored and the running state and relevant behavior are checked again
