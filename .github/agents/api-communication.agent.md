---
description: Analyze the source code and find all API communication points and their details (endpoints, methods, request/response formats, authentication, etc.).
user-invocable: true
---

Analyze the source code and find all API communication points and their details (endpoints, methods, query parameters, request/response formats, authentication, etc.).

# Requirements
- Find all API communication points in the codebase.
- For each API communication point, extract the following details:
  - Endpoint URL or address
  - HTTP method (GET, POST, PUT, DELETE, etc.) or communication method (for non-HTTP APIs)
  - Query parameters (if applicable)
  - Request content
  - Response content
  - Authentication method (e.g., API key, OAuth, JWT)

# Format
Output the results in a structured format, . For example:

```
# Overview
| Endpoint | Method | Query Parameters | Request Content | Response Content | Authentication |
|----------|--------|------------------|-----------------|------------------|----------------|
| /api/users | GET | page, limit | N/A | List of users | API key |
| /api/users | POST | N/A | { "name": "John", "email": "john@example.com" } | User created | API key |

# /api/users
- Method: GET
- Query Parameters: page, limit
- Request Content: N/A
- Response Content: List of users
- Authentication: API key
```
