#!/usr/bin/env python3
"""
Aggregate effectiveness data for heavy-workflow requests.

Sources (all local, nothing is sent anywhere):

  docs/agent/requests/<id>/state.json     stage progress, evidence bundle
  docs/agent/requests/<id>/metrics.jsonl  events written by agent_workflow_guard.py
  Claude Code transcript (optional)       token usage, when --tokens is passed

Usage:

  python workflow_metrics.py --project-root .
  python workflow_metrics.py --project-root . --tokens
  python workflow_metrics.py --project-root . --json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


USAGE_KEYS = (
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_events(path: Path) -> list[dict]:
    events = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return events
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def transcript_usage(transcript: Path) -> dict:
    """Sum token usage over a transcript and its subagent transcripts, when present."""
    files = [transcript]
    subagent_dir = transcript.with_suffix("") / "subagents"
    if subagent_dir.is_dir():
        files.extend(sorted(subagent_dir.glob("*.jsonl")))

    totals = Counter()
    seen_messages = set()
    for path in files:
        for event in load_events(path):
            message = event.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("usage"), dict):
                continue
            message_id = message.get("id")
            if message_id:
                if message_id in seen_messages:
                    continue
                seen_messages.add(message_id)
            for key in USAGE_KEYS:
                value = message["usage"].get(key)
                if isinstance(value, int):
                    totals[key] += value
    return dict(totals)


def summarize_request(request_dir: Path, with_tokens: bool) -> dict:
    state = load_json(request_dir / "state.json")
    events = load_events(request_dir / "metrics.jsonl")
    counts = Counter(event.get("type") for event in events)
    dispatch_roles = Counter(
        event.get("subagent_type") or "general-purpose"
        for event in events
        if event.get("type") == "subagent_dispatch"
    )
    blocked_tools = Counter(event.get("tool") for event in events if event.get("type") == "guard_block")

    started = parse_time((state.get("thread_binding") or {}).get("bound_at"))
    updated = parse_time(state.get("updated_at"))
    duration_minutes = None
    if started and updated and updated >= started:
        duration_minutes = round((updated - started).total_seconds() / 60, 1)

    evidence = state.get("evidence_bundle") or {}
    summary = {
        "request_id": state.get("request_id", request_dir.name),
        "title": state.get("request_title"),
        "risk_level": state.get("risk_level"),
        "current_stage": state.get("current_stage"),
        "completed_stages": len(state.get("completed_stages") or []),
        "total_stages": len((state.get("stage_transition_contract") or {}).get("ordered_stages") or []),
        "finished": state.get("stop_allowed") is True and not state.get("remaining_stages"),
        "duration_minutes": duration_minutes,
        "subagent_dispatches": sum(dispatch_roles.values()),
        "dispatches_by_role": dict(dispatch_roles),
        "guard_blocks": counts.get("guard_block", 0),
        "guard_blocks_by_tool": dict(blocked_tools),
        "premature_stops_blocked": counts.get("premature_stop_blocked", 0),
        "review_evidence": len(evidence.get("review_evidence") or []),
        "verification_evidence": len(evidence.get("verification_evidence") or []),
        "qa_evidence": len(evidence.get("qa_evidence") or []),
    }

    if with_tokens:
        transcripts = [
            Path(event["transcript_path"])
            for event in events
            if event.get("type") == "bound" and event.get("transcript_path")
        ]
        usage = Counter()
        for transcript in transcripts:
            if transcript.exists():
                usage.update(transcript_usage(transcript))
        summary["tokens"] = dict(usage) if usage else None

    return summary


def collect(project_root: Path, with_tokens: bool) -> dict:
    requests_dir = project_root / "docs/agent/requests"
    requests = []
    if requests_dir.is_dir():
        for request_dir in sorted(p for p in requests_dir.iterdir() if (p / "state.json").exists()):
            requests.append(summarize_request(request_dir, with_tokens))

    totals = {
        "requests": len(requests),
        "finished": sum(1 for r in requests if r["finished"]),
        "subagent_dispatches": sum(r["subagent_dispatches"] for r in requests),
        "guard_blocks": sum(r["guard_blocks"] for r in requests),
        "premature_stops_blocked": sum(r["premature_stops_blocked"] for r in requests),
    }
    durations = [r["duration_minutes"] for r in requests if r["finished"] and r["duration_minutes"] is not None]
    totals["median_finished_duration_minutes"] = sorted(durations)[len(durations) // 2] if durations else None
    return {"totals": totals, "requests": requests}


def format_tokens(tokens: dict | None) -> str:
    if not tokens:
        return "-"
    total = sum(tokens.values())
    return f"{total / 1000:.1f}k"


def render_markdown(report: dict, with_tokens: bool) -> str:
    totals = report["totals"]
    lines = [
        "# Agent Workflow Metrics",
        "",
        f"- Requests: {totals['requests']} ({totals['finished']} finished)",
        f"- Subagent dispatches: {totals['subagent_dispatches']}",
        f"- Orchestrator guard blocks: {totals['guard_blocks']}",
        f"- Premature stops blocked: {totals['premature_stops_blocked']}",
        f"- Median duration of finished requests: "
        + (f"{totals['median_finished_duration_minutes']} min" if totals["median_finished_duration_minutes"] is not None else "-"),
        "",
    ]
    if not report["requests"]:
        lines.append("No requests found.")
        return "\n".join(lines)

    header = ["Request", "Risk", "Stage", "Progress", "Minutes", "Dispatches", "Guard blocks", "Stops blocked", "Evidence (R/V/QA)"]
    if with_tokens:
        header.append("Tokens")
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in report["requests"]:
        row = [
            f"`{r['request_id']}`",
            r["risk_level"] or "-",
            r["current_stage"] or "-",
            f"{r['completed_stages']}/{r['total_stages']}",
            "-" if r["duration_minutes"] is None else str(r["duration_minutes"]),
            str(r["subagent_dispatches"]),
            str(r["guard_blocks"]),
            str(r["premature_stops_blocked"]),
            f"{r['review_evidence']}/{r['verification_evidence']}/{r['qa_evidence']}",
        ]
        if with_tokens:
            row.append(format_tokens(r.get("tokens")))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--tokens", action="store_true", help="Sum token usage from bound Claude Code transcripts")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    args = parser.parse_args()

    report = collect(Path(args.project_root).resolve(), args.tokens)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report, args.tokens))


if __name__ == "__main__":
    main()
