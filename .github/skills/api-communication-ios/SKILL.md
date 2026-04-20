---
name: api-communication-ios
description: Use when you need to analyze the iOS source code and find all API communication points and their details.
---

# Goal

Given a feature package path (e.g. `mobile-next-gen-ios/Packages/PctyPunch/Sources/PctyPunch`), find and describe all API communication: endpoints, HTTP methods, request bodies, response bodies, query parameters, authentication, and service targets.

# Step-by-step Instructions

## Step 1 — Find Endpoint Definitions

Search for files matching `*Endpoints.swift` inside the feature package's `Api/` folder. A feature may have **multiple** endpoint files (e.g. `SchedulingApiEndpoints.swift`, `TimeApiEndpoints.swift`).

Each endpoint file contains an `enum` conforming to `ApiEndpointProvider`. Read the full file and extract from each enum case:

| Field | Where to find it |
|---|---|
| **Endpoint name** | The enum case name (e.g. `.approvals(identity:)`) |
| **URL path** | The string inside `#apiPath("...")` or `untrackedPath:` — treat `\(variable)` segments as path parameters |
| **HTTP method** | The `method:` argument on `ApiEndpoint(...)`. If omitted, the default is `GET` |
| **Auth type** | The `auth:` argument. If omitted, the default is `.sentinet` |
| **Service** | The `service:` argument. If omitted, the default is `.apiGateway` |

## Step 2 — Find API Implementation Classes

Search for files matching `*Api.swift` or `*ApiImpl.swift` in the same `Api/` folder (or subfolders). These are mostly `final class` types that hold a `private let api: ApiProvider<SomeEndpoints>`.

For **each method** in the API class, extract:

| Field | Where to find it |
|---|---|
| **Endpoint used** | The `endpoint:` argument in `api.call(...)` — matches a case from the endpoints enum |
| **Query parameters** | The `parameters:` argument — a `[String: Any]` dictionary. Note which values are hardcoded vs dynamic |
| **Request body** | The `data:` argument. Common forms: `.encodable(someStruct)`, `.dictionary([...])`, `.multipart(...)`. If absent or `.empty`, there is no request body |
| **Response type** | Determined by the `api.call(...)` return type, or subsequent code. If the call returns `T` where `T: Decodable`, the response JSON is decoded into that type. If it returns `ApiResult`, the raw response is used (no typed body). If it returns `[String: Any]`, the response is an untyped dictionary |
| **Extra headers** | The `headers:` argument, if present |
| **Retry policy** | The `retryPolicy:` argument (e.g. `.readData`, `.noRetry`, `.safeWrite`) |

### Edge case: Direct API call without an endpoint case

In some cases, the API class may call `api.call(...)` directly with an inline endpoint definition instead of using a predefined enum case. For example:

```swift
try await api.call(endpoint: .init(path: "/custom/path", method: .post), data: ...)
```

In such cases, extract the endpoint details directly from the inline definition.

### How to identify the response type

The generic overload `api.call<Result: Decodable>(endpoint:...) async throws -> Result` auto-decodes the response. The concrete return type of the enclosing method tells you the response struct. For example:

```swift
func fetchApprovals() async throws -> TasksData {
    try await api.call(endpoint: .approvals(...), retryPolicy: .readData)
}
```

Here, `TasksData` is the response type.

When the method does `let _: ApiResult = try await api.call(...)` or returns `Void` after calling, there is **no typed response body**.

When the method manually calls `.asDecodable()` on an `ApiResult`, the type argument to `.asDecodable()` is the response type.

When pagination is used, look for `result.nextPageToken` — this reads a token from response headers.

## Step 3 — Find Request/Response Structures

For every request and response type identified in Step 2, locate the struct definition. These are typically in:
- The `Api/Models/` subfolder
- The `Models/` folder at the package root
- Inline in the same file

Read the full struct. For each field, record:

| Field detail | What to note |
|---|---|
| **Field name** | The property name (this matches the JSON key after key decoding, see below) |
| **Type** | The Swift type. `String`, `Int`, `Bool`, `Date`, `Decimal`, nested structs, arrays, optionals |
| **Property wrappers** | `@MixedDateValue<Formatter>` = date with flexible parsing; `@MixedDateOptionalValue<Formatter>` = optional date; `@StringValue` = accepts both string and int from JSON, etc. |
| **Nested types** | If a field's type is another struct, read that struct too (recursively) |
| **Enums with `UnknownDecodable`** | Enums that conform to `UnknownDecodable` have a `.unknown` fallback case — list all known cases only |
| **`Encodable` vs `Decodable` vs `Codable`** | `Encodable`-only = request body. `Decodable`-only = response body. `Codable` = potentially both |

