---
name: agent-workflow-start
description: Start one heavy-workflow request in the current thread, create the request workspace, bind the thread, and drive the request until completion or a real blocker.
---

# Agent Workflow Start

## Purpose

This skill is the only request-level entry point for the heavy workflow.

Use it when the user explicitly wants to start a substantial task under the project workflow.

This skill must:

1. create exactly one new request workspace
2. bind the current thread to that request
3. enter requirement clarification
4. continue through requirements, acceptance, plan, implementation, two-stage review, verification, and QA
5. avoid interrupting the user until a real blocker or high-risk confirmation boundary appears

## Prerequisite

The project must already be initialized by `agent-workflow-init`.

If `.codex/workflow/project.json` is missing, stop and tell the user to initialize the workflow first. Do not silently bootstrap the project from this skill.

## Thread Model

- one new thread for one new request
- one thread should not switch across requests
- one request should not be shared across multiple orchestrator threads unless explicitly rebound

## Trigger Examples

```text
按 workflow 启动这个需求
用重任务流程处理这个需求
start heavy workflow for this requirement
创建 request 并开始执行
```

## Required Start Behavior

1. Confirm the task is meant for the heavy workflow.
2. Create `docs/agent/requests/<request_id>/`.
3. Create all required request files.
4. Write request-local `state.json`.
5. Update `docs/agent/request-index.json`.
6. Bind the current thread in `state.json`.
7. Enter requirement clarification immediately.

## Orchestrator Execution Model

The main thread is an **Orchestrator**. It has exactly four jobs:

1. Talk to the user (requirement clarification, confirmations, final handoff)
2. Read and update `state.json`
3. Dispatch subagents via the Agent tool
4. Synthesize subagent results and decide next action

### Orchestrator NEVER does directly

- Read or modify source code files
- Run tests, lint, or build commands
- Write implementation code
- Perform code review
- Execute QA verification

If you catch yourself doing any of the above, **stop immediately** and spawn a subagent instead.

### SubagentContextPacket

Every subagent prompt must be self-contained. Build a **SubagentContextPacket** before dispatching:

- **Task:** what to do (from plan.md task text)
- **Goal:** success condition
- **Stop condition:** when to stop
- **Relevant files:** explicit file list with paths
- **Known facts:** from requirements.md, acceptance.md
- **Non-goals:** what NOT to do
- **Expected output:** what to write, where
- **Verification expected:** how to confirm success
- **Unsafe assumptions:** things the subagent should verify

The packet is a map, not proof. The subagent must verify critical facts from raw sources.

Do not paste full conversation history, full session context, or unbounded logs into subagent prompts.

### Prompt Templates

Use the prompt templates in `references/` for each role:

- `references/implementer-prompt.md` — implementation subagent (backend/general)
- `references/frontend-implementer-prompt.md` — implementation subagent (frontend/UI tasks, includes design constraints)
- `references/spec-reviewer-prompt.md` — spec compliance review
- `references/code-quality-reviewer-prompt.md` — code quality review
- `references/ui-reviewer-prompt.md` — UI/visual quality review (frontend tasks only)
- `references/verification-prompt.md` — test/lint/build verification
- `references/qa-prompt.md` — acceptance criteria verification

Read the template, fill in the SubagentContextPacket, and dispatch via Agent tool.

### Frontend Task Detection

When the plan includes frontend UI work (pages, components, layouts, visual changes):

1. Use `frontend-implementer-prompt.md` instead of `implementer-prompt.md` — it includes design constraints (typography, color, layout, motion rules)
2. Add `ui_review` stage after `code_quality_review` — dedicated visual quality check
3. The UI reviewer checks for AI-slop patterns, visual hierarchy, responsiveness, and accessibility

Signals that a task includes frontend UI work:
- Task mentions: 页面, UI, 界面, 组件, landing page, dashboard, form, layout, component
- Task creates/modifies: .tsx, .vue, .html, .css, .scss files
- Task involves: visual design, styling, responsive layout

For mixed tasks (frontend + backend), split the plan: backend tasks use `implementer-prompt.md`, frontend tasks use `frontend-implementer-prompt.md`.

## Confirmation → Delegation Pattern

After the user confirms both requirements and acceptance, the orchestrator must:

1. Update `state.json` (set `current_stage` to next stage)
2. **Immediately** spawn the next subagent via Agent tool
3. Do NOT respond to the user between confirmation and delegation
4. Do NOT summarize what was confirmed
5. Do NOT ask "should I proceed"

The user's confirmation IS the instruction to proceed. The next action is always delegation.

## Required Execution Behavior

After requirements and acceptance are confirmed, continue automatically by delegating to subagents.

### Positive Flow Rules

```
User confirms requirements+acceptance
  → Update state.json → Write plan.md → Dispatch IMPLEMENTATION agent

Implementation agent returns
  → Handle status (see Implementer Status Handling below)
  → If DONE: Dispatch SPEC COMPLIANCE REVIEWER

Spec review passes
  → Dispatch CODE QUALITY REVIEWER

Code quality review passes
  → If frontend task: Dispatch UI REVIEWER
  → If backend-only: Dispatch VERIFICATION agent

UI review passes (frontend tasks only)
  → Dispatch VERIFICATION agent

Verification passes
  → Dispatch QA agent

QA passes
  → Enter final_handoff, report to user

Any stage fails
  → Dispatch fix agent with specific instructions → Re-run failed stage
```

