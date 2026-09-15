from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _contract import ContractError, validate_step  # noqa: E402


def action(kind: str, command: list[str]) -> dict:
    return {
        "id": "STEP-01",
        "phase": "EXECUTE",
        "kind": kind,
        "description": "contract test",
        "command": command,
        "expected": {"return_codes": [0]},
    }


class ContractSafetyTest(unittest.TestCase):
    def test_shell_wrapper_is_rejected(self) -> None:
        step = action("assertion", ["bash", "-c", "true"])
        with self.assertRaisesRegex(ContractError, "cannot execute bash"):
            validate_step("CASE-01", step, set())

    def test_kind_must_match_executable(self) -> None:
        step = action("openstack", ["kubectl", "get", "pods"])
        with self.assertRaisesRegex(ContractError, "cannot execute kubectl"):
            validate_step("CASE-01", step, set())

    def test_control_plane_mutation_needs_authorization_name(self) -> None:
        step = action("openstack", ["openstack", "server", "stop", "server-id"])
        with self.assertRaisesRegex(ContractError, "needs destructive_operation"):
            validate_step("CASE-01", step, set())

    def test_declared_control_plane_mutation_is_accepted(self) -> None:
        step = action("openstack", ["openstack", "server", "stop", "server-id"])
        step["destructive_operation"] = "server.stop"
        validate_step("CASE-01", step, set())

    def test_kubernetes_mutation_needs_authorization_name(self) -> None:
        step = action("kubectl", ["kubectl", "apply", "-f", "overlay.yaml"])
        with self.assertRaisesRegex(ContractError, "needs destructive_operation"):
            validate_step("CASE-01", step, set())

    def test_env_access_allows_vectorized_read_only_command(self) -> None:
        step = action(
            "env_access",
            ["bash", "/skills/env-access.sh", "--target", "example", "--", "whoami"],
        )
        validate_step("CASE-01", step, set())

    def test_env_access_rejects_direct_script(self) -> None:
        step = action(
            "env_access",
            ["/skills/env-access.sh", "--target", "example", "--", "whoami"],
        )
        with self.assertRaisesRegex(ContractError, "cannot execute env-access.sh"):
            validate_step("CASE-01", step, set())

    def test_env_access_rejects_opaque_command_string(self) -> None:
        step = action(
            "env_access",
            ["bash", "/skills/env-access.sh", "--target", "example", "--cmd", "whoami"],
        )
        with self.assertRaisesRegex(ContractError, "compiler-verifiable read-only"):
            validate_step("CASE-01", step, set())


if __name__ == "__main__":
    unittest.main()
