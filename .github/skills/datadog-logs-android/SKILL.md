---
name: datadog-logs-android
description: Analyze Datadog logging usages in Android projects via the app's Logger abstraction
---

## Architecture

The app does **not** call the Datadog SDK directly for logging. Instead, it uses an abstraction:

1. **`Logger`** (`base/src/main/java/.../logging/Logger.kt`) — singleton with methods: `info()`, `warning()`, `error()`, `debug()`, `verbose()`, `log()`, `logThrowable()`, `errorWithStackInfo()`.
2. **`DatadogLogger`** (`core-data/src/main/java/.../api/DataDogInitializer.kt`) — implements `Logger.ConsoleLogger`, wraps the Datadog SDK's `com.datadog.android.log.Logger`.
3. **`LogCategory`** (`base/src/main/java/.../logging/LogCategory.kt`) — sealed class. Each log call requires one or more categories (e.g., `LogCategory.Authentication`, `LogCategory.Api`, `LogCategory.Punch`).
4. **`LogLevel`** (`base/src/main/java/.../logging/LogLevel.kt`) — enum: `Debug`, `Info`, `Warning`, `Error`, `Verbose`. Maps to Android `Log.*` priorities.
5. **`LogAttribute`** (`base/src/main/java/.../logging/LogAttribute.kt`) — sealed interface for structured key-value metadata.

### How logs flow to Datadog
- `Logger.info("msg", LogCategory.X)` → enqueued → `DatadogLogger.log()` → formats message as `"(category) msg"`, maps attributes to `Map<String, Any>`, calls Datadog SDK `Logger.log(priority, message, attributes)`.

## SDK Initialization
- `DataDogInitializerImpl` in `core-data/.../api/DataDogInitializer.kt`.
- Calls `Datadog.initialize` with `Configuration.Builder(clientToken, env, variant, service)`.
- `service`: `"MobileNG_Android"`, `site`: `US1`, `crashReportsEnabled`: `true`, `trackingConsent`: `GRANTED`.
- Logger configured with `remoteLogThreshold`: `Info`, `remoteSampleRate`: `100%`, `bundleWithRum`: `false`.
- Default attributes on logger: `appRunId`, `appBuild`, `buildType`, `deviceId`, `flavor`, `googlePlayServicesVersion`, `osVersion`, `portalVersion`, `service`, `version`, `webViewVersion`, `isRooted`.
- Dynamic attributes set on user session change: `employeeId`, `companyId`, `userId`, `identityKey`, `userType`, `full_logs`, `selectedCompanyId`.

## Batch / Flow Loggers (Sub-Loggers)

Some modules use **sub-loggers** that accumulate messages in memory and flush them as a single Datadog log entry. These are important because individual `logMessage()` / `logButtonTapped()` / `logScreenShown()` calls do **not** appear as separate Datadog logs — only the final `submitLog()` call sends one combined log.

### Pattern
1. A class holds a `ConcurrentLinkedQueue<String>` (or similar buffer).
2. Methods like `logMessage()`, `logButtonTapped(buttonName)`, `logScreenShown(screenName)` append timestamped strings to the queue.
3. `submitLog()` drains the entire queue into a single string and calls `Logger.log(message, LogLevel.Info, LogCategory.X)` — producing **one** Datadog log with all accumulated lines.
4. `clearLog()` discards buffered messages without sending.
5. A crash-safety handler (`UncaughtExceptionHandler`) may auto-flush on crash.

### Known Sub-Loggers
| Sub-Logger | Module | Category | Interface File | Impl File |
|---|---|---|---|---|
| `PunchFlowLogger` | `punch-v2` | `LogCategory.Punch` | `punch-v2/.../flow/logging/PunchFlowLogger.kt` | `punch-v2/.../flow/logging/PunchFlowLoggerImpl.kt` |

### Finding Sub-Logger Usages
To find all points that feed into a sub-logger (and therefore into Datadog indirectly), search for:
- The sub-logger's method calls: `logMessage(`, `logButtonTapped(`, `logScreenShown(`, `submitLog(`, `clearLog(`
- Scope to the module: e.g., `includePattern: "punch-v2/**"`

These calls will **not** show up in a direct `Logger.*` search, so they must be searched separately.

## Finding Log Usages

### Direct Logger calls
Search for:
- `Logger.info(`, `Logger.warning(`, `Logger.error(`, `Logger.debug(`, `Logger.verbose(`
- `Logger.log(`, `Logger.logThrowable(`, `Logger.errorWithStackInfo(`
- **Do NOT search for** `Logger.d`, `Logger.i`, `Logger.w`, `Logger.e` — those are Datadog SDK patterns, not used directly.

### Indirect calls via sub-loggers
Search for each known sub-logger's methods (see table above). These accumulate messages that eventually reach Datadog via `submitLog()`.

To scope to a specific module, use `includePattern` with the module's directory (e.g., `"punch-v2/**"`, `"payroll/**"`).

### Search Methodology (CRITICAL)
1. **Always use `maxResults: 500`** (or higher) on every grep search. The default limit is low and WILL silently truncate results, causing you to miss logging calls.
2. **Use a single combined regex** for all Logger methods in one search: `Logger\.(info|warning|error|debug|verbose|log|logThrowable|errorWithStackInfo)\(` with `isRegexp: true`. This gives you one total count to verify against.
3. **Record the total match count** returned by grep. This is your ground truth.
4. **For each file that appears in grep results**, read the ENTIRE file (or at minimum every line that matched). Do NOT skip files or assume you've seen enough.
5. **After building your report, verify**: count your reported rows and confirm it matches the grep total. If it doesn't, find the gap.
6. **Files with many matches are the most dangerous** — if a file has 20+ matches, read it in large chunks (100+ lines at a time) and enumerate every single Logger call sequentially. Do NOT skim.
7. Repeat steps 1-6 separately for sub-logger patterns (e.g., `punchFlowLogger\.(logMessage|logButtonTapped|logScreenShown|submitLog|clearLog)`).

## Verification Protocol (MANDATORY)
After building your report, you MUST perform these steps before presenting results:

### Step 1: Count Match Totals
- Re-run the combined regex search (`Logger\.(info|warning|error|debug|verbose|log|logThrowable|errorWithStackInfo)\(`) with `maxResults: 500` and `isRegexp: true`, scoped to the target module.
- Record the **total match count** (e.g., "86 matches").
- Do the same for each sub-logger pattern (e.g., `punchFlowLogger\.(logMessage|logButtonTapped|logScreenShown|submitLog|clearLog)`).

### Step 2: Cross-Reference
- Count the rows in your Direct Logger Calls table.
- **The row count MUST equal the grep match count.** If it doesn't, you missed entries.
- Do the same for sub-logger tables.

### Step 3: Find Gaps
- If counts don't match, compare the list of files in grep results against files in your table.
- For any file where your table has fewer rows than grep shows matches, re-read that file and find the missing calls.
- **Files with the most matches are the most likely to have gaps** — double-check them first.

### Step 4: Report Counts
- At the end of your report, include a **Verification Summary**:
  ```
  ## Verification
  - Direct Logger calls: X grep matches → X table rows ✅
  - Sub-logger calls: Y grep matches → Y table rows ✅
  ```
- If any count is mismatched, fix it before presenting.

## Tracing
- `DataDogInitializerImpl` sets up `Trace` with `DatadogTracing.newTracerBuilder()`.
- Tracer tags mirror logger attributes plus `airbaseVersion`.
- `TracingHeaderType.DATADOG` for distributed tracing headers.
- `sampleRate`: `100%`, `bundleWithRum`: `false`.