### Implementer Status Handling

Each implementer subagent reports one of four statuses. Handle each appropriately:

**DONE:** Proceed to spec compliance review.

**DONE_WITH_CONCERNS:** The implementer completed the work but flagged doubts. Read the concerns before proceeding. If the concerns are about correctness or scope, address them before review. If they're observations (e.g., "this file is getting large"), note them and proceed to review.

**NEEDS_CONTEXT:** The implementer needs information that wasn't provided. Provide the missing context and re-dispatch.

**BLOCKED:** The implementer cannot complete the task. Assess the blocker:
1. If it's a context problem, provide more context and re-dispatch
2. If the task requires more capability, re-dispatch with a more capable model
3. If the task is too large, break it into smaller pieces
4. If the plan itself is wrong, escalate to the user

**Never** ignore an escalation or force the same agent to retry without changes.

### Two-Stage Review

After each implementation, run two reviews in sequence:

**Stage 1: Spec Compliance Review** — Did the implementer build exactly what was requested?
- Read the actual code, don't trust the implementer's report
- Compare implementation to requirements line by line
- Check: missing requirements, extra work, misunderstandings
- Use `references/spec-reviewer-prompt.md`

**Stage 2: Code Quality Review** — Is the code well-built?
- Only dispatch after spec compliance passes
- Check: single responsibility, clear interfaces, follows patterns, testable
- Use `references/code-quality-reviewer-prompt.md`

Both reviews must pass before moving to the next task.

### When to interrupt the user

Only interrupt when:

- a key business decision cannot be inferred
- a real high-risk action requires confirmation (risk level = critical)
- external credentials, permissions, or accounts are missing
- the environment is unavailable and cannot reasonably be repaired
- QA fails repeatedly (3+ iterations) and root cause remains unclear
- request state is damaged and cannot be repaired safely

If the user says `继续`, `接着做`, or resumes from a handoff, read `handoff.md` first, then prefer execution over re-explaining status.

## Stage Transition Contract

The request must advance through these stages:

```text
requirement_clarification
→ requirements
→ acceptance
→ plan
→ implementation
→ spec_compliance_review
→ code_quality_review
→ ui_review            (frontend tasks only)
→ verification
→ qa
→ final_handoff
```

Each stage must update request-local state before advancing. Skip `ui_review` for backend-only tasks.

### 1. `requirement_clarification`

Exit only when:

- the objective is clear enough to draft requirements
- blocking business ambiguities are either resolved or recorded

Before leaving this stage, update:

- `current_stage`
- `next_action`
- `remaining_stages`
- `unfinished_reasons`

### 2. `requirements`

Exit only when:

- `requirements.md` is materially complete
- unresolved blockers are either answered or explicitly marked

Before leaving this stage, update:

- `completed_stages`
- `last_completed_action`
- `next_action`
- `unfinished_reasons`

### 3. `acceptance`

Exit only when:

- `acceptance.md` is testable and mapped to requirements
- acceptance blockers are resolved or explicitly recorded

Before leaving this stage, update:

- `completed_stages`
- `last_completed_action`
- `next_action`
- `unfinished_reasons`

### 4. `plan`

Exit only when:

- `plan.md` defines executable scope
- non-scope and validation approach are clear

Before leaving this stage, update:

- `completed_stages`
- `last_completed_action`
- `next_action`
- `unfinished_reasons`

### 5. `implementation`

**This stage MUST be delegated to a subagent via the Agent tool. The Orchestrator must not write or modify source code directly. High/critical risk tasks MUST use `isolation="worktree"`.**

Exit only when:

- implementer reports DONE or DONE_WITH_CONCERNS
- implementation notes are updated

Before leaving this stage, update:

- `implementation_status`
- `last_completed_action`
- `completed_stages`
- `next_action`
- `unfinished_reasons`

### 6. `spec_compliance_review`

**This stage MUST be delegated to a subagent via the Agent tool. Use `references/spec-reviewer-prompt.md`.**

Exit only when:

- reviewer reports PASS
- or blocking findings are resolved and re-reviewed

Before leaving this stage, update:

- `review_status`
- `completed_stages`
- `next_action`
- `unfinished_reasons`

### 7. `code_quality_review`

**This stage MUST be delegated to a subagent via the Agent tool. Use `references/code-quality-reviewer-prompt.md`. Only enter after spec compliance review passes.**

Exit only when:

- reviewer reports no Critical issues
- Important issues are resolved or explicitly deferred

Before leaving this stage, update:

- `review_status`
- `completed_stages`
- `next_action`
- `unfinished_reasons`

### 8. `ui_review` (frontend tasks only)

**This stage MUST be delegated to a subagent via the Agent tool. Use `references/ui-reviewer-prompt.md`. Only dispatch for tasks that include frontend UI work. Skip for backend-only tasks.**

