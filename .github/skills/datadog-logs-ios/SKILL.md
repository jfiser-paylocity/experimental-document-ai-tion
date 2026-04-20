---
name: datadog-logs-ios
description: Use when you need to analyze the iOS source code and find all Datadog log messages created in a specific feature module (package).
---

Given a feature package path (e.g. `mobile-next-gen-ios/Packages/PctyPunch/Sources/PctyPunch`), this is how to find and describe **every** log message that reaches Datadog from that module. Only direct logger calls in the module's own code should be considered, ignore any automatic API request/response logs triggered by the module's API calls.

# Architecture

The app does **not** call the Datadog SDK directly for logging. Instead, it uses an abstraction layer in `PctyCore`:

1. **`Logger`** (`Packages/PctyCore/Sources/PctyCore/Logger/Logger.swift`) — a protocol (`public protocol Logger`) with convenience extension methods: `debug()`, `info()`, `warning()`, `error()`, `log()`, `sensitiveLog()`.
2. **`LogCategory`** (`Packages/PctyCore/Sources/PctyCore/Logger/Parameters/LogCategory.swift`) — an enum. Every log call requires one or more categories (e.g. `.punch`, `.timeCardManagement`, `.api`).
3. **`LogLevel`** (`Packages/PctyCore/Sources/PctyCore/Logger/Parameters/LogLevel.swift`) — enum: `debug`, `info`, `warning`, `error`.
4. **`LogAttribute`** (`Packages/PctyCore/Sources/PctyCore/Logger/Parameters/LogAttribute.swift`) — enum for structured key-value metadata attached to logs (e.g. `.punchInfo(...)`, `.punchLocationInfo(...)`, `.apiCall(...)`, `.error(...)`, `.tcmInfo(...)`).
5. **`LogParameters`** (`Packages/PctyCore/Sources/PctyCore/Logger/Parameters/LogParameters.swift`) — bundles level, categories, attributes, date, file, and line into a single struct.

## How `core.logger` is accessed

Feature modules access the logger through the `Core` dependency injection graph:

- **ViewModels/Services** typically hold `private let core: Core` (or `CoreBase`) injected via init. They call `core.logger.warning(...)`.
- **Some classes** extract logger into a local property: `private let logger: Logger` (initialized from `core.logger`). They call `logger.warning(...)` directly.
- Both patterns reach the **same** pipeline. There is no difference in Datadog output.

## Datadog message format

The `DatadogLogger` formats the message as:

```
(category1, category2) [SourceFileName:lineNumber] Original message text
```

For example: `(punch) [PunchServiceImpl:354] PunchService: Punch is too old for submit, changing it to offline`

## Datadog attributes

Each log entry sent to Datadog can include these **per-log attributes** from `LogAttribute` cases:

| LogAttribute case | Attribute key in Datadog | Typical usage |
|---|---|---|
| `.punchInfo(encodable)` | `punchInfo` | Punch submit details |
| `.punchLocationInfo(encodable)` | `punchLocationInfo` | Location data during punch |
| `.tcmInfo(encodable)` | `timeCardManagementInfo` | Time card management context |
| `.apiCall(encodable)` | `apiCall` | API request/response info (auto-attached) |
| `.correlationId(string)` | `pcty-correlation-id` | Correlation ID for tracing |
| `.error(Error)` | `error` | Error details (auto-attached by `warning`/`error` convenience methods when `error:` parameter is provided) |
| `.airbase(encodable)` | `airbase` | Airbase-related data |
| `.portal(encodable)` | `portal` | Portal-related data |
| `.debug(encodable)` | `debug` | Debug-only data |
| `.pendoLog(encodable)` | `pendo` | Pendo analytics data |
| `.analytics(bool)` | `analytics` | Analytics flag |
| `.datadogCategoryOverride(category)` | `datadogCategoryOverride` | **Overrides** the `category` attribute in Datadog (replaces the array with only this category) |

# Step-by-step Instructions

## Step 1 — Find All Direct Logger Calls

Search the feature package's **Sources** directory for all logger calls using a single combined regex:

```
(core\.)?logger\.(info|warning|error|debug|log|sensitiveLog)\(
```

Record the **total match count** — this is your ground truth.

## Step 2 — Read and Extract Each Log Call

For **every file** that appears in the grep results, read the file and resolve these details for each log call:

| Field | Where to find it |
|---|---|
| **Log level** | The convenience method name: `info`, `warning`, `error`, `debug` — or the `level:` argument if using `log()` directly |
| **Message** | The first string argument. May be a string literal, string interpolation, or a variable. If interpolated, note what variables are included |
| **Error parameter** | If `error:` is provided (only on `warning` and `error` convenience methods), note the error source |
| **Categories** | The `LogCategory` values after the message (variadic). E.g. `.punch`, `.watch`, `.timeCardManagement` |
| **Attributes** | The `attributes:` parameter if present — array of `LogAttribute` values (e.g. `[.punchInfo(...), .punchLocationInfo(...)]`) |

### Special cases

- **`log()` method**: Uses explicit `level:` and `category:` parameters instead of convenience methods.
- **`sensitiveLog()`**: Has `protected:` and `unprotected:` message parameters instead of a single message. The `protected` version is what reaches Datadog in production; `unprotected` is used in debug/sandbox environments only.
- **Multi-line log calls**: The message or attributes may span multiple lines. Read enough context to capture the full call.

---

# Reference: Logger Call Signatures

```swift
// Convenience methods (most common):
core.logger.debug("message", .category1, .category2)
core.logger.info("message", .category1)
core.logger.warning(
    "message",
    error: someError,
    .category1,
    attributes: [.punchInfo(...)],
)
core.logger.error("message", error: someError, .category1, .category2)

// Explicit level:
core.logger.log("message", level: .info, category: .punch)
core.logger.log(
    "message",
    level: .error,
    category: .punch,
    attributes: [...],
)

// Sensitive log (redacted in production):
core.logger.sensitiveLog(
    protected: "redacted message",
    unprotected: "full message with \(sensitiveData)",
    level: .info,
    category: .api, .punch,
    attributes: [...]
)
```

# Reference: `LogLevel` Values

| Level | Datadog SDK method |
|---|---|
| `.debug` | `logger.debug(...)` |
| `.info` | `logger.info(...)` |
| `.warning` | `logger.warn(...)` |
| `.error` | `logger.error(...)` |
