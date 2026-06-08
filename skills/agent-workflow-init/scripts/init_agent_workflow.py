#!/usr/bin/env python3
"""
Initialize or reconcile the heavy-duty agent workflow at the project level.

This script never creates request workspaces.

Usage:

  python init_agent_workflow.py --project-root .
  python init_agent_workflow.py --project-root . --overwrite-agents
  python init_agent_workflow.py --project-root . --overwrite-custom-agents
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_VERSION = "3.0"


AGENTS_MD = """# AGENTS.md

## Project workflow

This project uses a heavy-duty Codex agent workflow for substantial tasks.

This workflow is not the default mode for casual questions. It should be enabled only when the user explicitly chooses the heavy workflow for the current project.

## Entry points

- `agent-workflow-init`: project-level initialization or reconcile only
- `agent-workflow-start`: start one new request in one new thread

## Thread model

- One requirement thread maps to one request.
- Each new requirement should start in a new thread.
- One thread should not switch across requests mid-run.

## User communication rule

The user communicates only with the Orchestrator thread.

Review, Implementation, and QA roles must not independently accept user instructions as the source of truth.

## Request workspace

Each request must live in:

```text
docs/agent/requests/<request_id>/
```

Each request directory must contain:

```text
requirements.md
acceptance.md
plan.md
risk.md
review.md
implementation.md
qa.md
handoff.md
decision-log.md
rollback.md
state.json
changes/
```

## Runtime source of truth

The only writable source of truth for a request is:

```text
docs/agent/requests/<request_id>/state.json
```

Project-level files may keep indexes and templates, but must not duplicate mutable request runtime state.

The Orchestrator must never use chat memory as the request source of truth.

On resume, compaction recovery, or handoff recovery, read in this order:

1. `docs/agent/requests/<request_id>/state.json`
2. `docs/agent/requests/<request_id>/handoff.md`
3. `docs/agent/requests/<request_id>/decision-log.md`
4. required source-of-truth docs such as `requirements.md`, `acceptance.md`, and `plan.md`

## Legacy runtime files

Do not rely on these old global runtime files as writable truth:

```text
docs/agent/current.md
docs/agent/workflow-state.json
docs/agent/router-log.md
```

## Orchestrator model

The main thread is an Orchestrator. It has exactly four jobs:

1. Talk to the user (requirement clarification, confirmations, final handoff)
2. Read and update `state.json`
3. Dispatch subagents via the Agent tool
4. Synthesize subagent results and decide next action

The Orchestrator NEVER reads or modifies source code, runs tests, performs review, or executes QA directly.

Subagent prompts must be self-contained via SubagentContextPacket. Do not pass conversation history to subagents.

## Required subagent policy

- `critical`: Spec Review, Code Quality Review, Implementation (worktree), Verification, QA all required.
- `high`: Spec Review, Code Quality Review, Implementation (worktree), Verification, QA all required.
- `medium`: Implementation, Verification, QA required. Reviews required for security, architecture, state, or data-boundary changes.
- `low`: exception-only path.

Implementer subagents report one of four statuses: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED.

When a role is required, the Orchestrator must dispatch a subagent via the Agent tool. The Orchestrator must not simulate that role.

## Automation rule

After requirements and acceptance are confirmed, the active request should continue automatically until:

- completion
- a real blocker
- a true high-risk confirmation boundary
- pause or cancel requested by the user

Do not interrupt the user for routine progress summaries while safe executable backlog remains.

The expected execution path after confirmation is:

```text
plan → implementation → spec compliance review → code quality review → verification → qa → fix / re-qa → final handoff
```

If the next step is safe and executable, continue it in the same thread instead of stopping with a progress-only response.

## Anti-premature-stop rule

The Orchestrator must not final while any of the following is true:

- `next_action_executable=true`
- `unfinished_reasons` is non-empty
- `remaining_stages` is non-empty
- `implementation_status` is not `completed`
- required `qa_status` is not `passed`
- `completion_guard.definition_of_done_satisfied` is not `true`

If context has been compacted, do not infer completion from memory. Reconstruct execution state from the request-local files and continue when safe.

## Stage progression rule

Requests must advance in this order:

```text
requirement_clarification → requirements → acceptance → plan → implementation → spec_compliance_review → code_quality_review → verification → qa → final_handoff
```

After each completed stage:

- update `state.json`
- refresh `handoff.md`
- recompute `remaining_stages`
- recompute `unfinished_reasons`

