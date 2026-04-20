---
description: Analyze the usage of datadog logs in the codebase and gather information about the logging events, data collection, and reporting. Summarize your findings in a clear and concise manner.
user-invocable: true
---

Analyze the source code and find all Datadog logging points and their details (log events, data collection, reporting, etc.), including mobile-specific instrumentation for Android and iOS.

# Requirements

## Logging
- Find all Datadog logging points in the codebase.
- For each Datadog logging point, extract the following details:
  - Log event name or identifier
  - Log level (e.g., INFO, WARN, ERROR)
  - Log message format
  - Data being logged
  - Reporting or alerting configuration

## Privacy & Consent
- Find tracking consent configuration (`TrackingConsent`).
- Note any PII scrubbing, masking, or GDPR-related logic.

## Crash Reporting
- Find crash/error reporting setup.

## App Lifecycle & Performance
- Find app lifecycle event tracking (background/foreground transitions, cold/warm/hot starts).
- Find performance metric collection (FPS, CPU, memory).

## Network & Batching
- Find network condition handling and batch upload configuration (batch size, upload frequency, connectivity-based deferral).

# Search Hints
Use these patterns to locate relevant code:

| Category | Android patterns | iOS patterns |
|---|---|---|
| SDK init | `Datadog.initialize`, `Configuration.Builder` | `Datadog.initialize`, `Datadog.Configuration` |
| Logs | `Logger.d`, `Logger.i`, `Logger.w`, `Logger.e` | `Logger.debug`, `Logger.info`, `Logger.warn`, `Logger.error` |
| Traces | `Tracer`, `buildSpan` | `Tracer`, `startSpan` |
| Consent | `TrackingConsent` | `TrackingConsent` |
| Custom attributes | `addAttribute`, `setExtraInfo` | `addAttribute`, `setExtraInfo` |

# Format
Output the results in a structured format. For example:

```
# Overview
| Level | Message | Screen | Trigger |
|----------|--------|------------------|-----------------|
| INFO | User login successful | Login Screen | User submits login form |
| ERROR | Failed to fetch user data | User Profile Screen | API request fails |

# SDK Configuration
| Setting | Value |
|---------|-------|
| Environment | production |
| Sample Rate | 100% |
| Tracking Consent | .granted |

