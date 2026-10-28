#!/usr/bin/env python3
"""Validate result objects in fenced examples without executing browser code."""

from __future__ import annotations

import re
import sys
from pathlib import Path


INTERMEDIATE = {
    "confirm_needed", "dialog_opened", "menu_opened", "selected", "submitted",
    "submitted_or_confirm_needed", "submission_unconfirmed", "wizard_progressing",
    "project_context_unconfirmed", "confirmation_required", "uploading", "creating",
    "saving", "queued", "rebooting", "deleting", "detaching", "associating",
    "creation_unconfirmed", "building", "binding", "restoring", "rolling_back",
    "pending", "loading", "switching",
}
TOKENS = re.compile(
    r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|'
    r'`(?:\\.|[^`\\])*`|[A-Za-z_$][\w$]*|[^\s]', re.DOTALL
)


def fenced_examples(text: str):
    """Yield code fences; prose and inline-code examples are not programs."""
    fence = None
    lines: list[str] = []
    start = 0
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
        if fence is None and marker:
            fence = marker[1]
            start = number + 1
            lines = []
        elif fence and marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
            yield start, "".join(lines)
            fence = None
        elif fence:
            lines.append(line)


def result_objects(code: str):
    """Read top-level properties, preserving nested and multiline expressions.

    This checks documented JS/JSON object notation; it is not a JavaScript
    interpreter. Dynamic ok/terminal/submitted values fail closed.
    """
    tokens = [m for m in TOKENS.finditer(code) if not m[0].startswith(("//", "/*"))]
    stack: list[int] = []
    for index, token in enumerate(tokens):
        if token[0] == "{":
            stack.append(index)
        elif token[0] == "}" and stack:
            begin = stack.pop()
            properties: dict[str, str] = {}
            duplicates: set[str] = set()
            part = []
            depth = 0
            for item in tokens[begin + 1:index] + [None]:
                value = item[0] if item else ","
                if value == "," and depth == 0:
                    if part:
                        key = part[0][0].strip("\"'")
                        if len(part) == 1:
                            expression = key
                        elif len(part) >= 3 and part[1][0] == ":":
                            expression = "".join(t[0] for t in part[2:])
                        else:
                            part = []
                            continue
                        if key in properties:
                            duplicates.add(key)
                        properties[key] = expression
                    part = []
                else:
                    part.append(item)
                    if value in ("{", "[", "("):
                        depth += 1
                    elif value in ("}", "]", ")"):
                        depth -= 1
            if "ok" in properties:
                yield token.start(), properties, duplicates


def findings(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.md")):
        for start, code in fenced_examples(path.read_text(encoding="utf-8")):
            for offset, properties, duplicates in result_objects(code):
                number = start + code[:offset].count("\n")
                prefix = f"{path.relative_to(root)}:{number}: "
                if duplicates & {"ok", "terminal", "submitted", "status"}:
                    errors.append(prefix + "duplicate result field")
                ok = properties["ok"]
                terminal = properties.get("terminal")
                submitted = properties.get("submitted")
                if ok not in {"true", "false", "null"}:
                    errors.append(prefix + "ok must be a literal true, false or null; button presence is not success")
                if terminal not in {"true", "false"}:
                    errors.append(prefix + "terminal boolean literal missing")
                if submitted not in {"true", "false"}:
                    errors.append(prefix + "submitted boolean literal missing")
                if ok == "null" and terminal != "false":
                    errors.append(prefix + "pending result requires terminal=false")
                if ok in {"true", "false"} and terminal != "true":
                    errors.append(prefix + "final result requires terminal=true")
                statuses = re.findall(r'''["']([^"']+)["']''', properties.get("status", ""))
                if ok == "true" and "status" in properties and not re.fullmatch(r'''["'][^"']+["']''', properties["status"]):
                    errors.append(prefix + "success status must be an explicit verified state")
                if ok == "true" and any(status.lower() in INTERMEDIATE for status in statuses):
                    errors.append(prefix + "intermediate state uses ok=true")
    template = root / "patterns" / "operation-template.md"
    if not template.is_file():
        errors.append("operation-template.md: missing")
    else:
        text = template.read_text(encoding="utf-8")
        if "`ok` 只表示 terminal" not in text or '"terminal": true' not in text:
            errors.append("operation-template.md: terminal result contract missing")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = findings(root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("PASS: fenced operation results preserve terminal and submitted semantics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
