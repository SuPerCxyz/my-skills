# easystack-development-workflow Specification

## Purpose
提供覆盖 EasyStack 前后端开发、项目联动和分层验证的工作流, 让使用者根据目标项目的
实际版本、调用和部署证据完成必要修改, 保留清晰的验证缺口与授权边界, 避免把单仓库
CI、页面渲染或发版分组误当成跨项目功能已经闭环的证据.
## Requirements
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

### Requirement: Preserve authorization and existing work

The workflow MUST preserve unrelated edits, follow current requirement confirmation and
Git authorization, and avoid inferring cleanup, installation, deployment or remote mutation
permission from development or read-only investigation requests.

#### Scenario: Project content is organized
- **WHEN** the user requests a project relationship inventory without authorizing file deletion
- **THEN** the workflow organizes documentation while preserving source directories and existing edits

### Requirement: Load company policy before unified delivery

EasyStack delivery tasks SHALL load the confirmed company defaults before entering the shared
Git delivery workflow bundled in this skill, including the default review site and new Author/Committer email.
Defaults MUST NOT replace the actual repository remote or authorize configuration or history changes.
CI SHALL hand off delivery instead of maintaining a separate amend/upload sequence.

#### Scenario: Delivery is the first task
- **WHEN** the user requests EasyStack delivery checks without prior development steps
- **THEN** the workflow reads its existing company policy, reports the confirmed defaults and separately verifies the real remote, identity, target branch and action authorization

#### Scenario: CI checks have passed
- **WHEN** the user separately authorizes Git delivery after CI
- **THEN** the workflow follows its bundled delivery reference and resolves both the real remote and target branch before an authorized upload; an external git-delivery skill is optional

### Requirement: Generalize authorized runtime code debugging

The workflow SHALL support authorized code debugging after development through its bundled
runtime-debugging reference, without requiring a preexisting incident or an external skill. It MUST discover
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

#### Scenario: Backend project code is updated
- **WHEN** a backend change is brought into an authorized environment for debugging
- **THEN** the workflow uses the complete compatible project runtime code or built artifact as the update, backup and rollback unit, accounts for added, changed and removed files, and keeps configuration, data and external dependencies within their own boundaries

#### Scenario: Multiple workloads consume the project
- **WHEN** a project is consumed by several workloads, replicas or eligible nodes
- **THEN** the workflow identifies all consumers, selects an authorized version-compatible update cohort and verifies its complete coverage without treating one Pod as whole-project proof

#### Scenario: Existing overlays or generated settings affect the code
- **WHEN** nested mounts or startup-generated configuration can override or write into the replacement project
- **THEN** the workflow resolves precedence, preservation and write permissions in the authorized plan and restores the recorded complete project and deployment baseline on rollback

### Requirement: Default frontend debugging to local development

Frontend development debugging SHALL use the target project's local development entrypoint
and authorized API proxy by default. It MUST distinguish standalone SPA and Host Remote
loading, prove that the browser uses the changed local code and identify the actual API
target. Environment static-artifact replacement SHALL require an explicit deployment
validation request and its concrete action authorization.

#### Scenario: Frontend code is debugged against an environment
- **WHEN** a frontend change needs runtime debugging with environment APIs
- **THEN** the workflow discovers the project's actual scripts, serve path, local address and proxy, then verifies local bundle or remote/chunk provenance and the intended environment API path

#### Scenario: An environment page is reached through a tunnel
- **WHEN** the browser can open a tunneled environment page or receives HTTP 200
- **THEN** the workflow does not treat that alone as evidence of local code loading and checks resource source, content type and applicable host/remote mapping

#### Scenario: No browser or local runtime is available
- **WHEN** the local code and API chain cannot be exercised
- **THEN** static checks are reported separately and local runtime validation remains unverified

### Requirement: Distribute the workflow as a self-contained skill

The complete easystack-workflow directory MUST contain the necessary development, review,
CI, resource testing, frontend E2E, runtime debugging, offline analysis and delivery guidance.
Required local references MUST resolve within that directory. Other skills and their scripts
MUST NOT be installation prerequisites. Standard tools, target source, environment access and
authorization remain execution prerequisites and MUST NOT be claimed to be bundled or verified.

#### Scenario: Only the workflow directory is installed
- **WHEN** the user copies only easystack-workflow to a client without the six previously referenced skills
- **THEN** all required workflow references remain readable and execution follows the bundled guidance using available tools, without requesting those skills

#### Scenario: A real execution prerequisite is unavailable
- **WHEN** an authorized task lacks a browser, Git client, target source or live environment access
- **THEN** the workflow reports the affected unexecuted steps and evidence gaps instead of inventing results or requiring an unrelated skill installation

#### Scenario: Specialized skills are available
- **WHEN** a relevant specialized skill is already available
- **THEN** it may provide optional automation within the same confirmed scope and authorization, without becoming a prerequisite for the bundled workflow