If the next stage is safe and executable, enter it immediately instead of stopping.

## State Update Rules

When a stage finishes, update request-local state as follows:

- append the finished stage to `completed_stages` if it is not already present
- remove the finished stage from `remaining_stages`
- set `current_stage` to the next stage
- set `last_completed_action` to a short factual summary of what was actually done
- set `next_action` to the next executable step
- set `next_action_executable` to `true` only if that step can be executed immediately
- remove resolved items from `unfinished_reasons`
- add new blockers or unmet conditions to `unfinished_reasons`
- set `completion_guard.implementation_complete` to `true` only when implementation is actually complete
- set `completion_guard.qa_passed` to `true` only when required QA has passed
- set `completion_guard.definition_of_done_satisfied` to `true` only when every required done condition is satisfied

Do not advance a stage unless the state has been updated first.
"""


README_MD = """# Agent Workflow

This folder stores project-level assets and per-request workspaces for the heavy workflow.

## Structure

```text
docs/agent/
├── README.md
├── OPERATION.md
├── request-index.json
├── templates/
│   ├── project/
│   └── request/
└── requests/
    └── <request_id>/
        ├── requirements.md
        ├── acceptance.md
        ├── plan.md
        ├── risk.md
        ├── review.md
        ├── implementation.md
        ├── qa.md
        ├── handoff.md
        ├── decision-log.md
        ├── rollback.md
        ├── state.json
        └── changes/
```

## Entry points

- `agent-workflow-init`: initialize or reconcile project-level workflow files
- `agent-workflow-start`: create one request in one dedicated thread and run it end to end

## Runtime truth

Mutable request runtime truth lives only in the request-local `state.json`.

After requirements and acceptance are confirmed, the request should keep executing until completion or a real blocker.

`handoff.md` is not only for pauses. It is also the per-stage recovery checkpoint and should be refreshed after each completed stage.
"""


OPERATION_MD = """# Workflow Operation

## When to use what

Use:

- `agent-workflow-init` when you need to initialize or reconcile the project-level heavy workflow
- `agent-workflow-start` when you open a new thread for a new substantial requirement and want the workflow to carry the request through execution

Do not use `agent-workflow-init` to create a request.

## Thread rule

- one thread corresponds to one request
- each new requirement should start in a new thread
- a thread should not switch across requests mid-run

## Request source of truth

The only writable runtime source of truth is:

```text
docs/agent/requests/<request_id>/state.json
```

Do not rely on chat memory as truth.

## Resume order

When resuming after compaction, handoff, or interruption, read in this order:

1. `handoff.md` (checkpoint)
2. `state.json` (runtime truth)
3. `decision-log.md`
4. `requirements.md`
5. `acceptance.md`
6. `plan.md`

Never resume from memory alone.

If `next_action_executable=true`, continue execution instead of giving a progress-only reply.

## Stage order

Requests advance in this order:

```text
requirement_clarification
→ requirements
→ acceptance
→ plan
→ implementation
→ spec_compliance_review
→ code_quality_review
→ verification
→ qa
→ final_handoff
```

After each completed stage:

- update `state.json`
- refresh `handoff.md`
- update `completed_stages`
- update `remaining_stages`
- update `unfinished_reasons`
- update `last_completed_action`
- update `next_action`

## Anti-premature-stop checklist

Do not final while any of these is true:

- `next_action_executable=true`
- `unfinished_reasons` is non-empty
- `remaining_stages` is non-empty
- `implementation_status != completed`
- required `qa_status != passed`
- `completion_guard.definition_of_done_satisfied != true`

## Key fields

Fields that matter most for recovery and completion:

- `objective`
- `definition_of_done`
- `current_stage`
- `completed_stages`
- `remaining_stages`
- `last_completed_action`
- `next_action`
- `next_action_executable`
- `unfinished_reasons`
- `completion_guard`

## Handoff rule

`handoff.md` is not just for pauses. It is the per-stage recovery checkpoint.

Each refresh should include:

- current objective
- current stage
- completed stages
- remaining stages
- last completed action
- next action
- why final is not allowed yet
"""


COORDINATION_POLICY = """# Coordination Policy

- One request per thread.
- One thread should not switch across requests.
- One request should have one coordinating Orchestrator thread.
- `docs/agent/request-index.json` is an index only, not runtime truth.
- `docs/agent/requests/<request_id>/state.json` is the only writable runtime source of truth for the request.
"""


MIGRATION_NOTE = """# Migration Note

