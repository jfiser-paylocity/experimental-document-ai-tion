---
name: api-communication-android
description: Use when you need to analyze the Android source code and find all API communication points and their details.
---

# Goal

Given a feature module path (e.g. `punch/punch-impl`), find and describe all API communication: endpoints, HTTP methods, URL paths, request bodies, response bodies, query parameters, authentication, base URLs, retry policies, and tracing.

# Step-by-step Instructions

## Step 1 — Find API Interface Definitions

Search for files matching `*Api.kt` inside the feature module's `data/remote/` folder. A feature may have **multiple** API interfaces (e.g. `PunchApi.kt`, `ServerTimeApi.kt`, `TimeApi.kt`).

Each API interface extends either `Api` (kotlinx.serialization) or `LegacyApi` (Moshi). Read the full file and extract from each function:

| Field | Where to find it |
|---|---|
| **Function name** | The Kotlin function name (e.g. `getPunchState`, `addPunch`) |
| **HTTP method** | The Retrofit annotation: `@GET`, `@POST`, `@PUT`, `@PATCH`, `@DELETE`, `@HTTP` |
| **URL path** | The string argument of the HTTP method annotation — treat `{variable}` segments as path parameters |
| **Base URL** | The `baseUrl` argument on `@Endpoint(...)` |
| **Auth type** | The `auth` argument on `@Endpoint(...)` |
| **Retry policy** | The `retry` argument on `@Endpoint(...)` |
| **Endpoint type** | The `type` argument on `@Endpoint(...)`. If omitted, the default is `EndpointType.Default` |
| **Tracing** | If `@TracedRequest(parentTrace = ...)` is present, note the trace name |

### Interface Marker Types

| Marker | Serialization | Converter |
|---|---|---|
| `Api` | kotlinx.serialization (`@Serializable`) | `KotlinxSerializerFactory` |
| `LegacyApi` *(deprecated)* | Moshi (`@JsonClass(generateAdapter = true)`) | `MoshiConverterFactory` |

The marker determines which Retrofit instance (and thus which serializer) is used when the interface is created via `singleOf<MyApi>()` in the Koin DI module.

## Step 2 — Extract Parameter Details

For **each function** in the API interface, extract:

| Field | Where to find it |
|---|---|
| **Path parameters** | Parameters annotated with `@Path("name")` — substituted into `{name}` segments in the URL |
| **Query parameters** | Parameters annotated with `@Query("name")` — appended as `?name=value`. Note default values |
| **Request body** | Parameter annotated with `@Body` — find and read the DTO type |
| **Headers** | Parameters annotated with `@Header("name")` for dynamic headers. Also check for `@Headers("...")` annotation on the function for static headers |
| **Tags** | Parameters annotated with `@Tag` — commonly `LogCategory`, `LogAttribute`, or `ApiLogOverride`. These are metadata, not sent over the wire |
| **Multipart** | Functions annotated with `@Multipart` use `@Part` parameters for file/form uploads |

### Response Type

The return type of the function determines the response:

- **`SomeDto`** — JSON is deserialized into that DTO directly
- **`ResponseWrapperDto<SomeDto>`** — Response has `data` and `errors` fields; the actual payload is unwrapped via `.getOrThrow()`
- **`KrakenDResponse<SomeDto>`** — KrakenD aggregated response with partial error support (used with `type = EndpointType.KrakenD`)
- **`Response<SomeDto>`** — Retrofit `Response<T>` wrapper; provides access to response headers (e.g. pagination tokens via `X-Pcty-Next-Token`) and HTTP status code
- **`List<SomeDto>`** — JSON array deserialized into a list
- **`Unit` / no return type** — No response body expected

## Step 3 — Find Request/Response DTOs

For every request and response type identified in Step 2, locate the DTO definition. These are typically in:
- `data/dto/` subfolder within the feature module
- `data/model/` subfolder within the feature module
- Inline in the same file as the API interface

Read the full data class. For each field, record:

| Field detail | What to note |
|---|---|
| **Field name** | The property name |
| **JSON key** | For `@Serializable`: the `@SerialName("key")` value, or the property name if absent. For `@JsonClass`: the `@Json(name = "key")` value, or the property name if absent |
| **Type** | The Kotlin type: `String`, `Int`, `Long`, `Boolean`, `Double`, `LocalDate`, `LocalDateTime`, `Instant`, nested DTOs, `List<T>`, etc. |
| **Nullable** | Whether the type is nullable (`T?`) — nullable fields may be absent or `null` in JSON |
| **Default value** | If a default is specified (e.g. `= emptyList()`, `= null`), note it |
| **Nested types** | If a field's type is another DTO, read that DTO too (recursively) |

### Serialization Formats

