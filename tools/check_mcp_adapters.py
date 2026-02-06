#!/usr/bin/env python3
"""Check Python files for forbidden direct-network usage and suggest MCP adapters.

Exits with non-zero when violations are found. Intended for CI and local runs.
"""

import re
import subprocess
import sys
from pathlib import Path


FORBIDDEN_PATTERNS = {
    r"\bimport\s+requests\b": "use an MCP HTTP adapter / sidecar (e.g. adapters/http_adapter)",
    r"\brequests\.": "use an MCP HTTP adapter / sidecar (e.g. adapters/http_adapter)",
    r"\bimport\s+socket\b": "use an MCP socket adapter or sidecar",
    r"\bfrom\s+socket\s+import\b": "use an MCP socket adapter or sidecar",
    r"\bimport\s+http\.client\b": "use an MCP HTTP adapter / sidecar",
    r"\burllib\.request\b": "use an MCP HTTP adapter / sidecar",
    r"\bimport\s+aiohttp\b": "use an MCP async HTTP adapter / sidecar",
    r"\bimport\s+urllib3\b": "use an MCP HTTP adapter / sidecar",
}

ALLOWED_DIRS = ("adapters", "sidecars", "tests", ".venv", "venv", "__pycache__")


def git_tracked_python_files():
    out = subprocess.check_output(["git", "ls-files", "*.py"])  # bytes
    files = out.decode().splitlines()
    return [Path(p) for p in files if p]


def is_allowed(path: Path) -> bool:
    parts = path.parts
    return any(p in ALLOWED_DIRS for p in parts)


def find_violations(path: Path):
    violations = []
    text = path.read_text(encoding="utf8", errors="ignore")
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        for pattern, suggestion in FORBIDDEN_PATTERNS.items():
            if re.search(pattern, line):
                violations.append((i, line.strip(), pattern, suggestion))
    return violations


def main():
    files = git_tracked_python_files()
    all_violations = []
    for path in files:
        if is_allowed(path):
            continue
        viols = find_violations(path)
        if viols:
            all_violations.append((path, viols))

    if not all_violations:
        print("No disallowed direct network usage found.")
        return 0

    print("Direct network usage detected outside allowed locations:\n")
    for path, viols in all_violations:
        print(f"File: {path}")
        for lineno, snippet, pattern, suggestion in viols:
            print(f"  Line {lineno}: {snippet}")
            print(f"    Pattern: {pattern}")
            print(f"    Suggestion: {suggestion}\n")

    print(
        "Policy: Move external calls behind an MCP adapter or place code in adapters/ or sidecars/."
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