This workflow no longer uses these files as writable runtime truth:

- `docs/agent/current.md`
- `docs/agent/workflow-state.json`
- `docs/agent/router-log.md`

If they exist, keep them only for historical reference during migration.
"""


REVIEW_AGENT = '''name = "review"
description = "Read-only review agent for heavy workflow requests (spec compliance and code quality)."
sandbox_mode = "read-only"
developer_instructions = """
Read only:
- state.json
- requirements.md
- acceptance.md
- risk.md
- plan.md when present
- implementation.md when present

Rules:
1. Read-only.
2. Do not write code.
3. Treat `state.json` as the runtime source of truth, never chat memory.
4. Spec compliance review: verify implementation matches requirements exactly (no missing, no extra).
5. Code quality review: check structure, correctness, maintainability, testing.
6. Do not trust the implementer's report — read the actual code.
7. Output explicit review findings and a clear PASS/FAIL decision.
8. Do not use vague conclusions such as "looks fine".
"""
'''


IMPLEMENTATION_AGENT = '''name = "implementation"
description = "Implementation agent for heavy workflow requests."
sandbox_mode = "workspace-write"
developer_instructions = """
Implement only confirmed scope from:
- state.json
- requirements.md
- acceptance.md
- plan.md
- review.md

Rules:
1. Read `state.json` first and treat it as the runtime source of truth.
2. Do not expand scope.
3. Implement only the current safe package for the active stage.
4. Update `implementation.md` with files changed and validations run.
5. After each completed implementation package, update request-local state with:
   - `last_completed_action`
   - `implementation_status`
   - `next_action`
   - `unfinished_reasons`
   - `updated_at`
   - `completed_stages`
   - `remaining_stages`
   - `completion_guard`
6. Do not mark the request complete merely because code changed.
7. Stop if requirements conflict with code reality.
8. Do not simulate QA.
"""
'''


QA_AGENT = '''name = "qa"
description = "Read-only QA agent for heavy workflow requests."
sandbox_mode = "read-only"
developer_instructions = """
Validate strictly against `acceptance.md`.

Rules:
1. Read-only.
2. Do not modify files.
3. Read `state.json` before QA and treat it as runtime truth.
4. Mark each required acceptance check as `pass`, `fail`, or `blocked`.
5. On QA pass, state clearly that `qa_status` should become `passed` and identify covered acceptance criteria.
6. On QA fail, state clearly which items must be added to `unfinished_reasons`.
7. Failures must include reproduction and evidence.
8. Do not say "basically done" or equivalent vague language.
9. If QA passes, expect state updates:
   - `qa_status = passed`
   - `completion_guard.qa_passed = true`
   - `unfinished_reasons` should lose QA-related blockers
   - `next_action` should advance toward final handoff only when no other blockers remain
"""
'''


REQUEST_INDEX = {
    "version": PROJECT_VERSION,
    "requests": {},
}


PROJECT_TEMPLATE_HINT = """# Project Template Notes

This directory stores project-level templates used by `agent-workflow-init`.
"""


REQUEST_TEMPLATE_HINT = """# Request Template Notes

