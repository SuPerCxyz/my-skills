## Context

See proposal.md for motivation. The existing skill has six Markdown files and a generic
development flow, but its detailed development and verification references are frontend-specific.
The repository already has a usable spec-driven schema and OpenSpec CLI 1.8.0; artifacts
can be managed through the current CLI without adding AI tool configuration or editing AGENTS.md.

Read-only exploration covered 26 Git directories under `~/EScode`, representing 25 distinct
origin URLs: 24 Gerrit projects and one GitLab documentation project. Current working copies
span Python 2/3, Django, modern and older Angular, Go controllers, C/Go services and Helm/Kolla.
Several contain user edits. Two os-brick checkouts share an origin but differ in branch.

## Goals / Non-Goals

**Goals:** Add compact backend references; connect them to existing implementation, Review
and acceptance routing; replace incomplete project roles with evidence-backed relationships.

**Non-Goals:** Change source repositories, unify their versions, resolve their existing code
issues, delete checkouts, install external skills, configure MCP, or execute live business tests.

## Decisions

- Add `backend-development.md` and `backend-testing.md` rather than expanding the main skill
  into a tutorial. Keep task selection in SKILL.md and all references directly indexed.
- Expand `project-relationships.md` in place. Separate local inventory, code/deployment
  evidence and governance release groups so grouping does not become an automatic edit list.
  Keep missing checkouts and unproven gateway rewriting explicit.
- Prefer each target's HACKING, actual dependencies, tooling and verified contracts.
  Consult OpenStack official guidance and pinned community skill sources for relevant principles;
  do not copy their tool-specific dispatch, automatic posting, version assumptions or rigid policies.
- A local Nova CLAUDE rule requires Alembic while inspected migration code uses sqlalchemy-migrate.
  Document how to surface this kind of conflict; do not silently ignore the mandatory rule
  or migrate the application as part of a documentation task.
- Keep CI, live resource tests, frontend E2E and deployment checks separate. Reuse existing
  skills only within their supported scope, including the backend executor's Backup exclusion.
- Preserve code-review.md, frontend-design.md and frontend-testing.md unchanged in this extension.
  Keep their full analysis, P0-P3, source attribution, version checks and runtime acceptance gates.
- The main agent owns shared entrypoints, the relationship map and OpenSpec. A reusable child
  writes only the two backend references; the other child performs read-only investigation/QA.

## Risks / Trade-offs

- Mutable local snapshots can drift -> identify evidence paths and snapshot context, require
  per-task branch/version verification, and avoid freezing transient worktree status as a policy.
- Gerrit MCP is blocked by platform approval policy -> do not claim remote enumeration.
  Inspect the subsequently supplied `/admin/repos` page read-only; record only retrieved data
  and preserve authentication/visibility limits. Continue local work independently.
- Community skills include modern Go patterns or upstream-specific rules -> adapt only after
  checking the actual project's supported versions; they are references, not installed dependencies.
- Routing can grow into mandatory testing of every service -> expand only on concrete changed
  contracts or risk evidence, and classify unchanged repositories with reasons.

## Validation

Check frontmatter, description, bilingual headings, ASCII punctuation, indexes, local links,
changed-file scope and source attribution. Verify preserved-reference checksums. Strictly validate
OpenSpec and walk backend service, library, operator, backup, legacy-version and permission scenarios.
These checks validate the workflow documentation, not runtime API or data-plane interoperability.

The supplied Gerrit page returned HTTP 200 with a JS shell. Following its actual links to
the site's REST documentation identified the read-only project list request; an anonymous
`GET /projects/?n=1&d` returned HTTP 200 and an empty object. This establishes anonymous
visibility only, not an empty server or a complete project catalog. Browser launch was
locally unavailable; existing SSH routes did not reach authentication because of local
configuration/host-key prerequisites. No security settings, identities or host trust were changed.