**kotlinx.serialization** (for `Api` interfaces):
```kotlin
@Serializable
internal data class SomeRequestDto(
    @SerialName("fieldName") val fieldName: String,
    @SerialName("optionalField") val optionalField: Int? = null,
)
```

**Moshi** (for `LegacyApi` interfaces):
```kotlin
@JsonClass(generateAdapter = true)
internal data class SomeResponseDto(
    @Json(name = "fieldName") val fieldName: String,
    @Json(name = "optionalField") val optionalField: Int?,
)
```

### Enum Types

Enums in DTOs are typically `@Serializable` with `@SerialName` for each case, or Moshi-based with `@Json`. Some enums include an `Unknown` fallback case for forward compatibility.

### `ResponseWrapperDto<T>`

Some feature modules define their own `ResponseWrapperDto<T>` locally (not from a shared module). It wraps the response with:
```kotlin
@Serializable
data class ResponseWrapperDto<T>(
    @SerialName("data") val data: T? = null,
    @SerialName("errors") val errors: List<ErrorResponseDto> = emptyList(),
)
```
Use `.getOrThrow()` to unwrap: returns `data` if no errors, otherwise throws `ApiDataException`.

### `KrakenDResponse<T>`

For KrakenD aggregated endpoints (`type = EndpointType.KrakenD`):
```kotlin
data class KrakenDResponse<out T>(
    val data: T,
    val errors: Map<String, KrakenDErrorDto>,
)
```
Each field in `T` represents a backend sub-call. Errors are keyed by backend name. Use `.throwIfPartialError()` to fail on any partial error, or `.getOrThrow()` to unwrap non-null data.

## Step 4 — Find Repository Implementations

Search for `*RepositoryImpl.kt` or `*DataSource*.kt` in `data/repository/` within the feature module. These classes:
- Inject the API interface(s)
- Call API functions wrapped in `apiCall { }` (from `com.paylocity.paylocitymobile.coredata.repository.apiCall`)
- Map DTOs to domain models
- Return `Result<DomainModel>`

### `apiCall { }` Wrapper

The `apiCall` function wraps a suspend API call and:
- Catches exceptions and maps them to `ErrorResult` subtypes
- Re-throws `CancellationException` (coroutine cancellation)
- Maps `HttpException` to `ServerErrorResult` (with HTTP code and error body parsing)
- Maps `SocketTimeoutException` to `TimeoutErrorResult`
- Maps `UnknownHostException` to `UnknownHostErrorResult`
- Maps `JsonDataException` / `ApiDataException` to `ApiDataErrorResult`
- Detects emergency mode from specific HTTP status codes
- Detects force-upgrade requirements from response

### Parallel API Calls

Repositories commonly use `coroutineScope` with `async { apiCall { ... } }` to make multiple API calls in parallel, then `.await()` each result.

---

# Reference: File Location Patterns

```
feature-module/
├── feature-api/                              # Public API module
│   └── src/main/java/com/.../
│       ├── domain/
│       │   ├── model/                        # Domain models (public)
│       │   ├── repository/                   # Repository interfaces (public)
│       │   └── usecase/                      # Use case interfaces (public)
├── feature-impl/                             # Implementation module
│   └── src/main/java/com/.../
│       ├── data/
│       │   ├── remote/                       # API interfaces (*Api.kt)
│       │   ├── dto/                          # DTOs (@Serializable / @JsonClass)
│       │   ├── model/                        # Data-layer models
│       │   └── repository/                   # Repository implementations
│       ├── domain/
│       │   ├── model/                        # Domain models (internal)
│       │   ├── repository/                   # Repository interfaces (internal)
│       │   └── usecase/                      # Use case implementations
│       ├── presentation/                     # UI / ViewModel layer
│       └── di/                               # Koin modules (*KoinModule.kt)
```

Some feature modules use a flat structure without `api/impl` split:
```
feature-module/
└── src/main/java/com/.../
    ├── data/remote/                          # API interfaces
    ├── data/dto/                             # DTOs
    ├── data/repository/                      # Repository implementations
    ├── domain/                               # Domain layer
    └── di/                                   # DI modules
```

### Core Infrastructure

