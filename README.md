# Project Chimera — Architectural Summary

Strategic Objective
-------------------
Project Chimera's strategic objective is to evolve from hand-written scripts into an Autonomous Influencer Network powered by Fractal Orchestration: small, auditable agents coordinated by an orchestrator that applies global policy and local autonomy. The system emphasizes spec-driven behavior, provable safety controls, and observable execution so the network can scale without losing governance.

The Governance Stack
--------------------
- `specs/` — source of truth for task and agent contracts (e.g., `specs/technical.md` defines `Agent Task` JSON Schema including `required_mcp_tools` and `budget_limit`).
- `.cursor/rules` — Prime Directive: normative repo-level policies (Spec-Driven Development, Traceability, MCP-first). CI, pre-commit hooks, and runtime checks read these rules as authoritative guidance.
- `tools/check_mcp_adapters.py` + `governor/mcp_linter.py` — the automated MCP linter that detects forbidden direct-network imports and offers remediation guidance (file, line, snippet, suggested adapter).

Together these components form an automated safety net: authors must codify intent in `specs/`, local hooks block violations at commit-time, CI enforces the same policies on push, and the orchestrator validates runtime constraints before execution.

AI-Driven PR Review (Digital Supervisor)
----------------------------------------
We run an AI-driven Reviewer configured by `.coderabbit.yaml` that acts as the repository's Digital Supervisor for Pull Requests. The reviewer enforces three high-value policies automatically:

- **Spec Alignment:** Validates that any new or modified `Agent Task` artifacts conform to the `specs/technical.md` JSON Schema and require a `spec_reference` to a ratified spec.
- **Rule 3 (MCP-first):** Scans diffs for direct network usage (`requests`, `urllib`, raw `curl`, sockets, etc.) and flags or blocks any such usage unless it lives within an `adapters/` or `sidecars/` directory.
- **TDD Verification:** Checks that new features include unit tests under `tests/`; PRs changing source files without matching tests will be rejected with remediation guidance.

How the AI Reviewer functions as the Digital Supervisor:

- **Automated Gatekeeping:** The AI Reviewer runs on each PR and provides deterministic pass/fail results recorded in PR checks. It blocks merges that violate core governance rules, creating an enforcement layer before code reaches CI or production.
- **Contextual Guidance:** When it flags issues, the reviewer posts actionable comments with file/line examples and suggested fixes (for example, refactoring network calls into an `adapters/http_adapter/`).
- **Audit Trail:** Every AI review run is recorded in the PR checks and CI logs; combined with `specs/_meta.md` this creates a traceable record of policy compliance and remediation history.
- **Digital Supervision for Agentic Swarms:** For agentic systems, the reviewer enforces contract-first design and prevents agents from gaining unsanctioned network access. This helps keep agent behaviors scoped to ratified specs and centralizes external access through auditable adapters/sidecars.


Infrastructure as Code
----------------------
- `Makefile` targets:
  - `make test` — runs unit tests (`pytest`).
  - `make lint` — runs the MCP linter (`governor/mcp_linter.py`).
  - `make verify` — runs `test` then `lint` to verify the Factory readiness.
- GitHub Actions CI Gate: `.github/workflows/governance.yml` runs the linter and tests on push/PR, installs `pre-commit`, and verifies hooks with `pre-commit run --all-files`.

OpenClaw Alignment (Sidecar / Adapter pattern)
---------------------------------------------
Our Sidecar/Adapter pattern enforces Rule 3 (MCP-first external connectivity) and aligns with OpenClaw-style agentic social protocols by:
- Centralizing outbound calls through `adapters/` (language-level libraries) or `sidecars/` (isolated processes), enabling capability discovery and standardized message framing.
- Enforcing provenance, capability gating (`required_mcp_tools`), and `budget_limit` at the orchestrator layer before execution.
- Allowing sidecars to enforce credentials, rate limits, and policy independently from agent logic, matching social protocol expectations for accountable, auditable interactions.

Spec Kit Checklist
------------------
This repository contains the artifacts required for the GitHub Spec Kit-style governance challenge:

- `specs/` — Source of Truth specs (e.g., `specs/technical.md`).
- `governor/` — runtime guard (linter wrapper `mcp_linter.py`).
- `research/` — architecture notes and strategy (`research/architecture_strategy.md`).
- `tests/` — unit tests for validator and linter (`tests/unit/*`).
- `.github/workflows/` — CI Gate workflow (`governance.yml`).
- `.pre-commit-config.yaml` — local pre-commit hooks for early enforcement.
- `tools/check_mcp_adapters.py` — the policy checker used by CI and hooks.
- `skills/README.md` — adapter/sidecar pattern documentation.
- `Makefile` — `test`, `lint`, `verify` tasks to validate the Factory.

Dockerfile
----------------
A minimal `Dockerfile` has been added to the repository root. It installs `make` and the Python tooling required by the governance checks, installs pre-commit hooks, and runs `make verify` during image build to validate the Factory.

Next steps
----------
- Add a root-level `Dockerfile` (if required) that builds a verification image.
- Scaffold an `adapters/http_adapter/` example and a small sidecar skeleton for developer onboarding.
- Optionally, expand CI to publish an SBOM and automated security checks as part of governance.

---
Generated for Project Chimera on 2026-02-06.
