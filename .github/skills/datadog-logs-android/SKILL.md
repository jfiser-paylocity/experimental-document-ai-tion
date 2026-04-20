---
name: datadog-logs-android
description: Analyze Datalog usages in Android projects
---

## SDK Initialization
- Find Datadog SDK initialization and configuration.
  - `Datadog.initialize`, `Configuration.Builder`
- Note client token, environment, service name, and sample rates.

## Tracing
- Find distributed tracing instrumentation:
  - `Tracer`, `buildSpan`