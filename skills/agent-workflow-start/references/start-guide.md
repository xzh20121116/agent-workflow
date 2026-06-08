# Agent Workflow Start Guide

## What this does

`agent-workflow-start` is the request-level entry point for the heavy workflow.

It creates one request in one new thread, then drives that request forward until completion or a real blocker.

## What this does not do

- It does not initialize the project workflow.
- It does not create multiple requests at once.
- It does not depend on global runtime files such as `current.md` or `workflow-state.json`.

## Request-local truth

The request-local `state.json` is the only writable runtime truth:

```text
docs/agent/requests/<request_id>/state.json
```

## Orchestrator role

The main thread is an **Orchestrator**. It never touches code directly.

| Stage | Who does it | Agent tool? |
|-------|------------|-------------|
| requirement_clarification | Orchestrator (talks to user) | No |
| requirements | Orchestrator (writes requirements.md) | No |
| acceptance | Orchestrator (writes acceptance.md) | No |
| plan | Orchestrator (writes plan.md) | No |
| implementation | Subagent | Yes (worktree if high/critical) |
| spec_compliance_review | Subagent | Yes |
| code_quality_review | Subagent | Yes |
| verification | Subagent | Yes |
| qa | Subagent | Yes |
| final_handoff | Orchestrator (reports to user) | No |

## SubagentContextPacket

Every subagent prompt must be self-contained. Build a SubagentContextPacket with:
- Task, Goal, Stop condition
- Relevant files, Known facts, Non-goals
- Expected output, Verification expected, Unsafe assumptions

Use the prompt templates in `references/` for each role.

## Implementer status handling

| Status | Action |
|--------|--------|
| DONE | Proceed to spec compliance review |
| DONE_WITH_CONCERNS | Read concerns, then proceed to review |
| NEEDS_CONTEXT | Provide missing context, re-dispatch |
| BLOCKED | Assess: context? capability? plan? escalate if needed |

## Two-stage review

After each implementation:
1. **Spec compliance review** — did the implementer build exactly what was requested?
2. **Code quality review** — is the code well-built? (only after spec review passes)

## Minimal interruption rule

Once the request starts and the user has confirmed requirements and acceptance, the workflow should keep going.

Do not stop for routine progress updates. Interrupt only for true blockers or real high-risk confirmation boundaries.

## Resume protocol

When resuming (context reset, user says "继续"):
1. Read `handoff.md` first
2. Read `state.json` to confirm current stage
3. Resume from the recorded `next_action`
4. Never resume from memory alone

## Automatic finish contract

After confirmation, the expected path is:

```text
plan (orchestrator writes)
→ implementation (via Agent tool, worktree if high/critical)
→ spec compliance review (via Agent tool)
→ code quality review (via Agent tool)
→ verification (via Agent tool)
→ qa (via Agent tool)
→ fix / re-qa loop (via Agent tool)
→ final handoff (orchestrator reports to user)
```

If the next step is safe and executable, spawn the next subagent immediately instead of returning to the user with a progress-only message.
