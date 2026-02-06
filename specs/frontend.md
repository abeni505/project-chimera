# Frontend Specification — Project Chimera

Purpose
-------
Define the frontend screens, component hierarchy, and user flows for human-in-the-loop review and operator monitoring. Each UI action maps to a specific Orchestrator API endpoint defined in `specs/technical.md`.

Screen Inventory
----------------
- Dashboard
  - Overview metrics: online influencers, queue length, recent approvals, system health.
  - Quick actions: open Review Queue, view Agent Monitoring.
- Content Review Queue
  - List of pending `video_metadata` items requiring human review.
  - Filters: influencer, priority, created_at, duration, confidence.
- Agent Monitoring View
  - Live registry of influencer `status` (online/idle/busy), capabilities, load, last_seen.
  - Search and drilldown into influencer details and recent tasks.
- Analytics Filter
  - Interface to query trending topics and metrics across platforms and time windows.

Component Hierarchy
-------------------
- App
  - NavBar
  - Routes: Dashboard, ReviewQueue, AgentMonitor, Analytics
- Dashboard
  - MetricsPanel
  - QuickActions
  - RecentApprovalsList
- ReviewQueue (page)
  - QueueFilters (controls)
  - QueueList (list component)
    - ApprovalCard (per-video row)
      - VideoPreview (thumbnail + small playable preview)
      - MetadataEditor (editable fields: title, tags, suggested_captions)
      - ApproveRejectControls
        - ApproveButton
        - RejectButton
      - AuditTrailLink (opens approval history)
- AgentMonitor
  - StatusTable (sortable rows)
  - AgentDetailModal (shows `content_tasks` and telemetry for influencer)
- Analytics
  - FiltersPanel
  - TrendsVisualization (charts)
  - ExportControls

Component Details
-----------------
- `ApprovalCard` contains:
  - `VideoPreview`: requests a small preview token from `GET /api/video_metadata/{video_id}` (field `preview_tokens`) and renders a low-bandwidth preview.
  - `MetadataEditor`: binds to `video_metadata` fields (`title`, `tags`, `thumbnail_uri`); saving invokes `POST /api/content_tasks` for metadata updates or `PATCH` endpoints (implementation-specific).
  - `ApproveButton`: when clicked, opens a confirmation modal and then calls `POST /api/video_metadata/{video_id}/approve` with `{approver_id, notes}`.
  - `RejectButton`: opens a rejection modal and then calls `POST /api/video_metadata/{video_id}/reject`.

User Flows
----------
Flow: Human reviews a video and clicks "Approve"
1. Operator opens `Review Queue` (UI loads via `GET /api/review/queue`) showing a paginated list of pending `video_metadata`.
2. Operator clicks an `ApprovalCard` to expand details. Frontend fetches the full record with `GET /api/video_metadata/{video_id}` and displays `video_metadata`, linked `content_tasks`, and `preview_tokens`.
3. Operator optionally edits metadata in `MetadataEditor`. If they save edits, the frontend calls `POST /api/content_tasks` (or `PATCH /api/content_tasks/{task_id}`) to create/update a small Agent Task that records the change; Orchestrator validates the task against the Agent Task schema.
4. Operator clicks `Approve`. Frontend shows a confirmation dialog summarizing action and required audit fields (approver identity is prefilled by session).
5. On confirmation, frontend performs:
   - POST /api/video_metadata/{video_id}/approve
     - Body: `{approver_id: "user:alice", notes: "Looks good", publish: true}`
   - The Orchestrator will:
     - Validate caller authorization.
     - Create a `user_approvals` row and set `video_metadata.approved = true`.
     - Stamp `published_at` and, if configured, enqueue publishing via the appropriate `adapters/moltbook/` adapter.
   - Frontend receives response `{status: 'approved', video_id, published_at}` and updates the card UI to show approved state and a link to the published post (if available).
6. System emits telemetry and audit logs; the `Review Queue` refreshes (`GET /api/review/queue`) to remove the approved item.

Flow: Operator rejects a video
1. Operator clicks `Reject` on the `ApprovalCard`.
2. UI opens rejection modal requesting mandatory `notes`.
3. On confirm, frontend calls `POST /api/video_metadata/{video_id}/reject` with `{approver_id, notes}`.
4. Orchestrator records `user_approvals` with `decision='reject'` and routes the `content_tasks` back to the worker for remediation or archives it.
5. UI updates to show rejection and next steps link.

Flow: Monitor an influencer
1. Operator opens `Agent Monitoring View` which calls `GET /api/agent_status`.
2. UI displays per-influencer rows with `status`, `capabilities`, `load`, and `last_seen`.
3. Operator clicks an influencer row → `AgentDetailModal` loads recent `content_tasks` via `GET /api/content_tasks?influencer_id={id}` and displays health metrics and recent approvals.

API mapping summary
-------------------
- `GET /api/review/queue` — Review Queue list
- `GET /api/video_metadata/{video_id}` — Load full video metadata and preview tokens
- `POST /api/video_metadata/{video_id}/approve` — Approve action (creates `user_approvals`, sets `approved=true`)
- `POST /api/video_metadata/{video_id}/reject` — Reject action
- `POST /api/content_tasks` — Record metadata edits or create small follow-up tasks
- `GET /api/agent_status` — Agent monitoring registry
- `GET /api/analytics/trends` — Analytics queries

Accessibility & Audit
---------------------
- All approval/rejection actions require explicit notes for non-trivial changes and must be recorded in `user_approvals` for auditability.
- UI actions that publish content must display a human-readable `spec_reference` and the audited `approver_id` and timestamp after action completes.

Security
--------
- Frontend must authenticate users and include an access token with each API call. The Orchestrator enforces RBAC and validates `spec_reference` on state-changing calls.

---

Generated for Project Chimera.
