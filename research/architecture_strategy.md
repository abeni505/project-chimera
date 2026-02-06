# Architecture Strategy — Perception Layer & MCP

## Overview

This document explains how the Model Context Protocol (MCP) will implement the Perception layer for Project Chimera's autonomous influencers, and how MCP's standardized connectivity prevents the "Cognitive Overload" called out in the SRS business objectives. The approach uses spec-driven development: perception contracts (schemas, topics, and quality-of-service) are the baseline API between data sources, preprocessing agents, and higher-order cognitive agents.

## How MCP Enables the Perception Layer

- **Standardized connectivity & contracts:** MCP provides explicit, versioned message schemas and capability discovery. Each data source (webhook, scraper, sensor, stream) exposes what it emits (schema, sampling rate, confidence metadata). Consumers declare what they accept. This removes ad-hoc adapters and mismatched assumptions.

- **Decoupling via adapters/sidecars:** MCP encourages small connectors (sidecars) that translate proprietary inputs into MCP messages. Translation logic and feature extraction live at the edge, keeping core agents focused on interpretation rather than parsing.

- **Schema-driven filtering & validation:** Incoming data is validated against MCP schemas; invalid or low-value messages are dropped or routed to quarantine streams. This gate prevents noisy, malformed inputs from reaching cognitive agents.

- **Stream semantics, backpressure & QoS:** MCP supports streaming patterns with explicit flow-control and QoS attributes. Consumers can apply backpressure or request summaries instead of full streams, preventing downstream overload during bursts.

- **Metadata & provenance:** MCP messages carry consistent metadata (source, timestamp, confidence, schema_version). This enables downstream agents to reason about reliability and apply selective attention rules.

- **Aggregation & preprocessing primitives:** MCP enables dedicated perception agents that perform aggregation, deduplication, sensor fusion, and summarization in-spec. Higher-level cognitive agents operate on concise, fused events instead of raw signals.

- **Observability & introspection:** Uniform message framing makes telemetry, tracing, and sampling straightforward. Team can measure event rates, processing latencies, and error budgets per source.

## How This Prevents Cognitive Overload

Cognitive Overload in the SRS refers to the system (or human overseers) receiving too much uncurated, noisy input, causing poor decisions, latency spikes, or model context window exhaustion. MCP prevents this in several concrete ways:

- **Edge curation reduces raw volume:** Sidecars / ingress agents filter and pre-process at sources (sampling, token-budget-aware summarization), so only relevant tokens reach expensive model contexts.

- **Relevance scoring and priority routing:** Every MCP message includes relevance/confidence scores. Orchestrators route high-priority events to real-time consumers and low-priority items to batch pipelines.

- **Summarization & windowing:** Perception agents use rolling-window summarizers to compress repetitive signals into time-series summaries or single events, preserving signal but lowering cognitive load.

- **Backpressure & graceful degradation:** Flow-control prevents overload by dropping or degrading lower-priority feeds when capacity is constrained, rather than letting everything compete for the same context window.

- **Spec-driven expectations:** Because all producers and consumers share schemas, mismatches and unexpected fields are minimized—less manual debugging and fewer surprise inputs that can derail agents.

- **Provenance-informed decisioning:** Cognitive agents can ignore or down-weight inputs with low provenance/confidence scores, focusing compute and attention where it matters.

## Practical Recommendations (next steps)

1. Define an initial `mcp.perception` schema family. Include fields: `id`, `source`, `timestamp`, `type`, `payload`, `confidence`, `schema_version`, `relevance_score`, `trace_id`.

2. Implement a small sidecar template for common sources (HTTP webhook, RSS/scraper, file drop) that: validate → enrich (confidence) → dedupe → emit MCP messages.

3. Build a Perception Aggregator agent that subscribes to `mcp.perception.*`, performs sampling/summarization, and emits `mcp.perception.fused` events for cognitive agents.

4. Add runtime QoS controls and backpressure metrics: per-source rate limits, per-consumer token budgets, and an overload policy (throttle/queue/trim).

5. Write small integration tests (simulated high-volume bursts) to validate that the aggregator enforces backpressure and that cognitive agents receive condensed events.

## Example message (JSON sketch)

{
  "id": "uuid-1234",
  "source": "scraper/news-site-A",
  "timestamp": "2026-02-06T12:34:56Z",
  "type": "article.summary",
  "payload": { "summary": "...", "keywords": ["policy","launch"] },
  "confidence": 0.87,
  "relevance_score": 0.62,
  "schema_version": "mcp.perception.v1",
  "trace_id": "trace-xyz"
}

## Closing

Using MCP as the spec-driven substrate for perception turns noisy heterogenous inputs into a managed, observable, prioritized feed of events. That design directly addresses the SRS goal of avoiding Cognitive Overload by shifting curation earlier, making attention explicit, and enabling reliable QoS controls.

---
Proposed next action: finalize `mcp.perception` schema and commit the sidecar template.
