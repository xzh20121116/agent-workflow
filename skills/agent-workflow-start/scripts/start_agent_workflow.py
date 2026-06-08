#!/usr/bin/env python3
"""
Create one heavy-workflow request workspace and bind it to the current thread.

Usage:

  python start_agent_workflow.py --project-root . --title "User login 2FA"
  python start_agent_workflow.py --project-root . --title "User login 2FA" --slug user-login-2fa --thread-id thread-123
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "new-request"


def unique_request_id(requests_dir: Path, title: str, explicit_slug: str | None) -> str:
    today = date.today().isoformat()
    slug = slugify(explicit_slug or title)
    base = f"{today}-{slug}"
    candidate = base
    counter = 2
    while (requests_dir / candidate).exists():
        candidate = f"{base}-{counter:02d}"
        counter += 1
    return candidate


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_project_metadata(project_root: Path) -> dict:
    project_json = project_root / ".codex/workflow/project.json"
    if not project_json.exists():
        raise SystemExit("Project workflow is not initialized. Run agent-workflow-init first.")
    return json.loads(project_json.read_text(encoding="utf-8"))


def subagent_policy_for_risk(risk_level: str) -> dict:
    if risk_level in {"critical", "high"}:
        return {
            "spec_review_required": True,
            "code_quality_review_required": True,
            "implementation_subagent_required": True,
            "verification_required": True,
            "qa_required": True,
            "implementation_isolation": "worktree",
            "reason": f"{risk_level} risk request",
        }
    if risk_level == "medium":
        return {
            "spec_review_required": False,
            "code_quality_review_required": False,
            "implementation_subagent_required": True,
            "verification_required": True,
            "qa_required": True,
            "implementation_isolation": "none",
            "reason": "medium risk request; reviews required for security, architecture, state, or data-boundary changes",
        }
    return {
        "spec_review_required": False,
        "code_quality_review_required": False,
        "implementation_subagent_required": True,
        "verification_required": False,
        "qa_required": False,
        "implementation_isolation": "none",
        "reason": "exception-only low risk request inside heavy workflow",
    }


def create_request_files(request_dir: Path, request_id: str, title: str, risk_level: str) -> None:
    created = date.today().isoformat()
    files = {
        "requirements.md": f"# Requirements: {title}\n\n- Request ID: `{request_id}`\n- Created at: `{created}`\n\n## Background\n\n## Goals\n\n## Functional Requirements\n\n### FR-1\n\n## Open Questions\n",
        "acceptance.md": f"# Acceptance: {title}\n\n- Request ID: `{request_id}`\n\n## Requirement Mapping\n\n| Requirement ID | Acceptance ID | Priority |\n|---|---|---|\n| FR-1 | AC-1 | Must |\n\n## Acceptance Criteria\n\n### AC-1\n",
        "plan.md": "# Plan\n\n## Scope\n\n## Non-Scope\n\n## Likely Files\n\n## Validation\n",
        "risk.md": f"# Risk\n\n- Risk Level: `{risk_level}`\n\n## Risk Summary\n",
        "review.md": "# Review\n\n## Findings\n",
        "implementation.md": "# Implementation\n\n## Changes\n",
        "qa.md": "# QA\n\n## Acceptance Checks\n",
        "handoff.md": "# Handoff\n\n## Current Objective\n\n## Current Stage\n\n## Completed Stages\n\n## Remaining Stages\n\n## Last Completed Action\n\n## Next Action\n\n## Why Final Is Not Allowed Yet\n",
        "decision-log.md": "# Decision Log\n",
        "rollback.md": "# Rollback\n",
    }
    for filename, content in files.items():
        write_text(request_dir / filename, content)
    (request_dir / "changes").mkdir(parents=True, exist_ok=True)


def create_state(request_id: str, title: str, risk_level: str, request_type: str, thread_id: str | None) -> dict:
    remaining_stages = [
        "requirement_clarification",
        "requirements",
        "acceptance",
        "plan",
        "implementation",
        "spec_compliance_review",
        "code_quality_review",
        "verification",
        "qa",
        "final_handoff",
    ]
    checkpoint_fields = [
        "current objective",
        "current stage",
        "completed stages",
        "remaining stages",
        "last completed action",
        "next action",
        "why final is not allowed yet",
    ]
    return {
        "request_id": request_id,
        "request_title": title,
        "objective": title,
        "definition_of_done": [
            "requirements confirmed",
            "acceptance confirmed",
            "implementation complete",
            "qa passed",
        ],
        "request_type": request_type,
        "risk_level": risk_level,
        "current_stage": "requirement_clarification",
        "stage_status": "in_progress",
        "completed_stages": [],
        "remaining_stages": remaining_stages,
        "stage_transition_contract": {
            "ordered_stages": remaining_stages,
            "checkpoint_required_after_each_stage": True,
            "checkpoint_fields": checkpoint_fields,
            "final_stage_requires": [
                "remaining_stages empty",
                "unfinished_reasons empty",
                "completion_guard.definition_of_done_satisfied true",
                "stop audit passed",
            ],
        },
        "auto_execute_after_confirmation": True,
        "requirements_confirmed": False,
        "acceptance_confirmed": False,
        "review_status": "not_started",
        "implementation_status": "not_started",
        "qa_status": "not_started",
        "paused": False,
        "blocked": False,
        "canceled": False,
        "stop_allowed": False,
        "stop_reason": None,
        "last_completed_action": None,
        "next_action": "clarify_requirements",
        "next_action_executable": True,
        "requires_user_confirmation": True,
        "safe_backlog_candidates": [],
        "safe_backlog_exhausted": True,
        "risk_boundary_next_actions": [],
        "premature_stop_detected": False,
        "unfinished_reasons": [
            "requirements not confirmed",
            "acceptance not confirmed",
            "implementation not complete",
            "qa not passed",
        ],
        "completion_guard": {
            "all_required_docs_present": True,
            "implementation_complete": False,
            "qa_passed": False,
            "definition_of_done_satisfied": False,
            "stage_updates_applied": False,
        },
        "evidence_bundle": {
            "verification_evidence": [],
            "review_evidence": [],
            "qa_evidence": [],
        },
        "drift_check": {
            "last_check_at": None,
            "original_intent": title,
            "drift_detected": False,
            "drift_notes": None,
        },
        "runtime_processes": [],
        "subagent_policy": subagent_policy_for_risk(risk_level),
        "thread_binding": {
            "thread_id": thread_id,
            "binding_mode": "hard" if thread_id else "manual",
            "bound_at": now_iso(),
        },
        "resume_protocol": {
            "read_order": [
                "handoff.md",
                "state.json",
                "decision-log.md",
                "requirements.md",
                "acceptance.md",
                "plan.md",
            ],
            "continue_if_next_action_executable": True,
            "never_resume_from_memory_alone": True,
        },
        "updated_at": now_iso(),
    }


def update_request_index(project_root: Path, state: dict) -> None:
    index_path = project_root / "docs/agent/request-index.json"
    try:
        index_payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        index_payload = {"version": "3.0", "requests": {}}

    index_payload.setdefault("requests", {})
    index_payload["requests"][state["request_id"]] = {
        "title": state["request_title"],
        "current_stage": state["current_stage"],
        "risk_level": state["risk_level"],
        "thread_binding": state["thread_binding"],
        "updated_at": state["updated_at"],
    }
    index_payload["updated_at"] = now_iso()
    write_json(index_path, index_payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug")
    parser.add_argument("--thread-id")
    parser.add_argument("--risk-level", choices=["low", "medium", "high", "critical"], default="medium")
    parser.add_argument("--request-type", default="feature")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    load_project_metadata(project_root)

    requests_dir = project_root / "docs/agent/requests"
    requests_dir.mkdir(parents=True, exist_ok=True)
    request_id = unique_request_id(requests_dir, args.title, args.slug)
    request_dir = requests_dir / request_id
    request_dir.mkdir(parents=True, exist_ok=False)

    create_request_files(request_dir, request_id, args.title, args.risk_level)
    state = create_state(request_id, args.title, args.risk_level, args.request_type, args.thread_id)
    write_json(request_dir / "state.json", state)
    update_request_index(project_root, state)

    print(f"Created request: docs/agent/requests/{request_id}/")


if __name__ == "__main__":
    main()
