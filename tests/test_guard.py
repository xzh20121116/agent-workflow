import json
import os

from helpers import ProjectTestCase, read_json, run_script

SESSION = "session-abc"


class GuardTests(ProjectTestCase):
    def setUp(self):
        super().setUp()
        self.init_project()
        self.guard = self.project / "scripts/agent/agent_workflow_guard.py"
        self.request_id = self.start_request("Guarded", "--thread-id", SESSION)
        self.request_dir = self.project / "docs/agent/requests" / self.request_id
        self.state_path = self.request_dir / "state.json"

    def hook(self, event, **fields):
        payload = {"hook_event_name": event, "session_id": SESSION, "cwd": str(self.project), **fields}
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.project)}
        result = run_script(self.guard, stdin=json.dumps(payload), env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def pre(self, tool, **tool_input):
        return self.hook("PreToolUse", tool_name=tool, tool_input=tool_input)

    def assert_denied(self, decision):
        self.assertIsNotNone(decision)
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def update_state(self, **changes):
        state = read_json(self.state_path)
        state.update(changes)
        self.state_path.write_text(json.dumps(state), encoding="utf-8")

    def events(self):
        path = self.request_dir / "metrics.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    # PreToolUse

    def test_blocks_source_writes_and_reads(self):
        self.assert_denied(self.pre("Edit", file_path=str(self.project / "src/app.py")))
        self.assert_denied(self.pre("Write", file_path="src/new.py"))
        self.assert_denied(self.pre("Read", file_path=str(self.project / "src/app.py")))
        self.assert_denied(self.pre("Grep", pattern="TODO"))
        self.assert_denied(self.pre("Glob", pattern="**/*.py"))

    def test_allows_workflow_docs(self):
        self.assertIsNone(self.pre("Write", file_path=str(self.request_dir / "requirements.md")))
        self.assertIsNone(self.pre("Edit", file_path=str(self.state_path)))
        self.assertIsNone(self.pre("Read", file_path=str(self.project / "AGENTS.md")))
        self.assertIsNone(self.pre("Grep", pattern="stage", path="docs/agent"))

    def test_allows_files_outside_project(self):
        self.assertIsNone(self.pre("Read", file_path="/home/someone/.claude/skills/x/SKILL.md"))

    def test_bash_allowlist(self):
        self.assertIsNone(self.pre("Bash", command=f"node scripts/agent/stop-audit.js --request-id {self.request_id}"))
        self.assertIsNone(self.pre("Bash", command="git status && git log --oneline -5"))
        self.assertIsNone(self.pre("Bash", command="python3 scripts/agent/workflow_metrics.py --project-root ."))
        self.assert_denied(self.pre("Bash", command="npm test"))
        self.assert_denied(self.pre("Bash", command="git status && pytest"))
        self.assert_denied(self.pre("Bash", command="cat src/app.py"))
        self.assert_denied(self.pre("Bash", command="echo hi > src/app.py"))
        self.assert_denied(self.pre("Bash", command="echo $(cat src/app.py)"))

    def test_agent_dispatch_allowed_and_logged(self):
        self.assertIsNone(self.pre("Agent", subagent_type="general-purpose", description="Implement FR-1"))
        dispatches = [e for e in self.events() if e["type"] == "subagent_dispatch"]
        self.assertEqual(len(dispatches), 1)
        self.assertEqual(dispatches[0]["description"], "Implement FR-1")

    def test_blocks_are_logged(self):
        self.pre("Bash", command="npm test")
        blocks = [e for e in self.events() if e["type"] == "guard_block"]
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["tool"], "Bash")

    def test_subagents_are_never_constrained(self):
        decision = self.hook("PreToolUse", agent_id="agent-1", tool_name="Edit", tool_input={"file_path": "src/app.py"})
        self.assertIsNone(decision)

    def test_unbound_session_is_not_constrained(self):
        decision = self.hook("PreToolUse", session_id="other", tool_name="Edit", tool_input={"file_path": "src/app.py"})
        self.assertIsNone(decision)

    def test_inactive_requests_are_not_constrained(self):
        self.update_state(paused=True)
        self.assertIsNone(self.pre("Edit", file_path="src/app.py"))
        self.update_state(paused=False, stop_allowed=True, remaining_stages=[])
        self.assertIsNone(self.pre("Edit", file_path="src/app.py"))

    def test_guard_can_be_disabled_or_relaxed(self):
        project_json = self.project / ".codex/workflow/project.json"
        project = read_json(project_json)
        project["orchestrator_guard"] = {"block_source_reads": False}
        project_json.write_text(json.dumps(project), encoding="utf-8")
        self.assertIsNone(self.pre("Read", file_path="src/app.py"))
        self.assert_denied(self.pre("Edit", file_path="src/app.py"))

        project["orchestrator_guard"] = {"enabled": False}
        project_json.write_text(json.dumps(project), encoding="utf-8")
        self.assertIsNone(self.pre("Edit", file_path="src/app.py"))

    def test_ignores_projects_without_workflow(self):
        (self.project / ".codex/workflow/project.json").unlink()
        self.assertIsNone(self.pre("Edit", file_path="src/app.py"))

    # PostToolUse binding

    def test_binds_session_after_start_script(self):
        request_id = self.start_request("Bind me")
        decision = self.hook(
            "PostToolUse",
            session_id="new-session",
            transcript_path="/tmp/t.jsonl",
            tool_name="Bash",
            tool_input={"command": 'python3 start_agent_workflow.py --title "Bind me"'},
            tool_response={"stdout": f"Created request: docs/agent/requests/{request_id}/\n", "stderr": ""},
        )
        self.assertIn(request_id, decision["hookSpecificOutput"]["additionalContext"])

        state = read_json(self.project / "docs/agent/requests" / request_id / "state.json")
        self.assertEqual(state["thread_binding"]["thread_id"], "new-session")
        index = read_json(self.project / "docs/agent/request-index.json")
        self.assertEqual(index["requests"][request_id]["thread_binding"]["thread_id"], "new-session")

        # the newly bound session is now guarded
        blocked = self.hook("PreToolUse", session_id="new-session", tool_name="Edit", tool_input={"file_path": "src/a.py"})
        self.assert_denied(blocked)

    def test_does_not_rebind_existing_binding(self):
        decision = self.hook(
            "PostToolUse",
            session_id="intruder",
            tool_name="Bash",
            tool_input={"command": "python3 start_agent_workflow.py --title x"},
            tool_response={"stdout": f"Created request: docs/agent/requests/{self.request_id}/"},
        )
        self.assertIsNone(decision)
        self.assertEqual(read_json(self.state_path)["thread_binding"]["thread_id"], SESSION)

    # Stop

    def test_stop_allowed_while_waiting_for_user(self):
        self.assertIsNone(self.hook("Stop"))

    def test_premature_stop_blocked(self):
        self.update_state(requires_user_confirmation=False, next_action_executable=True, next_action="dispatch_qa")
        decision = self.hook("Stop")
        self.assertEqual(decision["decision"], "block")
        self.assertIn("dispatch_qa", decision["reason"])
        self.assertEqual([e["type"] for e in self.events()], ["premature_stop_blocked"])

    def test_stop_not_blocked_twice_or_when_blocked(self):
        self.update_state(requires_user_confirmation=False, next_action_executable=True)
        self.assertIsNone(self.hook("Stop", stop_hook_active=True))
        self.update_state(blocked=True)
        self.assertIsNone(self.hook("Stop"))
