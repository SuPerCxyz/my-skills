from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_patterns", SKILL / "scripts/validate-patterns.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ResultContractTest(unittest.TestCase):
    def check(self, example: str) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="cloud-result-contract.") as temporary:
            root = Path(temporary)
            (root / "patterns").mkdir()
            (root / "patterns/operation-template.md").write_text(
                (SKILL / "patterns/operation-template.md").read_text(), encoding="utf-8"
            )
            (root / "sample.md").write_text(example, encoding="utf-8")
            return VALIDATOR.findings(root)

    def test_button_boolean_is_not_a_success_contract(self):
        errors = self.check("```js\n({ok: Boolean(button), status:'confirm_needed'});\n```\n")
        self.assertTrue(any("literal true, false or null" in error for error in errors))
        self.assertTrue(any("terminal" in error for error in errors))
        self.assertTrue(any("submitted" in error for error in errors))

    def test_submitted_and_dynamic_intermediate_states_are_rejected(self):
        for status in ("'submitted'", "'Creating'", "'Building'", "button ? 'confirm_needed' : 'selected'"):
            with self.subTest(status=status):
                errors = self.check("```js\n({ok:true, terminal:true, submitted:true, status:" + status + "});\n```")
                self.assertTrue(any("intermediate state" in error for error in errors))
        self.assertTrue(self.check("```js\n({ok:true, terminal:true, submitted:true, status: observedStatus});\n```"))

    def test_null_requires_pending_and_final_requires_terminal(self):
        for ok, terminal in (("null", "true"), ("true", "false"), ("false", "false")):
            with self.subTest(ok=ok, terminal=terminal):
                self.assertTrue(self.check(f"```js\n({{ok:{ok}, terminal:{terminal}, submitted:false}});\n```"))

    def test_nested_multiline_objects_and_quoted_braces_are_read_completely(self):
        code = '''```js
({
  ok: true,
  details: {message: "a } brace", data: [1, 2]},
  terminal: true,
  submitted: true,
  status: 'Available'
});
```'''
        self.assertEqual([], self.check(code))
        self.assertTrue(self.check(code.replace("submitted: true,", "")))

    def test_valid_pending_success_and_failure_are_accepted(self):
        code = '''```json
{"ok":null,"terminal":false,"submitted":true,"status":"uploading"}
{"ok":true,"terminal":true,"submitted":true,"status":"Available"}
{"ok":false,"terminal":true,"submitted":true,"status":"Error"}
```'''
        self.assertEqual([], self.check(code))

    def test_prose_comments_and_duplicate_fields(self):
        self.assertEqual([], self.check("Do not return `ok: Boolean(button)`.\n```js\n// {ok:true}\n```"))
        self.assertTrue(self.check("```js\n({ok:true, ok:null, terminal:true, submitted:false});\n```"))

    def test_real_documents_and_cli(self):
        self.assertEqual([], VALIDATOR.findings(SKILL))
        completed = subprocess.run([sys.executable, str(SKILL / "scripts/validate-patterns.py")],
                                   capture_output=True, text=True, check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("PASS:", completed.stdout)

    def test_real_readme_config_reader_does_not_print_secrets(self):
        readme = (SKILL / "README.md").read_text()
        code = re.search(r"<<'PYCONFIG'\n(.*?)\nPYCONFIG", readme, re.DOTALL).group(1)
        code = "import sys\n" + code.replace("Path('/tmp/easystack-env.json')", "Path(sys.argv[1])")
        with tempfile.TemporaryDirectory(prefix="cloud-config-summary.") as temporary:
            path = Path(temporary) / "env.json"
            for password, expected in (("private-password-DO-NOT-PRINT", 0), ("", 1)):
                path.write_text(json.dumps({"platform": {"url": "https://example.invalid", "username": "private-user-DO-NOT-PRINT", "password": password}, "token": "private-token-DO-NOT-PRINT"}))
                completed = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True, text=True, check=False)
                self.assertEqual(expected, completed.returncode)
                self.assertNotIn("DO-NOT-PRINT", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
