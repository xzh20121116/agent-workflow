import sys
import unittest
from datetime import date

from helpers import START_SCRIPT, ProjectTestCase, read_json, run_script

sys.path.insert(0, str(START_SCRIPT.parent))
import start_agent_workflow as start  # noqa: E402

REQUEST_FILES = [
    "requirements.md", "acceptance.md", "plan.md", "risk.md", "review.md", "implementation.md",
    "qa.md", "handoff.md", "decision-log.md", "rollback.md", "state.json",
]


class SlugTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(start.slugify("  User Login 2FA!! "), "user-login-2fa")
        self.assertEqual(start.slugify("添加 手机号"), "添加-手机号")
        self.assertEqual(start.slugify("!!!"), "new-request")

    def test_risk_policy(self):
        for risk in ("critical", "high"):
            policy = start.subagent_policy_for_risk(risk)
            self.assertTrue(policy["spec_review_required"])
            self.assertEqual(policy["implementation_isolation"], "worktree")
        self.assertTrue(start.subagent_policy_for_risk("medium")["qa_required"])
        self.assertFalse(start.subagent_policy_for_risk("low")["qa_required"])


class StartTests(ProjectTestCase):
    def test_requires_initialized_project(self):
        result = run_script(START_SCRIPT, "--project-root", str(self.project), "--title", "x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("agent-workflow-init", result.stderr)

    def test_creates_request_workspace_and_index_entry(self):
        self.init_project()
        request_id = self.start_request("User Login 2FA", "--risk-level", "high", "--thread-id", "t-1")
        self.assertEqual(request_id, f"{date.today().isoformat()}-user-login-2fa")

        request_dir = self.project / "docs/agent/requests" / request_id
        for name in REQUEST_FILES:
            self.assertTrue((request_dir / name).exists(), name)
        self.assertTrue((request_dir / "changes").is_dir())

        state = read_json(request_dir / "state.json")
        self.assertEqual(state["risk_level"], "high")
        self.assertEqual(state["current_stage"], "requirement_clarification")
        self.assertEqual(state["remaining_stages"][-1], "final_handoff")
        self.assertEqual(state["thread_binding"]["thread_id"], "t-1")
        self.assertEqual(state["thread_binding"]["binding_mode"], "hard")
        self.assertFalse(state["stop_allowed"])

        index = read_json(self.project / "docs/agent/request-index.json")
        self.assertEqual(index["requests"][request_id]["risk_level"], "high")

    def test_duplicate_titles_get_unique_ids(self):
        self.init_project()
        first = self.start_request("Same")
        second = self.start_request("Same")
        third = self.start_request("Same")
        self.assertEqual(second, f"{first}-02")
        self.assertEqual(third, f"{first}-03")
        self.assertEqual(len(read_json(self.project / "docs/agent/request-index.json")["requests"]), 3)

    def test_unbound_request_uses_manual_binding(self):
        self.init_project()
        request_id = self.start_request("No thread")
        state = read_json(self.project / "docs/agent/requests" / request_id / "state.json")
        self.assertIsNone(state["thread_binding"]["thread_id"])
        self.assertEqual(state["thread_binding"]["binding_mode"], "manual")