Exit only when:

- reviewer reports PASS (AI Slop Score < 5)
- or Critical issues are fixed and re-reviewed

Before leaving this stage, update:

- `review_status`
- `completed_stages`
- `next_action`
- `unfinished_reasons`

### 9. `verification`

**This stage MUST be delegated to a subagent via the Agent tool. The Orchestrator must not run tests, lint, or build commands directly.**

Exit only when:

- targeted test / lint / build checks for the implementation package have run
- failures are either fixed or recorded as blockers

Before leaving this stage, update:

- `last_completed_action`
- `completed_stages`
- `next_action`
- `unfinished_reasons`
- `evidence_bundle` (record verification evidence)

### 10. `qa`

**This stage MUST be delegated to a subagent via the Agent tool. The Orchestrator must not verify acceptance criteria directly.**

Exit only when:

- required QA has passed
- or a legitimate blocker is recorded

Before leaving this stage, update:

- `qa_status`
- `completed_stages`
- `next_action`
- `unfinished_reasons`
- `completion_guard`

### 11. `final_handoff`

Enter only when:

- `remaining_stages` is empty
- `unfinished_reasons` is empty
- `completion_guard.definition_of_done_satisfied` is `true`
- `evidence_bundle` has fresh verification evidence
- final stop audit passes

If any of the above is false, do not final. Continue execution or report a real blocker.

## Checkpoint and Resume Protocol

### Checkpoint Rule

After each completed stage, refresh `handoff.md` with:

- current objective
- current stage
- completed stages
- remaining stages
- last completed action
- next action
- why final is not allowed yet

Do not reserve `handoff.md` only for pause or cancel. It is also a recovery checkpoint.

### Resume Protocol

When the user says `继续`, `接着做`, or the context has been reset:

1. Read `handoff.md` first
2. Read `state.json` to confirm current stage
3. Compare what handoff.md claims with what state.json shows
4. If they disagree, pause and ask the user for direction
5. If they agree, resume from the recorded `next_action`

**Never resume from memory alone.** Always read the checkpoint files.

### Drift Check

After each stage, ask:

1. Does this work still serve the original request intent?
2. Is the implementation staying inside the agreed scope?
3. Have requirements changed since we started?
4. Is the risk level still accurate?

If drift is detected, pause and report to the user.

## State Update Rule

When a stage finishes:

- append the finished stage to `completed_stages` if needed
- remove the finished stage from `remaining_stages`
- set `current_stage` to the next stage
- set `last_completed_action` to a factual summary of what was done
- set `next_action` to the next executable step
- set `next_action_executable` to `true` only when that step can run now
- remove resolved items from `unfinished_reasons`
- add new blockers to `unfinished_reasons`
- set `completion_guard.implementation_complete` only when implementation is actually complete
- set `completion_guard.qa_passed` only when required QA has passed
- set `completion_guard.definition_of_done_satisfied` only when all done conditions are satisfied

Do not advance a stage before updating state.

## Request Runtime Truth

Use only:

```text
docs/agent/requests/<request_id>/state.json
```

Do not rely on global runtime files such as `docs/agent/current.md` or `docs/agent/workflow-state.json`.

## Subagent Policy

Heavy-workflow requests must enforce independent roles based on risk:

- `critical`: Spec Review, Code Quality Review, UI Review (frontend), Implementation, Verification, QA all required; Implementation uses worktree isolation
- `high`: Spec Review, Code Quality Review, UI Review (frontend), Implementation, Verification, QA all required; Implementation uses worktree isolation
- `medium`: Implementation, Verification, and QA required; Reviews required for security, architecture, state, or data-boundary changes; UI Review for frontend tasks; no worktree needed

When a role is required, the Orchestrator **must** dispatch a subagent via the Agent tool. The Orchestrator must never simulate that role by reading code or running commands directly.

### Isolation Rules

- `critical` risk: Implementation agent MUST use `isolation="worktree"`
- `high` risk: Implementation agent MUST use `isolation="worktree"`
- `medium` risk: No worktree needed, share working directory
- Review, Verification, QA agents: Never need worktree (read-only or test-only)

## Suggested Script

When shell execution is appropriate, use:

```bash
python skills/agent-workflow-start/scripts/start_agent_workflow.py --project-root . --title "<request title>"
```

Provide `--thread-id` when the runtime exposes one.

## Completion Standard

`agent-workflow-start` is complete only when the request has either:

- finished successfully
- reached a legitimate blocked state
- been paused or canceled explicitly

Do not treat a recorded `next_action` as a valid stopping point if it is safe and executable.

## Forbidden Stop Patterns

Do not end the turn with only:

- a progress summary
- a recommendation
- a status block
- a next-step note
- a handoff note
- a "should I continue" question

while safe executable backlog still exists.

### The Rule

If the current stage is complete and the next stage is safe and executable, the orchestrator's turn must end with an Agent tool call delegating to the next subagent.

A turn that does not contain an Agent tool call or a user-facing question is a wasted turn.
