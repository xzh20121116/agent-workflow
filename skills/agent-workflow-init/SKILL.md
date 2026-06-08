---
name: agent-workflow-init
description: Initialize or reconcile a heavy-duty Codex agent workflow at the project level. This skill never creates a request workspace and never starts request execution.
---

# Agent Workflow Init

## Purpose

This skill is the project-level bootstrapper for the heavy workflow.

Use it only when the user explicitly wants to:

- initialize workflow files for the current project
- reconcile or repair an existing workflow installation
- upgrade the project-level workflow layout

This skill does **not**:

- create `docs/agent/requests/<request_id>/`
- start a requirement thread
- enter requirements, acceptance, implementation, or QA execution

Those actions belong to `agent-workflow-start`.

## Heavy-Workflow Boundary

This workflow is intentionally heavy.

Assume it is enabled only for substantial work where the user wants:

- one request per thread
- independent request workspaces
- strict Review / Implementation / QA roles
- automatic execution after confirmation
- minimal user interruption until real blockers appear

Do not try to lighten the workflow here.

## Deterministic Project Boundary

Operate only inside the current project root.

Do not perform broad discovery. Do not search parent directories, home directories, unrelated projects, or global skill folders unless the user explicitly asks.

## Split Responsibilities

### `agent-workflow-init`

Project-level only.

Creates or reconciles:

- `AGENTS.md`
- `.codex/workflow/project.json`
- `.codex/agents/*.toml`
- `docs/agent/request-index.json`
- `docs/agent/templates/project/`
- `docs/agent/templates/request/`
- `scripts/agent/stop-audit.js`

### `agent-workflow-start`

Request-level only.

Creates:

- `docs/agent/requests/<request_id>/...`

Then binds the current thread to that request and runs the request lifecycle.

## Trigger Examples

```text
初始化 agent workflow
初始化这个项目的重任务流程
修复 workflow
reconcile workflow
升级当前项目的 agent workflow
```

## Required Behavior

1. Check `.codex/workflow/project.json`.
2. If missing, initialize the project-level workflow.
3. If present, enter reconcile mode.
4. Preserve customized project files unless explicit overwrite is requested.
5. Never create a request workspace during init/reconcile.
6. Never infer a requirement from a project-level init request.

## Project-Level File Model

The project-level workflow must use:

```text
.codex/workflow/project.json
docs/agent/request-index.json
```

The workflow must not rely on these old global runtime files as the writable source of truth:

```text
docs/agent/current.md
docs/agent/workflow-state.json
docs/agent/router-log.md
```

If they exist in older projects, treat them as legacy artifacts and migrate away from them.

## Request Runtime Model

The only writable source of truth for a request is:

```text
docs/agent/requests/<request_id>/state.json
```

Project-level files may store summaries and indexes, but not mutable request runtime truth.

## Reconcile Rules

Reconcile may:

- create missing project-level files
- add missing templates
- add missing stop-audit script
- migrate legacy global runtime files to the new project layout
- report incompatible customizations

Reconcile must not silently overwrite customized content in:

- `AGENTS.md`
- `.codex/agents/*.toml`
- `.codex/workflow/project.json`
- `docs/agent/request-index.json`

If a file exists and differs materially, prefer a preservation-first update path.

## Suggested Script

When shell execution is appropriate, use:

```bash
python skills/agent-workflow-init/scripts/init_agent_workflow.py --project-root .
```

Optional overwrite flags are allowed only when the user explicitly approves them.

## Completion Standard

`agent-workflow-init` is complete only when:

- project-level files exist or are reconciled
- no request workspace was created accidentally
- the project is ready for `agent-workflow-start`

## Do Not Do

- Do not start a request from this skill.
- Do not ask the user requirement questions from this skill.
- Do not create `requirements.md` / `acceptance.md` / `plan.md` during init.
- Do not simulate request execution here.
