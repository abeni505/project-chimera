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
## Formal Acceptance Criteria (Gherkin)

Scenario: Successful Trend Fetching
	Given the system has valid API credentials and `perception:youtube:raw` contains recent events
	When a client calls `GET /api/analytics/trends?platform=youtube&time_window=PT1H&top_k=10`
	Then the system returns HTTP 200 with a JSON body containing `trends` (top 10 topics), `metrics`, and `time_window` matching the request

Scenario: Video Metadata Generation
	Given a `content_tasks` row exists with `task_type = "video_generation"` and valid `inputs`
	When the Orchestrator assigns the task to a Video Gen Worker and the worker completes rendering
	Then an entry in `video_metadata` is created with `approved = false`, a `checksum`, and `thumbnail_uri` and a `mcp.video.generated` event is emitted

Scenario: Failed API Authentication
	Given a sidecar uses invalid or expired credentials to fetch external metadata
	When the adapter receives an HTTP 401 from the external API
	Then the adapter records the failure in logs, emits a `perception.error` event with error details, and the Orchestrator returns HTTP 401 for the inbound request

## Backend REST API (examples)

All endpoints use JSON. These are canonical examples; the Orchestrator must validate payloads against the Agent Task schema and perform RBAC checks.

1) Create Task
- POST /api/tasks/create
	- Request JSON:
		```json
		{
			"id": "task-123",
			"task_type": "video_generation",
			"created_by": "planner-service",
			"inputs": {"script": "Make a 30s promo...", "assets": []},
			"required_mcp_tools": ["adapters/storage"],
			"spec_reference": "specs/openclaw_integration.md",
			"budget_limit": {"amount": 50, "currency": "USD"}
		}
		```
	- Success Response (201):
		```json
		{"id": "task-123", "status": "pending", "created_at": "2026-02-06T15:00:00Z"}
		```

2) Fetch Trends
- GET /api/analytics/trends?platform=youtube&time_window=PT1H&top_k=10
	- Success Response (200):
		```json
		{
			"time_window": "PT1H",
			"platform": "youtube",
			"trends": [
				{"topic": "launch", "score": 0.92, "examples": ["vid1","vid2"]}
			],
			"metrics": {"volume": 12345}
		}
		```

3) Review Queue
- GET /api/review/queue?page=1&page_size=20
	- Success Response (200):
		```json
		{
			"items": [
				{"video_id": "vid-1", "thumbnail_uri": "/th/1.jpg", "task_id": "task-123", "created_at": "..."}
			],
			"total": 42
		}
		```

4) Approve Video (HITL)
- POST /api/video_metadata/{video_id}/approve
	- Request:
		```json
		{"approver_id": "user:alice", "notes": "OK to publish"}
		```
	- Success Response (200):
		```json
		{"status":"approved","video_id":"vid-1","published_at":"2026-02-06T15:05:00Z"}
		```

## Human-in-the-Loop (HITL) Points

- Safety Gate (Video Publication): After a Video Gen Worker produces `video_metadata` the orchestrator MUST pause the publish workflow and create a `user_approvals` draft with `decision = null`. The system must not set `video_metadata.approved = true` or call publisher adapters until a `user_approvals` row exists with `decision = 'approve'`.
- Timeout & Escalation: If no human approval is recorded within the configured timeout (e.g., 24 hours), the Orchestrator follows the escalation policy: (a) send notification to the on-call reviewer, (b) optionally retry once, (c) archive the `video_metadata` with `approved = false` and record the timeout in audit logs.
- Auditability: All HITL decisions must be recorded in `user_approvals` with `approver_id`, `notes`, `created_at`, and `spec_reference`.
