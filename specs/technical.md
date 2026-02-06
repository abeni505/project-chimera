# Technical Specification: Agent Task JSON Schema

Purpose
-------
This file defines the canonical JSON Schema for an Agent Task used by Project Chimera agents and orchestrators. The schema enforces a clear contract between task producers (planners, UIs) and consumers (agents, sidecars, execution engines). It explicitly includes `required_mcp_tools` and `budget_limit` to support Agentic Commerce and safe runtime enforcement.

JSON Schema
-----------
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Agent Task",
  "type": "object",
  "required": ["id", "task_type", "inputs", "required_mcp_tools", "budget_limit", "spec_reference"],
  "properties": {
    "id": {"type": "string", "pattern": "^[a-zA-Z0-9_\-:.]+$"},
    "title": {"type": "string"},
    "description": {"type": "string"},
    "task_type": {"type": "string"},
    "created_by": {"type": "string"},
    "created_at": {"type": "string", "format": "date-time"},
    "inputs": {"type": "object"},
    "outputs": {"type": "object"},
    "required_mcp_tools": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string", "format": "uri"},
      "description": "List of MCP-exposed tool URIs the agent must have access to before executing this task (e.g. mcp://payments/initiate)."
    },
    "spec_reference": {
      "type": "string",
      "description": "Path to the ratified specification that authorizes this task (must point to a file under specs/).",
      "pattern": "^specs\\\/[a-zA-Z0-9._-]+\\.md$"
    },
    "budget_limit": {
      "type": "object",
      "description": "Monetary or resource budget ceiling for the task (Agentic Commerce).",
      "required": ["amount", "currency"],
      "properties": {
        "amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "scope": {"type": "string", "enum": ["task", "step", "session"], "default": "task"}
      },
      "additionalProperties": false
    },
    "priority": {"type": "integer", "minimum": 0, "maximum": 10},
    "ttl_seconds": {"type": "integer", "minimum": 0},
    "constraints": {"type": "object"},
    "metadata": {"type": "object"}
  },
  "additionalProperties": false
}
```

Example
-------
```json
{
  "id": "order-creation-20260206-001",
  "title": "Create purchase order for social ad credit",
  "description": "Buy $500 of ad credit and return the confirmation ID.",
  "task_type": "transactional",
  # Technical Specification: Agent Task JSON Schema

  Purpose
  -------
  This file defines the canonical JSON Schema for an Agent Task used by Project Chimera agents and orchestrators. The schema enforces a clear contract between task producers (planners, UIs) and consumers (agents, sidecars, execution engines). It explicitly includes `required_mcp_tools` and `budget_limit` to support Agentic Commerce and safe runtime enforcement.

  JSON Schema
  -----------
  ```json
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Agent Task",
    "type": "object",
    "required": ["id", "task_type", "inputs", "required_mcp_tools", "budget_limit", "spec_reference"],
    "properties": {
      "id": {"type": "string", "pattern": "^[a-zA-Z0-9_\\-:.]+$"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "task_type": {"type": "string"},
      "created_by": {"type": "string"},
      "created_at": {"type": "string", "format": "date-time"},
      "inputs": {"type": "object"},
      "outputs": {"type": "object"},
      "required_mcp_tools": {
        "type": "array",
        "minItems": 1,
        "items": {"type": "string", "format": "uri"},
        "description": "List of MCP-exposed tool URIs the agent must have access to before executing this task (e.g. mcp://payments/initiate)."
      },
      "spec_reference": {
        "type": "string",
        "description": "Path to the ratified specification that authorizes this task (must point to a file under specs/).",
        "pattern": "^specs\\\/[a-zA-Z0-9._-]+\\.md$"
      },
      "budget_limit": {
        "type": "object",
        "description": "Monetary or resource budget ceiling for the task (Agentic Commerce).",
        "required": ["amount", "currency"],
        "properties": {
          "amount": {"type": "number", "minimum": 0},
          "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
          "scope": {"type": "string", "enum": ["task", "step", "session"], "default": "task"}
        },
        "additionalProperties": false
      },
      "priority": {"type": "integer", "minimum": 0, "maximum": 10},
      "ttl_seconds": {"type": "integer", "minimum": 0},
      "constraints": {"type": "object"},
      "metadata": {"type": "object"}
    },
    "additionalProperties": false
  }
  ```

  Example
  -------
  ```json
  {
    "id": "order-creation-20260206-001",
    "title": "Create purchase order for social ad credit",
    "description": "Buy $500 of ad credit and return the confirmation ID.",
    "task_type": "transactional",
    "created_by": "planner-service",
    "created_at": "2026-02-06T15:04:05Z",
    "inputs": {"account_id": "acct-123", "campaign": "spring-sale"},
    "required_mcp_tools": ["payments:initiate", "ads:purchaseCredit"],
    "budget_limit": {"amount": 500, "currency": "USD", "scope": "task"}
  }
  ```

  Why define schemas before writing Python code?
  ------------------------------------------------
  - **Clear contract:** A schema creates an unambiguous contract between producers and consumers so runtime components know exactly what to expect.
  - **Early validation:** Validating inputs at the boundary prevents malformed tasks from reaching agent runtime, reducing runtime errors.
  - **Safety & governance:** Fields like `budget_limit` are enforcement points for cost-control and compliance (prevents runaway spending in Agentic Commerce).
  - **Capability gating:** `required_mcp_tools` enumerates required capabilities; orchestrators can pre-check availability and access rights before execution.
  - **Easier testing & mocking:** Schemas enable automated test-case generation, consistent mocks, and deterministic simulations.
  - **Type generation & tooling:** Schemas allow automatic generation of type bindings, serializers, and validation code in Python (and other languages), accelerating development.
  - **Security & auditability:** Schemas force explicit provenance and constraints, making it easier to audit and reason about agent behavior.

  Next steps
  ----------
  - Review this schema against specific agent workflows in the SRS and provide any required additional fields (e.g., explicit `approval_required`, `cost_center`, or `legal_justification`).
  - After approval, I can generate a small Python validator module and unit tests that enforce this schema at runtime.

  ---

  ## Database & Data Management

  This section defines the canonical relational schema for the core system, a Mermaid ERD diagram, the high-velocity metadata strategy using Redis, and the Data Lifecycle for social metadata ingestion (YouTube/TikTok).

  ### PostgreSQL Schema (core tables)

  -- influencers: canonical influencer profiles
  CREATE TABLE IF NOT EXISTS influencers (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    profile_json JSONB,
    trust_score NUMERIC(3,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE
  );

  -- content_tasks: task-level records created by the orchestrator
  CREATE TABLE IF NOT EXISTS content_tasks (
    id TEXT PRIMARY KEY,
    influencer_id TEXT REFERENCES influencers(id) ON DELETE SET NULL,
    task_type TEXT NOT NULL,
    spec_reference TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    budget_limit JSONB,
    inputs JSONB,
    outputs JSONB,
    metadata JSONB
  );

  -- video_metadata: results produced by video generation workers
  CREATE TABLE IF NOT EXISTS video_metadata (
    id TEXT PRIMARY KEY,
    task_id TEXT REFERENCES content_tasks(id) ON DELETE CASCADE,
    influencer_id TEXT REFERENCES influencers(id) ON DELETE SET NULL,
    uri TEXT,
    duration_seconds INTEGER,
    format TEXT,
    checksum TEXT,
    thumbnail_uri TEXT,
    quality_metrics JSONB,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now(),
    published_at TIMESTAMPTZ
  );

  -- user_approvals: human review records (Safety Gate)
  CREATE TABLE IF NOT EXISTS user_approvals (
    id TEXT PRIMARY KEY,
    video_id TEXT REFERENCES video_metadata(id) ON DELETE CASCADE,
    approver_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('approve','reject')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    spec_reference TEXT
  );

  Indexes & performance notes:
  - Index `content_tasks (influencer_id, status)` for scheduling queries.
  - Index `video_metadata (influencer_id, approved, created_at)` for publishable content lookups.
  - Consider partial indexes for `approved = true` and for retention/archival pipelines.

  ### Mermaid ERD

  ```mermaid
  erDiagram
    INFLUENCERS ||--o{ CONTENT_TASKS : creates
    CONTENT_TASKS ||--o{ VIDEO_METADATA : produces
    VIDEO_METADATA ||--o{ USER_APPROVALS : reviewed_by
    INFLUENCERS {
      string id PK
      string display_name
      timestamp created_at
    }
    CONTENT_TASKS {
      string id PK
      string influencer_id FK
      string task_type
      string status
    }
    VIDEO_METADATA {
      string id PK
      string task_id FK
      string influencer_id FK
      string uri
      boolean approved
    }
    USER_APPROVALS {
      string id PK
      string video_id FK
      string approver_id
      string decision
    }
  ```

  ### High-Velocity Metadata Strategy (Redis)

  - Use Redis Streams (`XADD` / `XREADGROUP`) as the low-latency frontier for perception and trend events.
  - Ingress sidecars push raw or validated social metadata (YouTube/TikTok fetches) into namespaced streams like `perception:youtube:raw` and `perception:tiktok:raw`.
  - Perception Aggregators consume streams, dedupe, enrich (e.g., add `relevance_score`, language tags), and push condensed messages to `perception:fused` and to a separate Redis keyspace for fast lookup (e.g., `trends:current:<region>` with TTL).
  - Use Redis for:
    - Real-time counters and sliding window metrics (INCR, HLL, sorted sets for top-k)
    - Short-lived caches for `last_seen` and `current_load`
    - Work queues for fast task handoff to lightweight workers
  - Durability: checkpoint stream consumer offsets by writing consumer group positions and critical fused events to PostgreSQL periodically to prevent data loss on Redis failures.

  Scaling & operational notes:
  - Use Redis Cluster for scale and HA; set appropriate memory eviction and TTL policies for metric keys.
  - Monitor stream lengths and consumer lag; alert when backlog grows beyond configured thresholds.

  ### Data Lifecycle: YouTube/TikTok metadata

  1. Ingestion
     - Sidecars/adapters (`adapters/youtube_adapter/`, `adapters/tiktok_adapter/`) fetch metadata via hosted APIs or web scraping.
     - Sidecars validate against `mcp.perception` schemas, add provenance, and push raw events into Redis streams `perception:<platform>:raw`.

  2. Transformation & Enrichment
     - Perception Aggregators consume raw streams, perform deduplication, entity extraction, sentiment analysis, and compute `relevance_score` and `confidence`.
     - Aggregators emit `perception:fused` events containing condensed metadata and examples, and write transient summaries into Redis keys for fast serving.

  3. Validation & Safety Gate
     - For video generation outputs, orchestrator creates a `content_tasks` row and a `video_metadata` draft entry (approved=false).
     - The orchestrator calls the HITL tool `mcp.tools.safety_gate.human_approval` which records a `user_approvals` row on decision.

  4. Storage & Publication
     - On approval, `video_metadata.approved` is set to true and `published_at` is stamped. Downstream publisher adapters read approved rows and publish to `MoltBook` or external channels.
     - Aggregated analytics and long-term trend data are periodically flushed from Redis to PostgreSQL analytic tables (e.g., daily rollups) to enable historical queries.

  5. Retention & Archival
     - Redis data: short TTLs (minutes–hours) depending on sampling cadence; automated eviction for old keys.
     - PostgreSQL: keep canonical records for influencer profiles and approvals indefinitely (or per org policy), archive large historical tables to cheaper storage via partitioning and export jobs (CSV/Parquet to object storage).

  Security & Compliance
  - Ensure sidecars redact PII before pushing to shared Redis streams if required by policy.
  - All cross-service writes to PostgreSQL must be parameterized and use DB user roles scoped to necessary privileges.
  - Approval records (`user_approvals`) must be tamper-evident: record reviewer identity and store integrity checksums if regulatory provenance is required.

  ---

  Generated by the architecting phase for Project Chimera.

  ## API Endpoints

  This section lists the canonical HTTP API endpoints the Orchestrator exposes for frontend and adapter clients. All endpoints should be authenticated and respect RBAC rules. Responses use JSON and follow the canonical schema fragments above (e.g., `content_tasks`, `video_metadata`).

  ### Influencers
  - GET /api/influencers
    - Query: pagination, filter by `is_active`
    - Response: `{items: [{id, display_name, trust_score, profile_json, is_active}], total}`

  - GET /api/influencers/{influencer_id}
    - Response: influencer record (as `influencers` table row)

  ### Content Tasks
  - POST /api/content_tasks
    - Body: Agent Task object (validated against Agent Task JSON Schema)
    - Response: `{id, status, created_at}` (creates `content_tasks` row)

  - GET /api/content_tasks/{task_id}
    - Response: task row including `inputs`, `outputs`, `status`, `spec_reference`

  ### Review Queue & Video Metadata
  - GET /api/review/queue
    - Query: pagination, filters (influencer_id, priority)
    - Response: list of `video_metadata` items where `approved=false` plus short preview data (thumbnail_uri, duration_seconds, checksum, task_id)

  - GET /api/video_metadata/{video_id}
    - Response: full `video_metadata` row and linked `content_tasks` info

  - POST /api/video_metadata/{video_id}/approve
    - Body: `{approver_id: string, notes?: string}`
    - Behavior: creates `user_approvals` row, sets `video_metadata.approved = true`, stamps `published_at` (if publish requested) and returns `{status: 'approved', video_id, published_at}`

  - POST /api/video_metadata/{video_id}/reject
    - Body: `{approver_id: string, notes?: string}`
    - Behavior: creates `user_approvals` row with `decision='reject'`, optionally triggers remediation workflow for `content_tasks`

  ### Agent / Influencer Monitoring
  - GET /api/agent_status
    - Query: optional influencer_id
    - Response: current status registry pulled from Redis / Orchestrator cache `{items: [{influencer_id, status, capabilities, load, last_seen, trust_score}]}`

  ### Analytics & Trends
  - GET /api/analytics/trends
    - Query: `platform`, `region`, `time_window`, `top_k`
    - Response: trending topics and aggregated metrics (pulled from Postgres rollups or Redis fast keys)

  ### Notes
  - All POST endpoints that change state must validate `spec_reference` presence and check authorizations.
  - `POST /api/video_metadata/{id}/approve` is the canonical endpoint the frontend calls when a human clicks Approve (this call results in writing to `user_approvals` and toggling `video_metadata.approved`).
