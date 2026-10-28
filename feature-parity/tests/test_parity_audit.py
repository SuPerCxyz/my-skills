from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "parity_audit.py"
HEADER = (
    "| ID | Feature | Scope | Reference evidence | Target evidence | Status | Verification | Notes |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


class MatrixAuditTest(unittest.TestCase):
    def audit(self, rows: str, expected: int, header: str = HEADER) -> str:
        with tempfile.TemporaryDirectory(prefix="parity-audit.") as directory:
            matrix = Path(directory) / "matrix.md"
            matrix.write_text(header + rows, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(matrix)],
                capture_output=True, text=True, timeout=10, check=False,
            )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result.stdout

    def test_empty_matrix_fails(self) -> None:
        self.assertIn("at least one", self.audit("", 1))

    def test_invalid_id_is_reported_even_with_valid_sibling(self) -> None:
        rows = "| bad | behavior | In | ref:1 | target:1 | Implemented | Pass | |\n"
        rows += "| F-001 | behavior | In | ref:1 | - | Missing | Not run | |\n"
        self.assertIn("invalid feature ID", self.audit(rows, 1))

    def test_placeholder_reference_fails(self) -> None:
        for evidence in ("", "-", "`-`", "`<evidence>`"):
            with self.subTest(evidence=evidence):
                self.assertIn("reference evidence", self.audit(
                    f"| F-001 | behavior | In | {evidence} | target:1 | Implemented | Pass | |\n", 1
                ))

    def test_valid_row_accepts_empty_notes_and_escaped_pipe(self) -> None:
        self.audit("|F-001|behavior \\| alternative|In|ref:1|target:1|Implemented|Pass||\n", 0)

    def test_real_autolink_and_extension_column_remain_valid(self) -> None:
        self.audit(
            "| F-001 | behavior | In | <https://example.com/commit/abc> | target:1 | Implemented | Pass | | owner |\n", 0
        )

    def test_existing_consistency_gates_remain(self) -> None:
        rows = "| F-001 | behavior | In | ref:1 | - | Implemented | Pass | |\n"
        rows += "| F-001 | behavior | In | ref:1 | - | Blocked | Pass | unavailable |\n"
        output = self.audit(rows, 1)
        self.assertIn("duplicate ID", output)
        self.assertIn("without target evidence", output)
        self.assertIn("Blocked cannot", output)

    def test_missing_matrix_returns_two(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-audit.") as directory:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(Path(directory) / "absent.md")],
                capture_output=True, text=True, timeout=10, check=False,
            )
        self.assertEqual(2, result.returncode)


if __name__ == "__main__":
    unittest.main()
