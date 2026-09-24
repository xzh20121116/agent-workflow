from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INIT_SCRIPT = REPO_ROOT / "skills/agent-workflow-init/scripts/init_agent_workflow.py"
START_SCRIPT = REPO_ROOT / "skills/agent-workflow-start/scripts/start_agent_workflow.py"


def run_script(script: Path, *args: str, stdin: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ProjectTestCase(unittest.TestCase):
    """Gives each test a fresh temporary project directory."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name).resolve()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def init_project(self, *args: str) -> subprocess.CompletedProcess:
        result = run_script(INIT_SCRIPT, "--project-root", str(self.project), *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def start_request(self, title: str = "Add login", *args: str) -> str:
        result = run_script(START_SCRIPT, "--project-root", str(self.project), "--title", title, *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip().split("docs/agent/requests/")[1].rstrip("/")
