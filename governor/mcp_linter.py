#!/usr/bin/env python3
"""Small wrapper exposing the MCP linter at `governor/mcp_linter.py`.

This file allows CI / Makefile to call a stable entrypoint.
"""

from tools.check_mcp_adapters import main
import sys


def run():
    return main()


if __name__ == "__main__":
    sys.exit(run())
