#!/usr/bin/env python3
"""Plan loading and immutable execution-contract compilation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from _harness import object_digest, safe_component, skill_digest
from _validation import case_text_errors


HARNESS_VERSION = "3.0"
SCHEMA_VERSION = 3
CASE_PHASES = (
    "DISCOVER_CASE_CONTEXT",
    "OPEN_LOG_WINDOW",
    "SNAPSHOT_SERVICE_INSTANCES",
    "PREPARE",
    "EXECUTE",
    "WAIT",
    "VERIFY",
    "CLOSE_LOG_WINDOW",
    "COLLECT_LOGS",
    "COLLECT_RESOURCES",
    "DERIVE_VERDICT",
    "APPLY_CLEANUP_POLICY",
    "FINALIZE_RESULT",
    "CASE_GATE",
    "ADVANCE_LOG_CURSOR",
    "COMPLETE",
)
ACTION_PHASES = set(CASE_PHASES[:10]) | {"APPLY_CLEANUP_POLICY"}
STEP_PHASES = ACTION_PHASES
TERMINAL_STEP_STATUSES = {
    "PASS",
    "FAIL",
    "BLOCKED",
    "SKIPPED_BY_PLAN",
    "NOT_APPLICABLE",
}
ACTION_KINDS = {"openstack", "kubectl", "env_access", "assertion", "cleanup"}
ALLOWED_EXECUTABLES = {
    "openstack": {"openstack"},
    "kubectl": {"kubectl"},
    "env_access": {"bash"},
    "assertion": {"false", "grep", "jq", "test", "true"},
    "cleanup": {"bash", "kubectl", "openstack"},
}
DESTRUCTIVE_TOKENS = {
    "apply", "clean", "cordon", "delete", "drain", "edit", "evacuate",
    "force-delete", "lock", "migrate", "patch", "pause", "reboot", "rebuild",
    "remove", "rescue", "resize", "resume", "rollout", "scale", "shelve",
    "start", "stop", "suspend", "taint", "uncordon", "unlock", "unpause",
    "unrescue", "unshelve",
}


class ContractError(ValueError):
    """Raised when a normalized plan cannot become an execution contract."""


def load_structured(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as error:
            raise ContractError(
                "YAML input requires PyYAML; use canonical JSON instead"
            ) from error
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ContractError("plan root must be an object")
    return data


def require_fields(item: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in item]
    if missing:
        raise ContractError(f"{label} missing fields: {','.join(missing)}")


def executable_name(command: list[str]) -> str:
    return Path(command[0]).name


def validate_executable(case_id: str, step_id: str, step: dict[str, Any]) -> None:
    executable = executable_name(step["command"])
    allowed = ALLOWED_EXECUTABLES[step["kind"]]
    if executable not in allowed:
        raise ContractError(
            f"{case_id}/{step_id}: {step['kind']} action cannot execute {executable}"
        )
    if executable == "bash":
        command = step["command"]
        if len(command) < 2 or Path(command[1]).name != "env-access.sh":
            raise ContractError(
                f"{case_id}/{step_id}: bash may only launch env-access.sh"
            )


def env_access_read_only(command: list[str]) -> bool:
    if "--cmd" in command or "--" not in command:
        return False
    remote = command[command.index("--") + 1 :]
    if not remote:
        return False
    if remote[0] in {"hostname", "id", "pwd", "whoami"}:
        return len(remote) == 1 or remote[0] == "id"
    if remote[0] == "kubectl":
        return any(
            item in {"api-resources", "api-versions", "describe", "get", "logs", "version"}
            for item in remote[1:]
        )
    if remote[0] == "openstack":
        return any(item in {"list", "show"} for item in remote[1:])
    return False


def validate_step(case_id: str, step: dict[str, Any], seen: set[str]) -> None:
    require_fields(
        step, ("id", "phase", "kind", "description", "command", "expected"),
        f"{case_id} action",
    )
    if not isinstance(step["id"], str):
        raise ContractError(f"{case_id}: step ID must be a string")
    step_id = safe_component(str(step["id"]), "step ID")
    if step_id in seen:
        raise ContractError(f"{case_id}: duplicate step ID {step_id}")
    seen.add(step_id)
    phase = str(step["phase"]).upper()
    if phase not in ACTION_PHASES:
        raise ContractError(f"{case_id}/{step_id}: invalid step phase {phase}")
    step["phase"] = phase
    if not str(step["description"]).strip():
        raise ContractError(f"{case_id}/{step_id}: empty description")
    timeout = step.get("timeout_seconds")
    if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
        raise ContractError(f"{case_id}/{step_id}: timeout_seconds must be positive")
    if step["kind"] not in ACTION_KINDS:
        raise ContractError(f"{case_id}/{step_id}: invalid action kind")
    command = step["command"]
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(item, str) and item for item in command)
    ):
        raise ContractError(f"{case_id}/{step_id}: command must be a non-empty argv list")
    validate_executable(case_id, step_id, step)
    if (
        step["kind"] == "env_access"
        and not step.get("destructive_operation")
        and not env_access_read_only(command)
    ):
        raise ContractError(
            f"{case_id}/{step_id}: env_access must be compiler-verifiable read-only "
            "or declare destructive_operation"
        )
    if DESTRUCTIVE_TOKENS.intersection(item.lower() for item in command) and not step.get(
        "destructive_operation"
    ):
        raise ContractError(
            f"{case_id}/{step_id}: destructive command needs destructive_operation"
        )
    expected = step["expected"]
    if not isinstance(expected, dict):
        raise ContractError(f"{case_id}/{step_id}: expected must be an object")
    codes = expected.get("return_codes")
    if (
        not isinstance(codes, list)
        or not codes
        or not all(isinstance(code, int) and 0 <= code <= 255 for code in codes)
    ):
        raise ContractError(
            f"{case_id}/{step_id}: expected.return_codes must contain valid codes"
        )
    captures = step.get("capture", {}).get("resources", [])
    if not isinstance(captures, list):
        raise ContractError(f"{case_id}/{step_id}: capture.resources must be a list")
    for capture in captures:
        if not isinstance(capture, dict) or not all(
            capture.get(field) for field in ("key", "type", "id", "name")
        ):
            raise ContractError(
                f"{case_id}/{step_id}: resource capture needs key,type,id,name"
            )
    artifacts = step.get("capture", {}).get("artifacts", [])
    if not isinstance(artifacts, list) or any(
        not isinstance(item, dict) or not item.get("glob") for item in artifacts
    ):
        raise ContractError(f"{case_id}/{step_id}: capture.artifacts is invalid")
    cleanup_resources = step.get("cleanup_resources", [])
    if step["kind"] == "cleanup" and not isinstance(cleanup_resources, list):
        raise ContractError(f"{case_id}/{step_id}: cleanup_resources must be a list")
    if step["kind"] == "cleanup" and not step.get("destructive_operation"):
        raise ContractError(
            f"{case_id}/{step_id}: cleanup action needs destructive_operation"
        )


def validate_check(case_id: str, check: dict[str, Any], seen: set[str]) -> None:
    require_fields(
        check,
        ("id", "check_type", "required", "expected"),
        f"{case_id} verification",
    )
    if not isinstance(check["id"], str):
        raise ContractError(f"{case_id}: check ID must be a string")
    check_id = safe_component(str(check["id"]), "check ID")
    if check_id in seen:
        raise ContractError(f"{case_id}: duplicate check ID {check_id}")
    seen.add(check_id)
    if check["check_type"] not in {"functional", "diagnostic", "cleanup"}:
        raise ContractError(f"{case_id}/{check_id}: invalid check_type")
    if not isinstance(check["required"], bool):
        raise ContractError(f"{case_id}/{check_id}: required must be boolean")
    if not str(check["expected"]).strip():
        raise ContractError(f"{case_id}/{check_id}: expected must not be empty")
    evaluator = check.get("evaluator")
    if not isinstance(evaluator, dict) or evaluator.get("type") not in {
        "action_status", "json_path", "regex", "manual",
    }:
        raise ContractError(f"{case_id}/{check_id}: invalid evaluator")
    required_by_type = {
        "action_status": ("action_id",),
        "json_path": ("action_id", "path", "value"),
        "regex": ("action_id", "pattern"),
        "manual": (),
    }
    missing = [
        field for field in required_by_type[evaluator["type"]]
        if field not in evaluator
    ]
    if missing:
        raise ContractError(
            f"{case_id}/{check_id}: evaluator missing {','.join(missing)}"
        )


def validate_case(case: dict[str, Any]) -> None:
    require_fields(
        case,
        (
            "id",
            "scenario_key",
            "title",
            "requirement_summary",
            "domain",
            "objective",
            "actions",
            "verification",
            "log_requirement",
            "log_targets",
            "cleanup_policy",
            "impact_refs",
            "capability_status",
            "destructive_operations",
        ),
        "case",
    )
    if not isinstance(case["id"], str):
        raise ContractError("case ID must be a string")
    case_id = safe_component(str(case["id"]), "case ID")
    text_record = {
        "scenario_key": case["scenario_key"],
        "title": case["title"],
        "requirement_summary": case["requirement_summary"],
    }
    errors = case_text_errors(text_record)
    if errors:
        raise ContractError(f"{case_id}: {'; '.join(errors)}")
    if case["log_requirement"] not in {"required", "optional", "none"}:
        raise ContractError(f"{case_id}: invalid log_requirement")
    if case["cleanup_policy"] not in {
        "inherit",
        "preserve_all",
        "preserve_on_failure",
        "cleanup_on_success",
        "cleanup_all",
        "explicit_per_case",
    }:
        raise ContractError(f"{case_id}: invalid cleanup_policy")
    if not isinstance(case["impact_refs"], list) or not case["impact_refs"]:
        raise ContractError(f"{case_id}: impact_refs must be non-empty")
    if case["capability_status"] not in {
        "SUPPORTED", "CONDITIONAL", "UNSUPPORTED", "UNKNOWN",
    }:
        raise ContractError(f"{case_id}: invalid capability_status")
    if not isinstance(case["destructive_operations"], list):
        raise ContractError(f"{case_id}: destructive_operations must be a list")
    if not isinstance(case["log_targets"], list):
        raise ContractError(f"{case_id}: log_targets must be a list")
    if case["log_requirement"] == "required" and not case["log_targets"]:
        raise ContractError(f"{case_id}: required logs need explicit log_targets")
    for target in case["log_targets"]:
        if isinstance(target, str):
            valid_target = bool(target.strip())
        elif isinstance(target, dict):
            valid_target = bool(target.get("name") or target.get("service"))
            if "required" in target and not isinstance(target["required"], bool):
                raise ContractError(f"{case_id}: log target required must be boolean")
        else:
            valid_target = False
        if not valid_target:
            raise ContractError(f"{case_id}: invalid log target")
    if not isinstance(case["actions"], list) or not case["actions"]:
        raise ContractError(f"{case_id}: actions must be a non-empty list")
    step_ids: set[str] = set()
    resource_keys: set[str] = set()
    previous_phase = -1
    for step in case["actions"]:
        validate_step(case_id, step, step_ids)
        phase_index = CASE_PHASES.index(step["phase"])
        if phase_index < previous_phase:
            raise ContractError(f"{case_id}: actions must follow phase order")
        previous_phase = phase_index
        for capture in step.get("capture", {}).get("resources", []):
            if capture["key"] in resource_keys:
                raise ContractError(
                    f"{case_id}: duplicate resource key {capture['key']}"
                )
            unknown_dependencies = set(
                capture.get("dependencies", [])
            ) - resource_keys
            if unknown_dependencies:
                raise ContractError(
                    f"{case_id}/{step['id']}: unknown resource dependencies "
                    f"{','.join(sorted(unknown_dependencies))}"
                )
            resource_keys.add(capture["key"])
        unknown_cleanup = set(step.get("cleanup_resources", [])) - resource_keys
        if unknown_cleanup:
            raise ContractError(
                f"{case_id}/{step['id']}: unknown cleanup resource key "
                f"{','.join(sorted(unknown_cleanup))}"
            )
        operation = step.get("destructive_operation")
        if operation and operation not in case["destructive_operations"]:
            raise ContractError(
                f"{case_id}/{step['id']}: destructive operation is not declared"
            )
    if not isinstance(case["verification"], list) or not case["verification"]:
        raise ContractError(f"{case_id}: verification must be a non-empty list")
    check_ids: set[str] = set()
    for check in case["verification"]:
        validate_check(case_id, check, check_ids)
        action_id = check["evaluator"].get("action_id")
        if action_id and action_id not in step_ids:
            raise ContractError(
                f"{case_id}/{check['id']}: evaluator action not found {action_id}"
            )
    if not any(
        check["check_type"] == "functional" and check["required"]
        for check in case["verification"]
    ):
        raise ContractError(f"{case_id}: at least one required functional check needed")


def validate_plan(data: dict[str, Any]) -> list[dict[str, Any]]:
    impact = data.get("impact_analysis")
    authorization = data.get("authorization")
    if not isinstance(impact, dict) or not impact.get("id"):
        raise ContractError("plan needs impact_analysis.id")
    if not isinstance(impact.get("obligations"), list) or not impact["obligations"]:
        raise ContractError("impact_analysis.obligations must be non-empty")
    if not isinstance(authorization, dict) or not authorization.get("scope"):
        raise ContractError("plan needs authorization.scope")
    allowed = authorization.get("destructive_operations")
    if not isinstance(allowed, list):
        raise ContractError("authorization.destructive_operations must be a list")
    impact_ids = {
        str(item.get("id")) for item in impact["obligations"]
        if isinstance(item, dict) and item.get("id")
    }
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ContractError("plan must contain a non-empty cases list")
    ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ContractError("every case must be an object")
        validate_case(case)
        unknown_impact = set(case["impact_refs"]) - impact_ids
        if unknown_impact:
            raise ContractError(
                f"{case['id']}: unknown impact_refs "
                f"{','.join(sorted(unknown_impact))}"
            )
        case_id = str(case["id"])
        if case_id in ids:
            raise ContractError(f"duplicate case ID {case_id}")
        ids.add(case_id)
    for case in cases:
        unknown = set(case.get("dependencies", [])) - ids
        if unknown:
            raise ContractError(
                f"{case['id']}: unknown dependencies {','.join(sorted(unknown))}"
            )
        unauthorized = set(case["destructive_operations"]) - set(allowed)
        if unauthorized:
            raise ContractError(
                f"{case['id']}: unauthorized destructive operations: "
                f"{','.join(sorted(unauthorized))}"
            )
    positions = {case["id"]: index for index, case in enumerate(cases)}
    for case in cases:
        later = [
            dependency
            for dependency in case.get("dependencies", [])
            if positions[dependency] >= positions[case["id"]]
        ]
        if later:
            raise ContractError(
                f"{case['id']}: dependencies must appear earlier: {','.join(later)}"
            )
    return cases


def compile_contract(
    plan_path: Path,
    run_id: str,
    timezone: str,
    cleanup_policy: str,
    skill_root: Path,
    created_local: str,
    profile: dict[str, Any],
    profile_path: Path,
) -> dict[str, Any]:
    plan = load_structured(plan_path)
    cases = validate_plan(plan)
    contract = {
        "schema_version": SCHEMA_VERSION,
        "harness_version": HARNESS_VERSION,
        "run_id": run_id,
        "timezone": timezone,
        "cleanup_policy": cleanup_policy,
        "case_order": [case["id"] for case in cases],
        "cases": cases,
        "impact_analysis": plan["impact_analysis"],
        "authorization": plan["authorization"],
        "environment_profile": profile,
        "environment_profile_source": str(profile_path.resolve()),
        "environment_profile_sha256": object_digest(profile),
        "phase_order": list(CASE_PHASES),
        "terminal_step_statuses": sorted(TERMINAL_STEP_STATUSES),
        "skill_sha256": skill_digest(skill_root),
        "source_plan": str(plan_path.resolve()),
        "source_plan_sha256": object_digest(plan),
        "created_local": created_local,
    }
    contract["contract_sha256"] = object_digest(contract)
    return contract


def case_by_id(contract: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in contract.get("cases", []):
        if case.get("id") == case_id:
            return case
    raise ContractError(f"case not present in contract: {case_id}")


def contract_digest(contract: dict[str, Any]) -> str:
    unsigned = dict(contract)
    unsigned.pop("contract_sha256", None)
    return object_digest(unsigned)
