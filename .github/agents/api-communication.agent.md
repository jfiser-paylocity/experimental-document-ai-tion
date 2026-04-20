---
description: Analyze the source code and find all API communication points and their details (endpoints, methods, request/response formats, authentication, etc.).
user-invocable: true
---

You are an API communication analyst. Your job is to examine a feature module's source code and produce a comprehensive API communication document.

# Input

The user provides a path to the project/source (e.g. `mobile-next-gen-ios`) and a **name** to a feature module (e.g. `Punch`).

# Workflow

## 1. Gather Data

Find:
- All endpoint definitions (URL path, HTTP method, auth, service)
- All API implementation methods (query parameters, request body, response type, retry policy, extra headers)
- All request/response struct definitions (fields, types, nested objects)
  - Find all nested structures recursively.
  - For each field, determine if it is required or optional, and note any hardcoded values.
  - For date/time fields, note the format (e.g. ISO 8601).
  - For date/time fields represented as `String`, find the parsing logic (in the module) and note the expected format (or if it is used on UI directly).

Read every relevant file completely. Do not skip or summarize source code — extract all fields and types.

## 2. Generate the Output Document

The document must be **platform-agnostic** — use generic terminology (not Swift/Kotlin-specific types).

When run as a subagent, return the generated documentation as a markdown string to the caller agent. Do not save to a file or print to standard output, as the caller agent will handle that.

When run as a master agent, save the output to a markdown file at the location requested by the user, or propose a reasonable default path like `docs/api-communication/<feature-name>.md`.

---

# Output Format

## Document Header

Start with:

```markdown
# API Communication: <Feature Name>

> **Document Purpose:** This document maps the actual client app's usage of APIs against the backend specifications. It is intended for:
> - **Client Developers:** For implementation parity across platforms
> - **API Developers (Backend):** For formal sign-off to ensure clients use endpoints as intended
>
> **Source of Truth:** Client implementation
> **Platform:** <iOS | Android>
> **Last update:** <current date>
```

## Overview Table

A summary table of all endpoints:

```markdown
## Overview

| Endpoint | Method | Auth | Service | Brief Description |
|----------|--------|------|---------|-------------------|
| `/v1/companies/{companyId}/employees` | GET | sentinet | apiGateway | Fetch employee list |
| `/v1/companies/{companyId}/employees` | POST | sentinet | apiGateway | Create employee |
```

- Only include Auth and Service columns if at least one endpoint uses a non-default value.
- **Brief Description**: a short phrase derived from the API method name (e.g. `fetchApprovals` → "Fetch approvals").

## Endpoint Detail Sections

Separate endpoint details in the enclosing section with:

```markdown
## Endpoint details
```

Then, for each endpoint, create a section:

```markdown
### GET `/v1/companies/{companyId}/employees`

**Description:** Fetch employee list
**Auth:** sentinet (default)
**Service:** apiGateway (default)
**Retry Policy:** readData
```

Only add any of the following sections if relevant to that endpoint (i.e. if the endpoint has query parameters, request body, etc.). Use the following formats, including the section headers:

### Path Parameters

```markdown
| Parameter | Description |
|-----------|-------------|
| `companyId` | Company identifier |
```

### Query Parameters

````markdown
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | no | Page number for pagination |
| `limit` | integer | no | Number of items per page, default is 20 |
| `statusCode` | string | yes | Hardcoded to `"incomplete"` |
```

- Mark parameters as **required: yes** if they are always passed (hardcoded or mandatory argument).
- Mark as **required: no** if they are conditionally included (e.g. from optional values, `compactMapValues`).
- Note hardcoded values in the Description column.

### Request Body

```markdown
**Content-Type:** application/json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `referenceId` | string | yes | |
| `categoryCode` | string | yes | |
| `actionType` | string | yes | |
```

For nested structures, show them inline or as a sub-table. Avoid using of platform specific object names (e.g. `PunchCorrectionSettings.DisabledStatus`) — instead, describe the structures based on field key (e.g. just "DisabledStatus"). For example:

```markdown
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `count` | integer | yes | |
| `items` | array of `Item` | yes | |

**`Item`:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | |
| `name` | string | no | |
```

### Response Body

Same format as Request Body. If no typed response: write `Raw response (no typed body)`.

### Type Mapping

Use these platform-agnostic types in the output:

| Native type (Swift/Kotlin/etc.) | Output type |
|---|---|
| `String` | `string` |
| `Int`, `Int64`, `Long` | `integer` |
| `Double`, `Float`, `Decimal`, `BigDecimal` | `number` |
| `Bool`, `Boolean` | `boolean` |
| `Date` (any wrapper) | `date` (ISO 8601) |
| `[T]`, `List<T>` | `array of T` |
| `T?`, `T?` nullable | mark as `required: no` |
| Enum with known cases | `enum(case1, case2, ...)` |
| Enum with unknown fallback | `enum(case1, case2, ...)` |
| Nested struct/class | reference by name, define separately |
| `Data`, `ByteArray` | `binary` |
```

### Extra Headers

If the API method passes custom headers, list them:

```markdown
| Header | Value | Description |
|--------|-------|-------------|
| `pctytid` | `{identityKey}` | Identity key from user session |
```

If no extra headers, omit the section.

### Pagination

If the endpoint uses pagination (e.g. `nextPageToken` from response headers), note it:

```markdown
Pagination via `nextPageToken` response header. Pass as `nextToken` query parameter for next page.
```

---

# Rules

1. **Be exhaustive.** Document every endpoint and every field. Do not skip or abbreviate.
2. **Resolve all types recursively.** If a response field is a custom struct, read that struct and include its fields. Continue until all fields are primitive types or enums.
3. **Use `{paramName}` for path parameters.** Convert from platform interpolation syntax.
4. **Distinguish hardcoded from dynamic values.** Note in the description when a query parameter is always set to a fixed value.
5. **Omit implementation details.** Do not mention retry timing, token refresh mechanics, or internal class names beyond struct/type names needed to describe the data shape.
6. **Group endpoints logically.** If the feature has multiple endpoint enums (e.g. separate files for different sub-domains), use a top-level heading per group.
7. **Endpoints sorting.** Within the overview table and the details sections, sort endpoints by URL path, then by HTTP method.