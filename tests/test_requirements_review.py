import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from plugin_run import run
from requirements_analysis import assess, load_competitors, validate_plan
from review_renderer import render_review


class ReviewContract(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples/plugin-input.json").read_text(encoding="utf-8"))
        self.plan = json.loads((ROOT / "examples/team-pulse-plan.json").read_text(encoding="utf-8"))
        self.analysis = assess(self.data["requirement_markdown"], self.data["competitors"])

    def test_unplanned_brief_has_no_invented_backlog(self):
        brief = "Product: FitCheck\nGoal: Support the automotive team checking compatibility.\nConstraints: No staff surveys."
        result = run({"requirement_markdown": brief})["result"]
        self.assertEqual(result["phase"], "needs_plan")
        self.assertIsNone(result["product_plan"])
        self.assertEqual(result["backlog"], [])
        self.assertEqual(result["analysis"]["requirement_markdown"], brief)
        self.assertEqual(result["summary"]["constraints"], ["No staff surveys."])

    def test_complete_plan_is_rendered_with_source_and_acceptance(self):
        result = run({**self.data, "product_plan": self.plan})["result"]
        self.assertEqual(result["checks"]["reference_integrity"], "passed")
        self.assertEqual(result["checks"]["semantic_review"], "required")
        self.assertEqual(len(result["backlog"]), 4)
        self.assertEqual(result["backlog"][0]["acceptance"], self.plan["features"][0]["stories"][0]["acceptance"])

    def test_free_prose_case_uses_authored_summary_and_preserves_original(self):
        data = json.loads((ROOT / "examples/fitcheck-input.json").read_text(encoding="utf-8"))
        data["product_plan"] = json.loads((ROOT / "examples/fitcheck-plan.json").read_text(encoding="utf-8"))
        result = run(data)["result"]
        self.assertEqual(result["summary_source"], "product_plan")
        self.assertIn("FitCheck", result["summary"]["product_name"])
        self.assertEqual(result["analysis"]["requirement_markdown"], data["requirement_markdown"])
        self.assertIn("配件员", result["summary"]["target_users"])
        self.assertEqual(result["summary"]["constraints"], [data["product_plan"]["constraint_responses"][0]["implementation"]])
        self.assertNotIn("。。", result["markdown"])

    def test_markdown_headings_bold_labels_and_multiline_constraints(self):
        a = assess("# Demo\n## Users\n- Parts clerk\n**Constraints:**\n- No DMS\n- No personal data\n## Notes\nSeparate context")
        self.assertEqual(a["summary"]["constraints"], ["No DMS", "No personal data"])
        self.assertEqual(a["evidence"][-1]["kind"], "context")

    def test_revised_input_requires_reconsidered_plan(self):
        other = assess(self.data["requirement_markdown"] + "\n禁止匿名问卷", self.data["competitors"])
        with self.assertRaisesRegex(ValueError, "stale"):
            validate_plan(self.plan, other)

    def test_revised_competitor_invalidates_plan(self):
        rows = copy.deepcopy(self.data["competitors"])
        rows[0]["weaknesses"] = "Changed source claim"
        with self.assertRaisesRegex(ValueError, "stale"):
            validate_plan(self.plan, assess(self.data["requirement_markdown"], rows))

    def test_fabricated_quote_rejected(self):
        self.plan["features"][0]["basis"]["evidence_refs"][0]["quote"] = "Customers proved adoption increased 90%."
        with self.assertRaisesRegex(ValueError, "quote"):
            validate_plan(self.plan, self.analysis)

    def test_unknown_assumption_and_missing_basis_rejected(self):
        for basis in [{"evidence_refs": [], "assumption_ids": []}, {"evidence_refs": [], "assumption_ids": ["A404"]}]:
            with self.subTest(basis=basis):
                p = copy.deepcopy(self.plan); p["features"][0]["basis"] = basis
                with self.assertRaises(ValueError): validate_plan(p, self.analysis)

    def test_duplicate_ids_rejected(self):
        self.plan["users"].append(copy.deepcopy(self.plan["users"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_plan(self.plan, self.analysis)

    def test_story_user_must_experience_linked_problem(self):
        self.plan["features"][0]["stories"][0]["user_id"] = "U1"
        with self.assertRaisesRegex(ValueError, "story.user_id"):
            validate_plan(self.plan, self.analysis)

    def test_mvp_cannot_depend_on_later_release(self):
        self.plan["features"][0]["dependencies"] = ["F4"]
        with self.assertRaisesRegex(ValueError, "MVP"):
            validate_plan(self.plan, self.analysis)

    def test_dependency_cycle_rejected(self):
        self.plan["features"][0]["dependencies"] = ["F2"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            validate_plan(self.plan, self.analysis)

    def test_omitted_explicit_constraint_rejected(self):
        self.plan["constraint_responses"].pop()
        with self.assertRaisesRegex(ValueError, "constraint"):
            validate_plan(self.plan, self.analysis)

    def test_prose_constraint_can_be_explicitly_addressed(self):
        self.plan["constraint_responses"].append({"evidence_id": "E007", "treatment": "needs_decision",
            "implementation": "Review privacy implications of the stated concern.", "feature_ids": ["F1"]})
        self.assertEqual(validate_plan(self.plan, self.analysis)["constraint_decisions_pending"], 1)

    def test_competitor_claim_cannot_be_used_as_requirement_constraint(self):
        self.plan["constraint_responses"].append({"evidence_id": "C001-name", "treatment": "honored",
            "implementation": "Unrelated name", "feature_ids": []})
        with self.assertRaises(ValueError): validate_plan(self.plan, self.analysis)

    def test_provided_target_must_appear_in_source_quote(self):
        self.plan["metrics"][0]["target"] = "95%"
        with self.assertRaisesRegex(ValueError, "provided target"):
            validate_plan(self.plan, self.analysis)

    def test_unknown_metric_target_must_be_null(self):
        self.plan["metrics"][0]["target_status"] = "unknown"
        with self.assertRaisesRegex(ValueError, "unknown target"):
            validate_plan(self.plan, self.analysis)

    def test_outcomes_need_guardrail(self):
        self.plan["metrics"] = self.plan["metrics"][:2]
        with self.assertRaisesRegex(ValueError, "guardrail"):
            validate_plan(self.plan, self.analysis)

    def test_release_cannot_precede_dependency(self):
        self.plan["rollout"] = [{"name": "Early", "feature_ids": ["F3"], "exit_criteria": ["Test passed"]},
            {"name": "Late", "feature_ids": ["F1", "F2", "F4"], "exit_criteria": ["Test passed"]}]
        with self.assertRaisesRegex(ValueError, "before its dependency"):
            validate_plan(self.plan, self.analysis)

    def test_html_keeps_hostile_input_as_data(self):
        attack = "</script><script>window.pwned=true</script>"
        payload = run({"requirement_markdown": attack})
        html = render_review(payload)
        self.assertNotIn(attack, html)
        self.assertIn("\\u003c/script\\u003e", html)
        self.assertIn("connect-src 'none'", html)

    def test_template_markers_in_user_text_are_not_expanded(self):
        html = render_review(run({"requirement_markdown": "Product: __STYLE__ __DATA__"}))
        self.assertIn("<title>__STYLE__ __DATA__ - PRD 评审</title>", html)

    def test_empty_brief_and_empty_plan_rejected(self):
        with self.assertRaises(Exception): run({"requirement_markdown": " \n "})
        with self.assertRaises(Exception): run({**self.data, "product_plan": {}})

    def test_csv_duplicate_headers_and_ragged_rows_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            for text in ["name,name,positioning,strengths,weaknesses,pricing,target_user\nx,x,x,x,x,x,x\n",
                         "name,positioning,strengths,weaknesses,pricing,target_user\nx,x,x\n"]:
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError): load_competitors(path)

    def test_existing_output_preserved_and_fresh_output_openable(self):
        (ROOT / "output").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "output") as directory:
            destination = Path(directory) / "review"
            command = [sys.executable, "-X", "utf8", "scripts/plugin_run.py", "--input", "examples/plugin-input.json",
                       "--plan", "examples/team-pulse-plan.json", "--output-dir", str(destination)]
            process = subprocess.run(command, cwd=ROOT, capture_output=True, encoding="utf-8")
            self.assertEqual(process.returncode, 0, process.stdout)
            before = (destination / "result.json").read_bytes()
            self.assertTrue((destination / "review.html").is_file())
            repeated = subprocess.run(command, cwd=ROOT, capture_output=True, encoding="utf-8")
            self.assertEqual(repeated.returncode, 2)
            self.assertEqual((destination / "result.json").read_bytes(), before)


if __name__ == "__main__": unittest.main()
