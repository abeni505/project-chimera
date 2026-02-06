# OpenClaw Integration — Influencer Status Announcement

This document defines how Project Chimera announces an agent's `Influencer Status` using the `mcp.perception.v1` message family. The goal is to make influencer presence, capability, and readiness discoverable to downstream orchestrators, analytics, and the OpenClaw social layer.

Schema mapping (mcp.perception.v1)
---------------------------------
- `id` — UUID for the status event (e.g., `influencer-status-<uuid>`).
- `source` — origin identifier, e.g., `worker/influencer.<agent_id>`.
- `timestamp` — ISO-8601 event time when the status was emitted.
- `type` — `influencer.status.v1`.
- `payload` — object containing the status details:
  - `influencer_id`: canonical influencer id (string)
  - `status`: one of `online`, `idle`, `busy`, `maintenance`, `offline`
  - `capabilities`: list of capability descriptors (e.g., `video-gen:v2`, `captioning:v1`)
  - `current_task`: optional `Agent Task` summary or `null`
  - `load`: normalized 0.0–1.0 load indicator
  - `confidence`: confidence score in the status accuracy (0.0–1.0)
  - `schema_version`: `mcp.perception.v1`
- `relevance_score` — numeric priority hint used by orchestrators (0.0–1.0).
- `trace_id` — optional correlation id for debugging and provenance.

Publishing rules
----------------
- Only sidecars/adapters may publish `influencer.status.v1` events; workers must send status updates to their local adapter which then emits MCP events under the `mcp.perception.*` topics.
- Status events must include a `spec_reference` in the `payload` pointing to `specs/openclaw_integration.md` (or another ratified spec) to satisfy the Prime Directive.
- Frequency: `online`/`idle` heartbeats every 30s–2m depending on `relevance_score` and network policy. `busy` and `maintenance` states must be emitted immediately on change.
- QoS & TTL: use a short TTL for status heartbeats (e.g., 2x heartbeat interval) so stale statuses age out automatically from real-time buffers (Redis streams).

Orchestrator behavior
---------------------
- Subscribe to `mcp.perception.influencer.status` (or wildcard) and maintain a live registry of influencer states in memory and persisted snapshots in PostgreSQL for audit.
- Use `relevance_score`, `capabilities`, and `load` for task routing and scheduling decisions: prefer `online` influencers with matching `capabilities` and low `load`.
- If `confidence` < 0.5, schedule an active probing task (small `Agent Task`) to verify capability before assigning high-cost jobs.

OpenClaw announcement pattern
----------------------------
- For OpenClaw discovery, emit a derived `mcp.perception.openclaw.announce` event containing a minimal public profile:
  - `influencer_id`, `display_name`, `capabilities_public` (capabilities sanitized for external exposure), `last_seen`, and `trust_score`.
- Adapters responsible for publishing to the OpenClaw mesh must map internal metadata to public-safe fields and redact sensitive provenance tokens.

Storage & telemetry
-------------------
- Real-time registry: Redis streams hold the latest status events and provide a low-latency working set for the Orchestrator and schedulers.
- Canonical store: PostgreSQL persists status change events for audit, reporting, and historical analysis.
- Telemetry: record dropped/failed status events, stale status detections, and probe results for alerting.

Security & provenance
---------------------
- All status events must be signed or include adapter-issued provenance metadata. Orchestrator verifies adapter identity before trusting status updates.
- Network calls that publish status must live in `adapters/` per Rule 3; direct worker network usage is forbidden.

Example event (JSON)
--------------------
{
  "id": "influencer-status-2f4e8b9a",
  "source": "worker/influencer.alpha",
  "timestamp": "2026-02-06T12:45:00Z",
  "type": "influencer.status.v1",
  "payload": {
    "influencer_id": "alpha",
    "status": "online",
    "capabilities": ["video-gen:v2","captioning:v1"],
    "current_task": null,
    "load": 0.21,
    "confidence": 0.98,
    "schema_version": "mcp.perception.v1",
    "spec_reference": "specs/openclaw_integration.md"
  },
  "relevance_score": 0.75,
  "trace_id": "trace-abc-123"
}

Notes
-----
- Ensure adapters enforce privacy when announcing to external OpenClaw networks.
- Keep heartbeat cadence conservative in mobile or rate-limited environments; rely on event-driven state changes for fast updates.

Ratification
-----------
This integration spec should be ratified and referenced from `specs/_meta.md` before being relied upon by production orchestrators.