### JSON key mapping

By default, property names directly map to JSON keys, e.g. `firstName` → `"firstName"`. In case the mapping is different, there always is a `CodingKeys` enum implemented in the struct that explicitly maps each property to a JSON key, using the following format:

```swift
struct Example: Codable {
    let firstName: String

    enum CodingKeys: String, CodingKey {
        case firstName = "first_name" // case <property-name> = "<json-key>"
    }
```

For request encoding, `JSONEncoders.default` uses `.sortedKeys` and ISO 8601 dates. Some types opt into `CustomJSONEncodingStrategy` with `.uppercase` key encoding (first character uppercased).

### `ApiRequiredFields`

If a response struct conforms to `ApiRequiredFields`, it declares a `requiredFields` string that gets appended as `?fields=...` query parameter automatically. Note this in the endpoint description.

### Edge case: date/time properties represented as `String`

If a date/time property is represented as `String`, it is probably parsed with custom logic later in code. Search the module for the property name to find where it is parsed. The usage will mostly be `DateFormatters.xFormatter.string(from: dateString)` (may be split across multiple variables).

---

# Reference: File Location Patterns

```
Packages/PctyFeatureName/
  Sources/PctyFeatureName/
    Api/
      FeatureEndpoints.swift          # enum: ApiEndpointProvider
      FeatureApi.swift                # class wrapping ApiProvider<FeatureEndpoints>
      Models/                         # Request/Response Codable structs
    Models/                           # May also contain API-related structs
```

A feature may have **multiple endpoint enums and API classes** organized into subfolders (e.g. `Api/ContactApi/`, `Api/SecurityApi/`). Search the entire `Api/` directory tree.

# Reference: `ApiAuth` Values

| Value | Meaning |
|---|---|
| `.none` | No authentication |
| `.deviceIdentification` | Device ID header only (unauthenticated) |
| `.sentinet` | **Default** — gateway token + encryption key |
| `.mobileService` | Legacy JWT-based auth |
| `.mobileServiceNextGen` | Gateway token forwarded to next-gen service |
| `.chat` | Chat service auth |
| `.airbase` | Airbase service auth |

# Reference: `ApiEndpointService` Values

| Value | Meaning |
|---|---|
| `.apiGateway` | **Default** — main API gateway |
| `.apiGatewayPublic` | Public API gateway (no auth required) |
| `.mobileService` | Legacy mobile service |
| `.mobileServiceNextGen` | Next-gen mobile service |
| `.spApiServer` | SP API server |
| `.spLiveServer` | SP Live server |
| `.spCoeServer` | SP COE server |

# Reference: `ApiRetryPolicy` Values

| Value | Meaning |
|---|---|
| `.readData` | Read operations — safe to retry |
| `.noRetry` | No automatic retry (except token refresh on 401) |
| `.safeWrite` | Idempotent write operations (e.g. toggle, delete) |
| `.writeWithIdempotencyKey` | Write with idempotency key header |
| `.authorization` | Login / account switch flows |
| `.noRetryOnUnauthorized` | External auth — skip token refresh on 401 |

# Reference: `ApiData` Request Body Types

| Value | Meaning |
|---|---|
| `.encodable(someStruct)` | JSON body from an `Encodable` struct — **find and read that struct** |
| `.dictionary([String: Any])` | Inline JSON dictionary — read keys/values directly from the call site |
| `.dictionaries([[String: Any]])` | Array of JSON objects |
| `.multipart(content:boundary:)` | Multipart form data (file uploads) |
| `.jsonData(Data)` | Pre-serialized JSON data - **find the data origin** |
| `.rawData(Data)` | Raw binary data - **find the data origin** |
| `.stream(provider, contentType:)` | Streamed body |
| `.empty` or absent | No request body |

# Reference: Common Codable Property Wrappers

| Wrapper | Meaning |
|---|---|
| `@MixedDateValue<Formatter>` | Required `Date` field — tries multiple date formats |
| `@MixedDateOptionalValue<Formatter>` | Optional `Date` field |
| `@StringValue` | Accepts both `String` and `Int` JSON values, stored as `String` |

# Reference: `UnknownDecodable` Enums

Enums conforming to `UnknownDecodable` must have an `.unknown` case. Unknown server values decode to `.unknown` instead of causing a decoding failure. List all known cases when documenting these.

# Reference: `@KrakenD` Aggregated Responses

Structs annotated with `@KrakenD` represent aggregated API responses (multiple backend calls merged by KrakenD gateway). Each field is wrapped as `Result<T, KrakenDError>` allowing partial failures. These are called via `api.call(endpoint:responseType:)` overload.
