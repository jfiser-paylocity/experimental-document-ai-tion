---
description: Analyze the usage of datadog logs in the codebase and gather information about the logging events, data collection, and reporting. Summarize your findings in a clear and concise manner.
user-invocable: true
---

Analyze the source code and find **every single** logging point that is sent to Datadog, along with full contextual details and produce full table of the log points.
Create and save the summary in a markdown file in the repository. The file should be named `datadog-logs-analysis.md` and placed in the root directory. The summary should include:
- A comprehensive list of all log points sent to Datadog, including:
  - Log level
  - Log message or template (with variable names)
  - Log category or categories
  - Structured attributes (key-value pairs) with their source values/variables
  - Exact file path, class name, and function/method name for each log point
  - Detailed trigger information for each log point (e.g., user action, API call, error/exception, lifecycle event, background job, state change, conditional check)

**IMPORTANT**: Refer to the agent skills for platform-specific architecture, search patterns, search methodology, and SDK configuration details. 

# Requirements

## 1. Logger Calls
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
# Logger calls
| # | Level | Message | Category | Attributes | Method | Trigger (detailed) |
|---|-------|---------|----------|------------|------------------------|--------------------|
| 1 | INFO | "User login successful" | Authentication | [userId, companyId] | onLoginSuccess() | User taps "Sign In" button on login screen; called after successful authentication API response |
| 2 | ERROR | "Failed to fetch user data: ${error.message}" | Api | [endpoint, statusCode, errorBody] | fetchUser() | API returns non-2xx; inside catch block of fetchUser() |



