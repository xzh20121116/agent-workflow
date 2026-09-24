import json

from helpers import ProjectTestCase, read_json, run_script


class MetricsTests(ProjectTestCase):
    def setUp(self):
        super().setUp()
        self.init_project()
        self.metrics = self.project / "scripts/agent/workflow_metrics.py"

    def report(self, *args):
        result = run_script(self.metrics, "--project-root", str(self.project), *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_empty_project(self):
        data = json.loads(self.report("--json"))
        self.assertEqual(data["totals"]["requests"], 0)
        self.assertIn("No requests found", self.report())

    def test_aggregates_events_and_tokens(self):
        request_id = self.start_request("Measured", "--thread-id", "s1")
        request_dir = self.project / "docs/agent/requests" / request_id

        transcript = self.project / "session.jsonl"
        usage = {"input_tokens": 100, "output_tokens": 50}
        transcript.write_text(
            "\n".join([
                json.dumps({"message": {"id": "m1", "usage": usage}}),
                json.dumps({"message": {"id": "m1", "usage": usage}}),  # streamed duplicate
                json.dumps({"type": "user"}),
            ]),
            encoding="utf-8",
        )
        subagents = self.project / "session" / "subagents"
        subagents.mkdir(parents=True)
        (subagents / "a.jsonl").write_text(json.dumps({"message": {"id": "m2", "usage": {"output_tokens": 25}}}), encoding="utf-8")

        events = [
            {"type": "bound", "transcript_path": str(transcript)},
            {"type": "subagent_dispatch", "subagent_type": "Explore"},
            {"type": "subagent_dispatch", "subagent_type": None},
            {"type": "guard_block", "tool": "Edit"},
            {"type": "premature_stop_blocked"},
        ]
        (request_dir / "metrics.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\nnot json\n", encoding="utf-8")

        state = read_json(request_dir / "state.json")
        state.update(stop_allowed=True, remaining_stages=[], completed_stages=["a", "b"])
        state["evidence_bundle"]["qa_evidence"] = ["qa.md#AC-1"]
        (request_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")

        data = json.loads(self.report("--json", "--tokens"))
        request = data["requests"][0]
        self.assertTrue(request["finished"])
        self.assertEqual(request["subagent_dispatches"], 2)
        self.assertEqual(request["dispatches_by_role"], {"Explore": 1, "general-purpose": 1})
        self.assertEqual(request["guard_blocks_by_tool"], {"Edit": 1})
        self.assertEqual(request["premature_stops_blocked"], 1)
        self.assertEqual(request["qa_evidence"], 1)
        self.assertEqual(request["tokens"], {"input_tokens": 100, "output_tokens": 75})
        self.assertEqual(data["totals"]["finished"], 1)

        markdown = self.report("--tokens")
        self.assertIn(f"`{request_id}`", markdown)
        self.assertIn("0.2k", markdown)
