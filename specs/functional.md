<!-- specs/functional.md -->
# Functional Specification: Agentic Influencer Network

Purpose
-------
Define the high-level goals and success criteria for Project Chimera's Agentic Influencer Network. This document complements the technical schema and provides the behavioral expectations planners and orchestrators must meet.

Strategic Goal
--------------
Transition from one-off scripts to a resilient, auditable Autonomous Influencer Network that coordinates many small agents using Fractal Orchestration. The network must be spec-driven, observable, and safe for Agentic Commerce.

Perception-Action Cycle
-----------------------
The network operates on a continuous Perception-Action Cycle:

- Perception: adapters/sidecars and MCP streams provide standardized sensory events (social signals, telemetry, external API events). Events are normalized, filtered, and semantically compressed by sidecars before being presented to planners.
- Planning: planners generate `Agent Task` objects (conforming to `specs/technical.md`) that include `spec_reference`, `required_mcp_tools`, and `budget_limit`.
- Action: orchestrator validates tasks (schema + policy), checks capability grants and budget, then assigns tasks to worker agents. Workers execute via MCP adapters/sidecars only.

Success Criteria
----------------
- All tasks are generated from ratified specs and include `spec_reference` (traceability requirement).
- No direct network calls from worker code — all external connectivity flows through adapters/sidecars (Prime Directive: see `.cursor/rules`).
- Economic safety: `budget_limit` present on all commerce tasks; operations that exceed project thresholds require explicit approval.

Governance link
---------------
This functional spec is ratified under the Prime Directive (`.cursor/rules`) and referenced in the specs registry (`specs/_meta.md`). CI and runtime validation enforce these behaviors.
