#!/usr/bin/env python3
"""
Claude Code hook that turns the Orchestrator rules into hard constraints.

Installed by `init_agent_workflow.py` into `scripts/agent/agent_workflow_guard.py`
and registered in `.claude/settings.json` for these events:

  PreToolUse   main thread bound to an active request may not touch source code
  PostToolUse  binds the session to a request right after `start_agent_workflow.py` runs
  Stop         blocks a premature stop while the request still has executable work

The hook reads the event JSON from stdin. It only ever constrains the *main
thread* of a session that is bound to an active request. Subagent tool calls
(input carries `agent_id`) and unbound sessions are never touched.

Every decision is appended to `docs/agent/requests/<id>/metrics.jsonl`, which
`workflow_metrics.py` aggregates into effectiveness data.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path


AGENT_TOOLS = {"Agent", "Task"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob", "LS"}

DEFAULT_GUARD = {
    "enabled": True,
    "block_source_reads": True,
    # Project-relative globs the Orchestrator may read inside the project.
    "allowed_read_globs": [
        "docs/agent/**",
        "AGENTS.md",
        "CLAUDE.md",
        "README*",
        ".codex/workflow/**",
    ],
    # Project-relative globs the Orchestrator may write inside the project.
    "allowed_write_globs": ["docs/agent/**"],
    # Regexes; every segment of a Bash command must match one of these.
    "allowed_bash_patterns": [
        r"^(python3?|node)\s+\S*(start_agent_workflow|init_agent_workflow|workflow_metrics)\.py\b",
        r"^(node\s+)?\S*stop-audit\.js\b",
        r"^git\s+(status|log|branch|rev-parse|worktree\s+list)\b",
        r"^(ls|pwd|date|echo)\b",
        r"^cat\s+\S*docs/agent/\S+$",
    ],
    "block_premature_stop": True,
}

START_SCRIPT_RE = re.compile(r"start_agent_workflow\.py")
CREATED_RE = re.compile(r"docs/agent/requests/([^/\s]+)/")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_project_root(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        if (candidate / ".codex/workflow/project.json").exists():
            return candidate
    return None


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def guard_config(project_root: Path) -> dict:
    config = dict(DEFAULT_GUARD)
    overrides = load_json(project_root / ".codex/workflow/project.json").get("orchestrator_guard")
    if isinstance(overrides, dict):
        config.update(overrides)
    return config


def find_bound_request(project_root: Path, session_id: str | None) -> tuple[Path, dict] | None:
    if not session_id:
        return None
    requests_dir = project_root / "docs/agent/requests"
    if not requests_dir.is_dir():
        return None
    for state_path in sorted(requests_dir.glob("*/state.json")):
        state = load_json(state_path)
        if (state.get("thread_binding") or {}).get("thread_id") == session_id:
            return state_path, state
    return None


def request_is_active(state: dict) -> bool:
    if state.get("canceled") or state.get("paused"):
        return False
    finished = state.get("stop_allowed") is True and not state.get("remaining_stages")
    return not finished


def log_event(state_path: Path, event: dict) -> None:
    event = {"at": now_iso(), **event}
    try:
        with (state_path.parent / "metrics.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def relative_to_project(project_root: Path, raw: str | None, cwd: Path) -> str | None:
    """Project-relative POSIX path, or None when the path lies outside the project."""
    if not raw:
        raw = str(cwd)
    path = Path(raw)
    if not path.is_absolute():
        path = cwd / path
    try:
        rel = Path(os.path.normpath(path)).relative_to(project_root)
    except ValueError:
        return None
    return rel.as_posix() or "."


def matches_any(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pattern) or rel == pattern.rstrip("/*") for pattern in globs)


def split_bash_segments(command: str) -> list[str]:
    segments = re.split(r"\s*(?:&&|\|\||;|\||\n)\s*", command.strip())
    return [segment for segment in segments if segment]


def check_bash(command: str, config: dict) -> str | None:
    if re.search(r"(^|[^>])>{1,2}(?!&)", command) or "$(" in command or "`" in command:
        return "output redirection and command substitution are not allowed for the Orchestrator"
    patterns = [re.compile(p) for p in config["allowed_bash_patterns"]]
    for segment in split_bash_segments(command):
        try:
            normalized = " ".join(shlex.split(segment))
        except ValueError:
            normalized = segment
        if not any(p.search(normalized) for p in patterns):
            return f"command segment `{segment}` is not on the Orchestrator allowlist"
    return None


def evaluate_pre_tool_use(payload: dict, project_root: Path, state: dict, config: dict) -> str | None:
    """Return a denial reason, or None to allow."""
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or project_root)

    if tool in AGENT_TOOLS:
        return None

    if tool in WRITE_TOOLS:
        raw = tool_input.get("file_path") or tool_input.get("notebook_path")
        rel = relative_to_project(project_root, raw, cwd)
        if rel is None or matches_any(rel, config["allowed_write_globs"]):
            return None
        return f"the Orchestrator may not modify `{rel}`; dispatch an implementation subagent"

    if tool in READ_TOOLS:
        if not config["block_source_reads"]:
            return None
        raw = tool_input.get("file_path") or tool_input.get("path")
        rel = relative_to_project(project_root, raw, cwd)
        if rel is None:
            return None
        if tool == "Glob" and rel == "." and tool_input.get("pattern"):
            rel = tool_input["pattern"].lstrip("./")
        if matches_any(rel, config["allowed_read_globs"]):
            return None
        return f"the Orchestrator may not read `{rel}`; dispatch a subagent to inspect source code"

    if tool == "Bash":
        reason = check_bash(tool_input.get("command", ""), config)
        if reason:
            return f"{reason}; dispatch a subagent to run builds, tests, or code inspection"
        return None

    return None


def handle_pre_tool_use(payload: dict, project_root: Path) -> dict | None:
    if payload.get("agent_id"):
        return None
    config = guard_config(project_root)
    if not config.get("enabled", True):
        return None
    bound = find_bound_request(project_root, payload.get("session_id"))
    if not bound:
        return None
    state_path, state = bound
    if not request_is_active(state):
        return None

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    reason = evaluate_pre_tool_use(payload, project_root, state, config)

    if tool in AGENT_TOOLS:
        log_event(
            state_path,
            {
                "type": "subagent_dispatch",
                "stage": state.get("current_stage"),
                "subagent_type": tool_input.get("subagent_type"),
                "description": tool_input.get("description"),
            },
        )
    if reason is None:
        return None

    log_event(
        state_path,
        {"type": "guard_block", "stage": state.get("current_stage"), "tool": tool, "reason": reason},
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"agent-workflow guard: {reason}.",
        }
    }


def handle_post_tool_use(payload: dict, project_root: Path) -> dict | None:
    if payload.get("agent_id") or payload.get("tool_name") != "Bash":
        return None
    command = (payload.get("tool_input") or {}).get("command", "")
    if not START_SCRIPT_RE.search(command):
        return None
    match = CREATED_RE.search(json.dumps(payload.get("tool_response"), ensure_ascii=False))
    session_id = payload.get("session_id")
    if not match or not session_id:
        return None

    request_id = match.group(1)
    state_path = project_root / "docs/agent/requests" / request_id / "state.json"
    state = load_json(state_path)
    if not state or (state.get("thread_binding") or {}).get("thread_id"):
        return None

    binding = {"thread_id": session_id, "binding_mode": "hook", "bound_at": now_iso()}
    state["thread_binding"] = binding
    state["updated_at"] = now_iso()
    write_json(state_path, state)

    index_path = project_root / "docs/agent/request-index.json"
    index = load_json(index_path)
    if request_id in index.get("requests", {}):
        index["requests"][request_id]["thread_binding"] = binding
        write_json(index_path, index)

    log_event(
        state_path,
        {"type": "bound", "session_id": session_id, "transcript_path": payload.get("transcript_path")},
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"agent-workflow: this session is now bound to request {request_id}. "
                "The Orchestrator guard is active: source reads/writes and non-workflow shell "
                "commands from the main thread will be denied. Use subagents."
            ),
        }
    }


def handle_stop(payload: dict, project_root: Path) -> dict | None:
    if payload.get("agent_id") or payload.get("stop_hook_active"):
        return None
    config = guard_config(project_root)
    if not config.get("enabled", True) or not config.get("block_premature_stop", True):
        return None
    bound = find_bound_request(project_root, payload.get("session_id"))
    if not bound:
        return None
    state_path, state = bound
    if not request_is_active(state) or state.get("blocked"):
        return None
    if state.get("requires_user_confirmation") or not state.get("next_action_executable"):
        return None

    log_event(state_path, {"type": "premature_stop_blocked", "stage": state.get("current_stage")})
    return {
        "decision": "block",
        "reason": (
            "agent-workflow guard: state.json says next_action_executable=true and no user "
            f"confirmation is pending (next_action: {state.get('next_action')!r}). Continue the "
            "workflow, or update state.json to record a real blocker or confirmation boundary."
        ),
    }


HANDLERS = {
    "PreToolUse": handle_pre_tool_use,
    "PostToolUse": handle_post_tool_use,
    "Stop": handle_stop,
}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    handler = HANDLERS.get(payload.get("hook_event_name", ""))
    if handler is None:
        return 0
    start = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    project_root = find_project_root(start.resolve())
    if project_root is None:
        return 0
    result = handler(payload, project_root)
    if result is not None:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
