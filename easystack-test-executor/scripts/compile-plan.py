#!/usr/bin/env python3
"""Compile a normalized plan into an immutable runnable contract."""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from _actions import PLACEHOLDER, lookup
from _contract import ContractError, compile_contract
from _events import append_event, load_events, project_state
from _harness import atomic_json, atomic_text, local_now
from _profile import validate_profile


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--plan", required=True, type=Path)
    result.add_argument("--result-root", required=True, type=Path)
    result.add_argument("--run-id", required=True)
    result.add_argument("--timezone", required=True)
    result.add_argument("--profile", required=True, type=Path)
    result.add_argument(
        "--cleanup-policy",
        default="preserve_on_failure",
        choices=(
            "preserve_all",
            "preserve_on_failure",
            "cleanup_on_success",
            "cleanup_all",
            "explicit_per_case",
        ),
    )
    return result


def write_resume(root: Path, state: dict) -> None:
    case_id = state["current_case"]
    lines = [
        "# Test Run Resume",
        "",
        f"- Run ID: `{state['run_id']}`",
        f"- Current case: `{case_id}`",
        "- Current phase: `NOT_STARTED`",
        "- Allowed action: `python3 scripts/checkpoint.py next`",
        "",
        "恢复时先运行:",
        "",
        "```bash",
        f"{sys.executable} {Path(__file__).with_name('checkpoint.py').resolve()} "
        f"next --result-root {root}",
        "```",
        "",
        "只执行新返回的 `launcher_argv`, 不从对话历史推断下一步.",
    ]
    atomic_text(root / "resume.md", "\n".join(lines) + "\n")


def compile_run(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    if not re.fullmatch(r"R[0-9]{14}", args.run_id):
        raise ContractError("run-id must match R<YYYYMMDDHHmmss>")
    try:
        datetime.strptime(args.run_id[1:], "%Y%m%d%H%M%S")
    except ValueError as error:
        raise ContractError("run-id contains an invalid local date") from error
    if root.exists() and any(root.iterdir()):
        raise ContractError(f"result root is not empty: {root}")
    ZoneInfo(args.timezone)
    profile, profile_errors, _ = validate_profile(
        args.profile.resolve(), max_age_days=30, enforce_runtime=True
    )
    if profile_errors:
        raise ContractError("; ".join(profile_errors))
    if profile["environment"]["timezone"] != args.timezone:
        raise ContractError("profile timezone differs from run timezone")
    root.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(root, 0o700)
    skill_root = Path(__file__).resolve().parents[1]
    contract = compile_contract(
        args.plan,
        args.run_id,
        args.timezone,
        args.cleanup_policy,
        skill_root,
        local_now(args.timezone),
        profile,
        args.profile,
    )
    for case in contract["cases"]:
        for action in case["actions"]:
            for argument in action["command"]:
                for binding in PLACEHOLDER.findall(argument):
                    if binding.startswith("profile."):
                        try:
                            lookup(
                                contract["environment_profile"],
                                binding.removeprefix("profile."),
                            )
                        except (ValueError, IndexError, KeyError) as error:
                            raise ContractError(
                                f"{case['id']}/{action['id']}: {error}"
                            ) from error
    atomic_json(root / "execution-contract.json", contract)
    atomic_json(root / "normalized-cases.json", {"cases": contract["cases"]})
    atomic_json(root / "environment-profile.json", profile)
    atomic_json(root / "impact-analysis.json", contract["impact_analysis"])
    atomic_json(root / "authorization.json", contract["authorization"])
    atomic_text(root / "artifact-manifest.jsonl", "")
    atomic_json(root / "resources-all.json", [])
    for case in contract["cases"]:
        case_root = root / "cases" / case["id"]
        case_root.mkdir(parents=True, mode=0o700)
        atomic_json(case_root / "case.json", case)
        atomic_json(case_root / "resources.json", [])
    append_event(root, args.timezone, "RUN_INITIALIZED")
    state = project_state(contract, load_events(root / "events.jsonl"))
    atomic_json(root / "run-state.json", state)
    write_resume(root, state)
    for path in root.rglob("*"):
        if path.is_file():
            os.chmod(path, 0o600)


def main() -> int:
    args = parser().parse_args()
    try:
        compile_run(args)
    except (ContractError, OSError, ValueError) as error:
        print(f"compile-plan error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