This directory stores request-level templates used by `agent-workflow-start`.
"""


REQUEST_FILE_TEMPLATES = {
    "requirements.md.template": "# Requirements: <request_title>\n\n## Background\n\n## Goals\n\n## Functional Requirements\n\n### FR-1\n\n## Open Questions\n",
    "acceptance.md.template": "# Acceptance: <request_title>\n\n## Requirement Mapping\n\n| Requirement ID | Acceptance ID | Priority |\n|---|---|---|\n| FR-1 | AC-1 | Must |\n\n## Acceptance Criteria\n\n### AC-1\n",
    "plan.md.template": "# Plan\n\n## Scope\n\n## Non-Scope\n\n## Likely Files\n\n## Validation\n",
    "risk.md.template": "# Risk\n\n## Risk Summary\n",
    "review.md.template": "# Review\n\n## Findings\n",
    "implementation.md.template": "# Implementation\n\n## Changes\n",
    "qa.md.template": "# QA\n\n## Acceptance Checks\n",
    "handoff.md.template": "# Handoff\n\n## Current Objective\n\n## Current Stage\n\n## Completed Stages\n\n## Remaining Stages\n\n## Last Completed Action\n\n## Next Action\n\n## Why Final Is Not Allowed Yet\n",
    "decision-log.md.template": "# Decision Log\n",
    "rollback.md.template": "# Rollback\n",
    "state.json.template": "{\n  \"request_id\": \"<request_id>\",\n  \"objective\": \"<objective>\",\n  \"definition_of_done\": [\n    \"requirements confirmed\",\n    \"acceptance confirmed\",\n    \"implementation complete\",\n    \"qa passed\"\n  ],\n  \"current_stage\": \"requirement_clarification\",\n  \"stage_status\": \"in_progress\",\n  \"completed_stages\": [],\n  \"remaining_stages\": [\n    \"requirement_clarification\",\n    \"requirements\",\n    \"acceptance\",\n    \"plan\",\n    \"implementation\",\n    \"spec_compliance_review\",\n    \"code_quality_review\",\n    \"verification\",\n    \"qa\",\n    \"final_handoff\"\n  ],\n  \"stage_transition_contract\": {\n    \"ordered_stages\": [\n      \"requirement_clarification\",\n      \"requirements\",\n      \"acceptance\",\n      \"plan\",\n      \"implementation\",\n      \"spec_compliance_review\",\n      \"code_quality_review\",\n      \"verification\",\n      \"qa\",\n      \"final_handoff\"\n    ],\n    \"checkpoint_required_after_each_stage\": true\n  },\n  \"auto_execute_after_confirmation\": true,\n  \"last_completed_action\": null,\n  \"next_action\": \"clarify_requirements\",\n  \"next_action_executable\": true,\n  \"requires_user_confirmation\": true,\n  \"unfinished_reasons\": [\n    \"requirements not confirmed\",\n    \"acceptance not confirmed\",\n    \"implementation not complete\",\n    \"qa not passed\"\n  ]\n}\n",
}


STOP_AUDIT_JS = r"""#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

function fail(message) {
  console.error(message);
  process.exit(1);
}

function parseArgs(argv) {
  const args = { mode: "final", projectRoot: process.cwd() };
  for (let i = 2; i < argv.length; i += 1) {
    const part = argv[i];
    if (part === "--request-id") args.requestId = argv[++i];
    else if (part === "--request-path") args.requestPath = argv[++i];
    else if (part === "--project-root") args.projectRoot = argv[++i];
    else if (part === "--mode") args.mode = argv[++i];
  }
  return args;
}

function loadState(args) {
  let statePath = args.requestPath;
  if (!statePath) {
    if (!args.requestId) fail("Missing --request-id or --request-path");
    statePath = path.join(args.projectRoot, "docs", "agent", "requests", args.requestId, "state.json");
  }
  if (!fs.existsSync(statePath)) fail(`State file not found: ${statePath}`);
  const raw = fs.readFileSync(statePath, "utf8");
  return JSON.parse(raw);
}

function validateFinal(state) {
  const safeBacklog = Array.isArray(state.safe_backlog_candidates) ? state.safe_backlog_candidates : [];
  const runtimeProcesses = Array.isArray(state.runtime_processes) ? state.runtime_processes : [];
  const blockingProcesses = runtimeProcesses.filter((item) => item && item.must_cleanup_before_final);
  const unfinishedReasons = Array.isArray(state.unfinished_reasons) ? state.unfinished_reasons : [];
  const remainingStages = Array.isArray(state.remaining_stages) ? state.remaining_stages : [];
  const completionGuard = state.completion_guard || {};

  if (state.stop_allowed !== true) fail("stop audit failed: stop_allowed is not true");
  if (state.next_action_executable === true) fail("stop audit failed: next_action_executable is true");
  if (safeBacklog.length > 0) fail("stop audit failed: safe backlog still exists");
  if (unfinishedReasons.length > 0) fail("stop audit failed: unfinished reasons still exist");
  if (remainingStages.length > 0) fail("stop audit failed: remaining stages still exist");
  if (state.implementation_status && state.implementation_status !== "completed") fail("stop audit failed: implementation_status is not completed");
  if (state.qa_status && state.qa_status !== "passed" && state.subagent_policy && state.subagent_policy.qa_required) fail("stop audit failed: required qa_status is not passed");
  if (completionGuard.definition_of_done_satisfied !== true) fail("stop audit failed: definition of done is not satisfied");
  if (blockingProcesses.length > 0) fail("stop audit failed: runtime processes still require cleanup");
}

