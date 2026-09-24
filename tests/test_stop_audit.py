import json
import shutil
import subprocess
import unittest

from helpers import ProjectTestCase, read_json


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class StopAuditTests(ProjectTestCase):
    def setUp(self):
        super().setUp()
        self.init_project()
        self.request_id = self.start_request("Audit me")
        self.state_path = self.project / "docs/agent/requests" / self.request_id / "state.json"

    def audit(self, *args):
        return subprocess.run(
            ["node", str(self.project / "scripts/agent/stop-audit.js"), "--project-root", str(self.project),
             "--request-id", self.request_id, *args],
            capture_output=True, text=True,
        )

    def update_state(self, **changes):
        state = read_json(self.state_path)
        state.update(changes)
        self.state_path.write_text(json.dumps(state), encoding="utf-8")

    def test_fresh_request_fails_final_audit(self):
        result = self.audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("stop_allowed", result.stderr)

    def test_completed_request_passes_final_audit(self):
        state = read_json(self.state_path)
        self.update_state(
            stop_allowed=True, next_action_executable=False, unfinished_reasons=[], remaining_stages=[],
            implementation_status="completed", qa_status="passed",
            completion_guard={**state["completion_guard"], "definition_of_done_satisfied": True},
        )
        result = self.audit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("stop audit passed", result.stdout)

    def test_required_qa_not_passed_fails(self):
        state = read_json(self.state_path)
        self.update_state(
            stop_allowed=True, next_action_executable=False, unfinished_reasons=[], remaining_stages=[],
            implementation_status="completed", qa_status="failed",
            completion_guard={**state["completion_guard"], "definition_of_done_satisfied": True},
        )
        result = self.audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("qa_status", result.stderr)

    def test_pre_implementation_requires_confirmation(self):
        self.assertEqual(self.audit("--mode", "pre-implementation").returncode, 1)
        self.update_state(requires_user_confirmation=False)
        self.assertEqual(self.audit("--mode", "pre-implementation").returncode, 0)