```
core-data/src/main/java/com/paylocity/paylocitymobile/coredata/
├── api/
│   ├── NetworkAnnotations.kt                # @Endpoint, BaseUrl, Auth, RetryPolicy enums
│   ├── Api.kt                               # Api / LegacyApi marker interfaces
│   ├── SingleOf.kt                          # singleOf<*Api>() DI extension
│   ├── AuthInterceptor.kt                   # Auth header injection + base URL routing
│   ├── HttpHeader.kt                        # HTTP header constants
│   ├── retry/
│   │   ├── RetryInterceptor.kt              # Retry logic
│   │   └── behaviour/                       # Per-policy retry behaviors
│   └── tracing/                             # Distributed tracing interceptors
├── model/
│   ├── KrakenDResponse.kt                   # KrakenD aggregated response wrapper
│   └── KrakenDErrorDto.kt                   # KrakenD error DTO
├── remote/                                   # Core API interfaces
├── repository/
│   ├── ApiHelper.kt                         # apiCall {} wrapper + error mapping
│   └── ApiLogOverride.kt                    # Per-endpoint log level override
└── di/
    └── CoreDataKoinModule.kt                # Retrofit + OkHttp + serializer setup
```

# Reference: `BaseUrl` Values

| Value | Meaning |
|---|---|
| `MobileServices` | Legacy mobile services backend |
| `NextGen` | Next-gen API gateway (authenticated) |
| `NextGenPublic` | Next-gen API gateway (public, no auth required) |
| `SentinetGateway` | **Most common** — Sentinet API gateway |
| `SpLiveServer` | SP Live server |
| `Provider` | Provider-specific server |
| `Empty` | No base URL override (URL used as-is) |
| `Scheduling` | Scheduling-specific server |
| `Payroll` | Payroll-specific server |

Base URLs are **not** hardcoded in Retrofit. The `AuthInterceptor` dynamically resolves the actual URL from the `BaseUrl` enum via `ApiAuthorization.getUrlFor(baseUrl)` and rewrites the request URL at runtime. This supports dynamic environment switching.

# Reference: `Auth` Values

| Value | Meaning |
|---|---|
| `None` | No authentication headers |
| `MobileServices` | Legacy JWT-based auth (`JWTToken` header) |
| `MobileServicesPublic` | Public mobile services (minimal auth) |
| `NextGen` | Next-gen gateway token + encryption key |
| `NextGenPublic` | Public next-gen gateway (no auth required) |
| `SentinetGateway` | **Most common** — Sentinet gateway token |
| `Chat` | Chat service authentication |
| `Airbase` | Airbase service authentication |
| `Video` | Video service authentication |
| `Coil` | Image loading authentication (Coil) |

Authentication headers are injected by `AuthInterceptor` based on the `Auth` value. On 401 responses, `RefreshTokenAuthenticator` automatically attempts a token refresh and retries the request (unless the endpoint is `Login`, `RefreshToken`, or has `NoRetryOnUnauthorized` tag).

# Reference: `RetryPolicy` Values

| Value | Meaning |
|---|---|
| `Read` | Read/fetch operations — safe to retry (exponential backoff) |
| `ReadTryReach` | Read that retries on network issues, but non-2xx codes are treated as valid results (not retried) |
| `Write` | Retryable write operations — resource must be idempotent/safe on server |
| `WriteWithIdempotency` | Same as `Write`, but injects an `Idempotency-Key` header to prevent duplicate processing |
| `WriteOnlyOnce` | Unsafe write — **no retry** to prevent data corruption |
| `WriteNoEmergency` | Normally retries like `Write`, but behaves like `WriteOnlyOnce` when in emergency mode |
| `Auth` | Auth-sensitive — minimal retries to avoid loops |
| `RefreshToken` | Token refresh — linear retry every 500ms |

Retry logic is implemented by `RetryInterceptor` which delegates to per-policy behavior classes in `core-data/api/retry/behaviour/`.

# Reference: `EndpointType` Values

| Value | Meaning |
|---|---|
| `Default` | **Default** — standard endpoint |
| `KrakenD` | KrakenD aggregated endpoint — response is `KrakenDResponse<T>` with partial error support |
| `Login` | Login endpoint — special handling: no token refresh on 401 |
| `RefreshToken` | Token refresh endpoint — on failure, triggers user logout |

# Reference: `@Tag` Types

Tags are Retrofit metadata tags attached to requests via `@Tag` parameters. They are **not** sent as HTTP headers — they are used internally by interceptors and logging.

| Tag type | Purpose |
|---|---|
| `LogCategory` | Categorizes the request for Datadog logging (e.g. `LogCategory.Punch`, `LogCategory.Home`) |
| `LogAttribute` | Attaches additional structured attributes to log entries |
| `ApiLogOverride` | Overrides the default log level for specific HTTP status codes (e.g. log 400 as Warning instead of Error) |
| `NoRetryOnUnauthorized` | Prevents the `RefreshTokenAuthenticator` from retrying on 401 |

# Reference: Common HTTP Headers

