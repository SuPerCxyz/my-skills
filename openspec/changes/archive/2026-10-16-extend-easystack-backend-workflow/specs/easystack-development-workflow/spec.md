## Purpose

提供覆盖 EasyStack 前后端开发、项目联动和分层验证的工作流, 让使用者根据目标项目的
实际版本、调用和部署证据完成必要修改, 保留清晰的验证缺口与授权边界, 避免把单仓库
CI、页面渲染或发版分组误当成跨项目功能已经闭环的证据.

## ADDED Requirements

### Requirement: Route development by task and implementation type

The workflow SHALL route backend, frontend, review-only, testing-only and delivery tasks
to the relevant references and available capabilities without forcing unrelated stages.

#### Scenario: Backend implementation request
- **WHEN** a user requests a backend behavior change
- **THEN** the workflow selects backend development and verification guidance and follows
  the confirmed requirements and actual affected callers

#### Scenario: Review-only request
- **WHEN** a user requests only a review of an explicit patch
- **THEN** the workflow preserves that target and does not modify files or post reviews

### Requirement: Adapt backend guidance to the target repository

The workflow MUST identify the target baseline, local rules, language, dependency and
test constraints before selecting coding, migration, compatibility and validation mechanisms.
Conflicting mandatory rules and implementation evidence MUST be disclosed rather than silently overridden.

#### Scenario: Legacy and modern services coexist
- **WHEN** related repositories support different language or framework generations
- **THEN** the workflow uses each repository's actual constraints and does not impose one common runtime

#### Scenario: Operator or native service
- **WHEN** a change concerns a Go controller or a C/Go service
- **THEN** the workflow selects its actual build and test entrypoints rather than Python tox by default

#### Scenario: Migration documentation conflicts with code
- **WHEN** a mandatory repository rule names a migration mechanism inconsistent with the current implementation
- **THEN** the conflict and its impact are surfaced before the affected migration work proceeds

### Requirement: Assess backend contracts and lifecycle as needed

The workflow SHALL follow the relevant API, authorization, RPC or SDK, object, database,
manager, driver and configuration boundaries of a change. It MUST assess affected version
compatibility, asynchronous state, concurrency, retries, idempotency, failure recovery and cleanup.

#### Scenario: Attachment or connector contract changes
- **WHEN** a change affects a volume connection contract shared by consumers and providers
- **THEN** the workflow checks the actual consuming and producing versions, failure paths
  and required coordinated changes without assuming every related repository must change

#### Scenario: Client contract remains satisfied
- **WHEN** the current consumer already supports the provider's confirmed behavior
- **THEN** it can be classified as not requiring changes with supporting evidence

### Requirement: Keep an evidence-backed project map

The workflow SHALL describe the known local repositories and relevant confirmed project
groups with their roles and source evidence. It MUST distinguish runtime calls, package
dependencies, deployment consumption, release grouping, inference and unknowns.

#### Scenario: Backup shares service code
- **WHEN** a task concerns the backup UI, API or worker
- **THEN** the workflow considers yak, golem, Cinder backup and ark-thor according to actual
  caller and deployment evidence rather than treating backup as only a different frontend

#### Scenario: Two checkouts use the same origin
- **WHEN** the same library has separate local checkouts on different branches
- **THEN** the map preserves both identities and requires target selection without deleting or merging them

#### Scenario: Gerrit data cannot be read
- **WHEN** a remote project query is blocked or a page requires unavailable authentication
- **THEN** the workflow reports the limit and does not present local inventory as the complete remote catalog

### Requirement: Decide coordinated changes from evidence

The workflow SHALL classify each actually relevant repository as requiring changes,
requiring further evidence or not requiring changes, with reasons and validation implications.
Names, shared issue identifiers or release groups alone MUST NOT establish mandatory coordinated edits.

#### Scenario: UI displays an existing API field
- **WHEN** the requested field already traverses the relevant API and response mapping correctly
- **THEN** the workflow limits implementation to the required UI work and records evidence for unchanged layers

### Requirement: Separate CI from runtime acceptance

The workflow MUST distinguish repository CI, targeted unit or functional tests, live resource
acceptance, frontend E2E and deployment verification. It SHALL select only relevant supported
entrypoints, record the tested version and report failure, skipped checks and environmental limits.

#### Scenario: Unit tests pass without a live environment
- **WHEN** local repository tests pass but the relevant live resource behavior cannot be exercised
- **THEN** the workflow reports CI success and runtime verification gaps separately

#### Scenario: Backup testing is requested
- **WHEN** the behavior involves backup but the selected executor excludes that domain
- **THEN** the workflow verifies a supported authorized path and does not silently reuse unsupported Cinder cases

#### Scenario: Deployment version is unknown
- **WHEN** an existing deployment cannot be tied to the changed code
- **THEN** its successful behavior is not used as proof that the new change works

### Requirement: Preserve review and frontend contracts

The workflow MUST preserve the user's complete issue-, function- and evidence-driven
review analysis, P0/P1/P2/P3 severity and concise reporting without hiding important defects
or verification gaps. Existing frontend conventions and real business-effect acceptance MUST remain available.

#### Scenario: Concise report with missing cross-project evidence
- **WHEN** no confirmed defect is found but critical issue or compatibility evidence is unavailable
- **THEN** the review reports NEEDS VERIFICATION and the relevant gaps without shortening its analysis

### Requirement: Preserve authorization and existing work

The workflow MUST preserve unrelated edits, follow current requirement confirmation and
Git authorization, and avoid inferring cleanup, installation, deployment or remote mutation
permission from development or read-only investigation requests.

#### Scenario: Project content is organized
- **WHEN** the user requests a project relationship inventory without authorizing file deletion
- **THEN** the workflow organizes documentation while preserving source directories and existing edits
