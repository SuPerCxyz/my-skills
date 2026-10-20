## ADDED Requirements

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

## MODIFIED Requirements

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

#### Scenario: Backend project code is updated
- **WHEN** a backend change is brought into an authorized environment for debugging
- **THEN** the workflow uses the complete compatible project runtime code or built artifact as the update, backup and rollback unit, accounts for added, changed and removed files, and keeps configuration, data and external dependencies within their own boundaries

#### Scenario: Multiple workloads consume the project
- **WHEN** a project is consumed by several workloads, replicas or eligible nodes
- **THEN** the workflow identifies all consumers, selects an authorized version-compatible update cohort and verifies its complete coverage without treating one Pod as whole-project proof

#### Scenario: Existing overlays or generated settings affect the code
- **WHEN** nested mounts or startup-generated configuration can override or write into the replacement project
- **THEN** the workflow resolves precedence, preservation and write permissions in the authorized plan and restores the recorded complete project and deployment baseline on rollback