function validatePreImplementation(state) {
  if (state.blocked === true) fail("pre-implementation audit failed: request is blocked");
  if (state.paused === true) fail("pre-implementation audit failed: request is paused");
  if (state.canceled === true) fail("pre-implementation audit failed: request is canceled");
  if (state.requires_user_confirmation === true) fail("pre-implementation audit failed: request still needs user confirmation");
}

function main() {
  const args = parseArgs(process.argv);
  const state = loadState(args);
  if (args.mode === "pre-implementation") validatePreImplementation(state);
  else validateFinal(state);
  console.log("stop audit passed");
}

main();
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_text(path: Path, content: str, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_project_layout(project_root: Path, overwrite_agents: bool, overwrite_custom_agents: bool) -> None:
    created_at = now_iso()
    write_text(project_root / "AGENTS.md", AGENTS_MD, overwrite_agents)

    project_json_path = project_root / ".codex/workflow/project.json"
    if project_json_path.exists():
        try:
            project_payload = json.loads(project_json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            project_payload = {}
    else:
        project_payload = {}
    project_payload.update(
        {
            "initialized": True,
            "version": PROJECT_VERSION,
            "project_root": str(project_root),
            "mode": "heavy_workflow",
            "created_at": project_payload.get("created_at", created_at),
            "last_reconcile_at": created_at,
            "request_state_source": "docs/agent/requests/<request_id>/state.json",
            "supports_thread_binding": True,
        }
    )
    write_json(project_json_path, project_payload, overwrite=True)

    write_text(project_root / ".codex/agents/review.toml", REVIEW_AGENT, overwrite_custom_agents)
    write_text(project_root / ".codex/agents/implementation.toml", IMPLEMENTATION_AGENT, overwrite_custom_agents)
    write_text(project_root / ".codex/agents/qa.toml", QA_AGENT, overwrite_custom_agents)

    write_text(project_root / "docs/agent/README.md", README_MD, overwrite=True)
    write_text(project_root / "docs/agent/OPERATION.md", OPERATION_MD, overwrite=True)
    write_text(project_root / "docs/agent/coordination-policy.md", COORDINATION_POLICY, overwrite=True)
    write_text(project_root / "docs/agent/MIGRATION.md", MIGRATION_NOTE, overwrite=True)

    request_index_path = project_root / "docs/agent/request-index.json"
    if request_index_path.exists():
        try:
            existing = json.loads(request_index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        existing["version"] = PROJECT_VERSION
        existing["updated_at"] = created_at
        if "requests" not in existing or not isinstance(existing["requests"], dict):
            existing["requests"] = {}
        write_json(request_index_path, existing, overwrite=True)
    else:
        payload = dict(REQUEST_INDEX)
        payload["updated_at"] = created_at
        write_json(request_index_path, payload, overwrite=True)

    project_template_dir = project_root / "docs/agent/templates/project"
    request_template_dir = project_root / "docs/agent/templates/request"
    write_text(project_template_dir / "README.md", PROJECT_TEMPLATE_HINT, overwrite=True)
    write_text(project_template_dir / "AGENTS.md.template", AGENTS_MD, overwrite=True)
    write_text(project_template_dir / "OPERATION.md.template", OPERATION_MD, overwrite=True)
    write_text(project_template_dir / "coordination-policy.md.template", COORDINATION_POLICY, overwrite=True)
    write_text(request_template_dir / "README.md", REQUEST_TEMPLATE_HINT, overwrite=True)
    for filename, content in REQUEST_FILE_TEMPLATES.items():
        write_text(request_template_dir / filename, content, overwrite=True)

    (project_root / "docs/agent/requests").mkdir(parents=True, exist_ok=True)

    stop_audit_path = project_root / "scripts/agent/stop-audit.js"
    write_text(stop_audit_path, STOP_AUDIT_JS, overwrite=True)
    stop_audit_path.chmod(0o755)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--overwrite-agents", action="store_true")
    parser.add_argument("--overwrite-custom-agents", action="store_true")
    parser.add_argument("--new-request", help="Deprecated and unsupported in v3. Use agent-workflow-start instead.")
    args = parser.parse_args()

    if args.new_request:
        raise SystemExit("`--new-request` has been removed. Use `agent-workflow-start` to create and run a request.")

    project_root = Path(args.project_root).resolve()
    ensure_project_layout(project_root, args.overwrite_agents, args.overwrite_custom_agents)
    print("Initialized or reconciled project-level heavy workflow.")


if __name__ == "__main__":
    main()
