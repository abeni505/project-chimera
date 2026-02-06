# Adapter / Sidecar Pattern — Rule 3 Compliance

Purpose
-------
Provide a concise guide for implementers explaining the Adapter/Sidecar pattern required by Project Chimera's Prime Directive: all external connectivity must go through MCP-compatible adapters or sidecars.

Overview
--------
- Adapter: a small library/module inside `adapters/` that implements the protocol for a specific external capability (HTTP, payments, social API, telemetry, etc.). Adapters are imported by orchestrator or agent code and expose an MCP-compatible interface.
- Sidecar: a separate process or container that wraps third-party APIs and communicates with local agents over a local IPC or HTTP using the MCP transport framing; useful when network credentials, security, or async behavior must be isolated.

Why this pattern
-----------------
- Centralizes external connectivity behind a small, auditable surface.
- Enables capability discovery, provenance tracking, rate limiting, cost accounting, and secure credential handling.
- Makes enforcement (pre-commit/CI/orchestrator) straightforward: only `adapters/` or `sidecars/` are allowed to hold direct network calls.

Contract & Responsibilities
---------------------------
- Adapters MUST:
  - Expose a minimal MCP-friendly API (normalize inputs, outputs, metadata, provenance).
  - Validate inputs and sanitize/escape network parameters.
  - Emit structured logs and audit events (include `spec_reference` when applicable).
  - Implement retries/backoff and surface failure modes to orchestrator in a deterministic way.

- Sidecars MUST:
  - Run as a separate process or container and accept only local, authenticated calls.
  - Enforce credential isolation and rotate secrets independently of agent code.
  - Provide health endpoints, metric emission, and rate-limiting.

Implementation Checklist
------------------------
- Create an adapter under `adapters/<capability>/` (example: `adapters/http_adapter/`).
- Add a minimal public entrypoint (e.g., `adapters/http_adapter/__init__.py`) that exposes `request(mcp_event)` or a small typed client.
- Add unit tests in `tests/unit/adapters/` and integration tests in `tests/integration/`.
- Register any sidecar endpoints in `.vscode/mcp.json` (for local dev and orchestrator discovery).
- Ensure `tools/check_mcp_adapters.py` does not flag adapter files (it already skips `adapters/`).
- Add docs and usage examples in `skills/README.md` and the adapter folder.

Example Adapter Skeleton (Python)
---------------------------------
```py
# adapters/http_adapter/client.py
import requests

def request(event):
    # event => {method, url, headers, body, metadata}
    resp = requests.request(event['method'], event['url'], headers=event.get('headers'), data=event.get('body'))
    return {
        'status': resp.status_code,
        'body': resp.text,
        'provenance': {'adapter': 'http_adapter', 'timestamp': '...'}
    }
```

Sidecar Example (notes)
-----------------------
- Run a small HTTP server that accepts MCP-framed requests on `localhost` and forwards to external endpoints.
- Sidecar performs credential management and exposes metrics + health for orchestrator.

Compliance & Developer Workflow
-------------------------------
- Local: developers write code that imports adapters (not `requests`). Pre-commit will block direct network imports.
- CI: governance workflow runs `tools/check_mcp_adapters.py` and `pre-commit` to prevent bypassing local hooks.
- Runtime: orchestrator checks `required_mcp_tools` in task specs and enforces capability grants at execution time.

Best Practices
--------------
- Keep adapters minimal and focused; push complexity (retries, batching) into sidecars when needed.
- Document adapter public API and examples in the adapter folder.
- Keep secrets out of repository; store them in the orchestrator's secrets manager and sidecars only.

Checklist for PRs implementing external integrations
---------------------------------------------------
- [ ] Adapter or sidecar added under `adapters/` or `sidecars/`.
- [ ] Unit tests for adapter behavior added.
- [ ] `specs/technical.md` updated if new task types are introduced.
- [ ] `required_mcp_tools` and `budget_limit` added to sample `Agent Task` spec if required.
- [ ] CI and pre-commit pass (`pre-commit run --all-files`).

References
----------
- Prime Directive: `.cursor/rules`
- Adapter checker: `tools/check_mcp_adapters.py`
- MCP config example: `.vscode/mcp.json`