| Header constant | HTTP header name | Purpose |
|---|---|---|
| `AUTHORIZATION` | `Authorization` | Bearer token |
| `JWT_TOKEN` | `JWTToken` | Legacy JWT token |
| `IDP_AUTHORIZATION` | `IdpAuthorization` | IDP authorization token |
| `PCTY_CORRELATION_ID` | `X-Pcty-Request-Correlation-Id` | Request correlation ID for tracing |
| `PCTY_ENCRYPTION_TOKEN` | `X-Pcty-Pctyjekid` | Encryption key token |
| `PCTY_GATEWAY` | `X-Pcty-Gateway` | Gateway routing header |
| `PCTY_NEXT_TOKEN` | `X-Pcty-Next-Token` | Pagination next-page token (response header) |
| `PCTY_TOTAL_COUNT` | `X-Pcty-Total-Count` | Total item count for pagination (response header) |
| `PCTY_EM_STATUS` | `X-Pcty-EM-Status` | Emergency mode status (response header) |
| `PCTY_CLIENT_VERSION` | `X-Pcty-Client-Version` | Client app version |
| `IDEMPOTENCY_KEY` | `Idempotency-Key` | Idempotency key for write operations |
| `USER_AGENT` | `User-Agent` | User agent string |
| `DEVICE_INFO` | `DeviceInfo` | Device information header |

# Reference: Interceptor Chain

Requests pass through these interceptors in order:

1. **`StartTraceInterceptor`** — Initiates distributed tracing span
2. **`CorrelationIdInterceptor`** — Adds `X-Pcty-Request-Correlation-Id` header
3. **`PctyClientAndUserAgentInterceptor`** — Injects client version and user agent
4. **`AuthInterceptor`** — Resolves base URL from `@Endpoint(baseUrl)` and injects auth headers based on `@Endpoint(auth)`
5. **`RetryInterceptor`** — Implements retry logic based on `@Endpoint(retry)`
6. **`GetImageByImageFileKeyCacheControlInterceptor`** — Cache control for image requests
7. **`EmergencyStatusInterceptor`** — Reads `X-Pcty-EM-Status` response header to track emergency mode
8. **`KrakenDErrorInterceptor`** — Parses KrakenD error responses for `EndpointType.KrakenD` endpoints
9. **`HttpLoggingInterceptor`** — Logs request/response details
10. **`CompleteTraceInterceptor`** — Completes the distributed tracing span

Additionally, `RefreshTokenAuthenticator` handles 401 responses by refreshing the token and retrying.

# Reference: DI Registration Pattern

API interfaces are registered in Koin modules using the `singleOf<MyApi>()` extension:

```kotlin
fun Injector.registerFeatureModule(instanceScope: InstanceScope) {
    modules(
        module {
            singleOf<FeatureApi>()           // Creates Retrofit proxy from the correct Retrofit instance
            singleOf(::FeatureRepositoryImpl) bind FeatureRepository::class
            viewModelOf(::FeatureViewModel)
        },
        instanceScope,
    )
}
```

The `singleOf<T : BaseApi>()` extension (defined in `core-data/api/SingleOf.kt`) checks whether `T` extends `Api` or `LegacyApi` and resolves the appropriate qualified `Retrofit` instance to call `.create(T::class.java)`.

# Reference: Error Hierarchy

The `apiCall { }` wrapper maps exceptions to `ErrorResult` subtypes:

| Exception | ErrorResult | Meaning |
|---|---|---|
| `HttpException` (emergency codes) | `EmergencyModeErrorResult` | Server is in emergency mode |
| `HttpException` (force upgrade) | `ForceUpgradeErrorResult` | App update required |
| `HttpException` (other) | `ServerErrorResult` | Server error with HTTP code and error body |
| `ApiDataException` | `ApiDataErrorResult` | API-level error (e.g. response wrapper errors) |
| `JsonDataException` | `ApiDataErrorResult` | JSON deserialization failure |
| `SocketTimeoutException` | `TimeoutErrorResult` | Request timed out |
| `UnknownHostException` | `UnknownHostErrorResult` | DNS resolution failed |
| `ConnectException` / `SocketException` | `ConnectErrorResult` | Connection failed |
| `CancellationException` | *(re-thrown)* | Coroutine was cancelled — not caught |
| Other | `GeneralNetworkError` | Unknown network error |

# Reference: `@TracedRequest`

The `@TracedRequest(parentTrace = "trace_name")` annotation groups API calls under a named trace for performance monitoring. The `@Endpoint` annotation itself is meta-annotated with `@TracedRequest(parentTrace = API_CALL)`, so **all** endpoints get a default `"api_call"` trace. Adding `@TracedRequest` on a specific function **overrides** the default parent trace.

Common trace names are defined as constants in the `monitoring` module (e.g. `FETCH_HOME`, `ADD_PUNCH`, `FETCH_CHATS`).
