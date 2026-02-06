import textwrap
from pathlib import Path

import tools.check_mcp_adapters as checker


def test_flags_import_requests_in_standard_file(tmp_path):
    p = tmp_path / "bad.py"
    p.write_text("import requests\n")

    viols = checker.find_violations(p)
    assert viols, "Expected violations for import requests in standard file"
    # ensure snippet contains the import
    assert any("import requests" in line for _, line, _, _ in viols)


def test_ignores_import_requests_in_adapters_folder(tmp_path):
    dir_adapters = tmp_path / "adapters"
    dir_adapters.mkdir()
    p = dir_adapters / "allowed.py"
    p.write_text("import requests\n")

    # find_violations will detect the import, but the linter should skip files
    # located inside adapters/; verify is_allowed returns True
    assert checker.is_allowed(p) is True
    viols = checker.find_violations(p)
    assert viols, "find_violations should still detect the pattern"
    # The main runner would skip this file because it's allowed
