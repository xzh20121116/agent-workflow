# Agent Workflow Guide

## Mental model

This is a heavy-duty workflow for substantial project work.

Project setup and request execution are split:

- `agent-workflow-init`: project-level bootstrap / reconcile only
- `agent-workflow-start`: request creation plus end-to-end execution

## Orchestrator model

The main thread is an Orchestrator. It:

- Talks to the user (requirement clarification, confirmations, final handoff)
- Reads and updates `state.json`
- Dispatches subagents via the Agent tool
- Synthesizes subagent results and decides next action

It NEVER reads/modifies source code, runs tests, performs review, or executes QA directly.

## Thread model

- One requirement thread maps to one request.
- Each new requirement should start in a new thread.
- A thread should not switch across requests mid-run.

## Source of truth

Project level:

- `.codex/workflow/project.json`
- `docs/agent/request-index.json`

Request level:

- `docs/agent/requests/<request_id>/state.json`
- `docs/agent/requests/<request_id>/handoff.md` (checkpoint)
- `requirements.md`
- `acceptance.md`
- `decision-log.md`

The request `state.json` is the only writable runtime truth.

## Subagent dispatch

Each stage that touches code or tests is delegated to a subagent via the Agent tool.

Prompt templates live in `agent-workflow-start/references/`:

- `implementer-prompt.md`
- `spec-reviewer-prompt.md`
- `code-quality-reviewer-prompt.md`
- `verification-prompt.md`
- `qa-prompt.md`

Every subagent prompt must be self-contained via SubagentContextPacket.

## Implementer status

| Status | Action |
|--------|--------|
| DONE | Proceed to spec compliance review |
| DONE_WITH_CONCERNS | Read concerns, then proceed |
| NEEDS_CONTEXT | Provide missing context, re-dispatch |
| BLOCKED | Assess and escalate if needed |

## Stage order

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

## Two-stage review

After each implementation:
1. Spec compliance review — did the implementer build exactly what was requested?
2. Code quality review — is the code well-built? (only after spec review passes)

## Legacy files

These old global runtime files should no longer be used as writable runtime truth:

- `docs/agent/current.md`
- `docs/agent/workflow-state.json`
- `docs/agent/router-log.md`

They may exist during migration, but new workflow runs should not depend on them.

## Execution rule

After `agent-workflow-start` creates a request and the user confirms requirements and acceptance, execution should continue automatically until:

- completion
- a real blocker
- a true high-risk confirmation boundary
- pause / cancel requested by the user

Do not interrupt the user for routine progress updates.

## Resume protocol

When resuming (context reset, user says "继续"):
1. Read `handoff.md` first
2. Read `state.json` to confirm current stage
3. Resume from the recorded `next_action`
4. Never resume from memory alone

## Multi-host support

Skills are installed in `~/.codex/skills/` (canonical). For Claude Code, run `install_symlinks.sh` to create symlinks in `~/.claude/skills/`.
