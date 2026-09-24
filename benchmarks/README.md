# Benchmarks

This directory holds a repeatable protocol for measuring whether Agent Workflow actually helps. **No results are published yet.** Numbers get added here only from real runs, following the protocol below.

## Protocol

1. **Pick tasks.** 5–10 real, substantial tasks from one repository (features or bug fixes that touch 3+ files). Write each task as a single fixed prompt and a hidden acceptance checklist.
2. **Two arms, same model, same starting commit.**
   - **Baseline:** plain Claude Code session, the task prompt only.
   - **Workflow:** `agent-workflow-init` done beforehand, then `agent-workflow-start` with the same prompt.
3. **Human input budget.** Answer clarification questions identically in both arms; count every user message after the first prompt.
4. **Score after the agent claims completion** (do not help it further):
   - acceptance checklist items passed (checked by a person or a hidden test suite)
   - defects found by a separate review after completion
   - whether the agent claimed "done" with a failing test
5. **Collect cost and process data** for the workflow arm:

   ```bash
   python3 scripts/agent/workflow_metrics.py --project-root . --tokens --json > run-<task>.json
   ```

   For the baseline arm, sum token usage from its transcript (`~/.claude/projects/.../<session>.jsonl`).

## Results table

| Task | Arm | Acceptance passed | Post-hoc defects | False "done" | User messages | Wall-clock (min) | Tokens | Subagents | Guard blocks |
|------|-----|-------------------|------------------|--------------|---------------|------------------|--------|-----------|--------------|
| _pending_ | baseline | | | | | | | – | – |
| _pending_ | workflow | | | | | | | | |

Report medians across tasks and include the raw `run-*.json` files alongside the table.
