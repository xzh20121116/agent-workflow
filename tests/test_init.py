import json

from helpers import INIT_SCRIPT, ProjectTestCase, read_json, run_script


class InitTests(ProjectTestCase):
    def test_creates_project_layout(self):
        self.init_project()
        for rel in [
            "AGENTS.md",
            ".codex/workflow/project.json",
            ".codex/agents/review.toml",
            ".codex/agents/implementation.toml",
            ".codex/agents/qa.toml",
            "docs/agent/README.md",
            "docs/agent/OPERATION.md",
            "docs/agent/request-index.json",
            "docs/agent/templates/request/state.json.template",
            "scripts/agent/stop-audit.js",
            "scripts/agent/agent_workflow_guard.py",
            "scripts/agent/workflow_metrics.py",
        ]:
            self.assertTrue((self.project / rel).exists(), rel)
        self.assertTrue((self.project / "docs/agent/requests").is_dir())

        project = read_json(self.project / ".codex/workflow/project.json")
        self.assertTrue(project["initialized"])
        self.assertEqual(project["version"], "3.0")
        self.assertTrue(project["orchestrator_guard"]["enabled"])

    def test_state_template_is_valid_json(self):
        self.init_project()
        template = read_json(self.project / "docs/agent/templates/request/state.json.template")
        self.assertEqual(template["current_stage"], "requirement_clarification")

    def test_reconcile_preserves_user_files_and_requests(self):
        self.init_project()
        (self.project / "AGENTS.md").write_text("custom\n", encoding="utf-8")
        index_path = self.project / "docs/agent/request-index.json"
        index = read_json(index_path)
        index["requests"]["r1"] = {"title": "keep me"}
        index_path.write_text(json.dumps(index), encoding="utf-8")
        created_at = read_json(self.project / ".codex/workflow/project.json")["created_at"]

        self.init_project()

        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "custom\n")
        self.assertEqual(read_json(index_path)["requests"]["r1"]["title"], "keep me")
        self.assertEqual(read_json(self.project / ".codex/workflow/project.json")["created_at"], created_at)

    def test_overwrite_agents_flag(self):
        self.init_project()
        (self.project / "AGENTS.md").write_text("custom\n", encoding="utf-8")
        self.init_project("--overwrite-agents")
        self.assertIn("Orchestrator", (self.project / "AGENTS.md").read_text(encoding="utf-8"))

    def test_registers_claude_hooks_idempotently_and_keeps_other_settings(self):
        settings_path = self.project / ".claude/settings.json"
        settings_path.parent.mkdir()
        settings_path.write_text(
            json.dumps({"permissions": {"allow": ["Bash(ls)"]}, "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo mine"}]}]}}),
            encoding="utf-8",
        )
        self.init_project()
        self.init_project()

        settings = read_json(settings_path)
        self.assertEqual(settings["permissions"], {"allow": ["Bash(ls)"]})
        for event in ("PreToolUse", "PostToolUse", "Stop"):
            guard_groups = [
                g for g in settings["hooks"][event] if "agent_workflow_guard.py" in g["hooks"][0]["command"]
            ]
            self.assertEqual(len(guard_groups), 1, event)
        self.assertIn("echo mine", json.dumps(settings["hooks"]["Stop"]))

    def test_no_claude_hooks_flag(self):
        self.init_project("--no-claude-hooks")
        self.assertFalse((self.project / ".claude/settings.json").exists())

    def test_invalid_settings_json_is_not_overwritten(self):
        settings_path = self.project / ".claude/settings.json"
        settings_path.parent.mkdir()
        settings_path.write_text("{broken", encoding="utf-8")
        result = run_script(INIT_SCRIPT, "--project-root", str(self.project))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(settings_path.read_text(encoding="utf-8"), "{broken")

    def test_new_request_flag_is_rejected(self):
        result = run_script(INIT_SCRIPT, "--project-root", str(self.project), "--new-request", "x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("agent-workflow-start", result.stderr)
