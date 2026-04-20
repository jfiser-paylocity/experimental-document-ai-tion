---
description: Analyze the usage of datadog logs in the codebase and gather information about the logging events, data collection, and reporting. Summarize your findings in a clear and concise manner.
user-invocable: true
---

Analyze the source code and find **every single** logging point that is sent to Datadog, along with full contextual details.

**IMPORTANT**: This project uses an abstraction layer over the Datadog SDK. Do NOT search for raw Datadog SDK calls. Refer to the agent skills for platform-specific architecture, search patterns, search methodology, and SDK configuration details.

# Requirements

## 1. Direct Logger Calls
- Find ALL usages of the app's logging abstraction in the codebase (the specified module or all modules if none specified).
- Use the search patterns and methodology documented in the platform-specific skill file.
- **Do NOT stop early.** If a search returns many results, paginate or increase `maxResults`. Every single call site must be listed.
- For each logging call, extract **all** of the following:
  - **Log level** — the exact level
  - **Message** — the exact string or template passed to the log call (include interpolated variable names)
  - **Category/Categories** — the category value(s) used by the platform's logging abstraction
  - **Attributes** — every structured attribute or key-value pair passed; list each attribute name and its source value/variable
  - **Location** — full file path, class name, and function/method name
  - **Trigger — be maximally specific:**
    - If triggered by a **user action**: which UI element (button name, menu item, gesture), on which screen
    - If triggered by an **API call**: which endpoint / repository method, and whether it's on success, failure, or both
    - If triggered by an **error/exception**: which exception type, what operation failed
    - If triggered by a **lifecycle event**: which lifecycle callback
    - If triggered by a **background job or timer**: which job/worker, what schedule
    - If triggered by a **state change**: which state transition
    - If triggered by a **conditional check**: what condition is being evaluated
    - Include the **surrounding context** (e.g., "inside catch block of fetchPayroll()", "after successful biometric prompt")

## 2. Sub-Logger / Batch Logger Calls
Some modules use **sub-loggers** that accumulate messages in memory and flush them as a single Datadog log entry. Refer to the platform skill file for the list of known sub-loggers and their search patterns.

- Search for all known sub-logger method calls as documented in the skill.
- For each sub-logger call, extract the same details as above (level is determined at flush time — note the sub-logger's configured level from the skill file).
- Clearly mark these as **"Batched via [SubLoggerName]"** in the output.
- Also document where the flush / submit and clear methods are called, and what triggers them.

## 3. Crash Reporting
- Find crash/error reporting usages (e.g., throwable loggers, uncaught exception handlers in sub-loggers).
- For each, document the exception type caught and the context.

## 4. SDK Configuration
- Summarize SDK initialization configuration: environment, sample rate, tracking consent, default attributes, dynamic attributes, service name.

# Completeness Rules
- **NEVER skip, summarize, or group multiple log calls into one row.** Every individual call site gets its own row.
- **NEVER say "and similar" or "etc."** — list every single occurrence.
- **NEVER stop searching because you found "enough" results.** Exhaust all search patterns across all relevant files.
- If a module has 50 log calls, the output must have 50 rows for that module.
- **Follow the Verification Protocol in the platform skill file.** You MUST cross-reference grep match counts against your table row counts and resolve any discrepancies before presenting results.

# Search Settings (CRITICAL)
- **ALWAYS use `maxResults: 500`** on every grep search. The default limit silently truncates results.
- **Use combined regex patterns** (as specified in the skill) to get accurate total counts in a single search.
- **Read every file that appears in search results.** For files with many matches (10+), read the entire file in large chunks rather than small snippets.

# Format
Output the results in a structured format. (DO NOT GROUP OR AGGREGATE) For example:

```
# Direct Logger Calls
| # | Level | Message | Category | Attributes | File / Class.Function() | Trigger (detailed) |
|---|-------|---------|----------|------------|------------------------|--------------------|
| 1 | INFO | "User login successful" | Authentication | [userId, companyId] | login/…/LoginViewModel.onLoginSuccess() | User taps "Sign In" button on login screen; called after successful authentication API response |
| 2 | ERROR | "Failed to fetch user data: ${error.message}" | Api | [endpoint, statusCode, errorBody] | profile/…/ProfileRepository.fetchUser() | API returns non-2xx; inside catch block of fetchUser() |

# Sub-Logger Calls (Batched)
| # | Sub-Logger | Method | Message / Param | File / Class.Function() | Trigger (detailed) |
|---|-----------|--------|----------------|------------------------|--------------------|
| 1 | PunchFlowLogger | logScreenShown | "PunchConfirmation" | punch-v2/…/PunchConfirmationScreen.kt | Screen composable enters composition |
| 2 | PunchFlowLogger | logButtonTapped | "Submit" | punch-v2/…/PunchConfirmationScreen.kt | User taps "Submit" button on PunchConfirmation screen |
| 3 | PunchFlowLogger | submitLog | (flushes all) | punch-v2/…/PunchFlowViewModel.onPunchComplete() | Punch flow completes successfully after API confirms punch |

# Crash Reporting
| # | Method | Exception / Context | File / Class.Function() | Trigger |
|---|--------|--------------------|-----------------------|--------|

# SDK Configuration
| Setting | Value |
|---------|-------|
| Service Name | ... |
| Environment | ... |
| Sample Rate | ... |
| Tracking Consent | ... |
| Crash Reports | ... |
| Default Attributes | ... |
| Dynamic Attributes | ... |

