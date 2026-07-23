---
title: "Introduction"
excerpt: "Build storefront, customer, and authenticated business integrations with Scalev API v3."
deprecated: false
hidden: false
metadata:
  robots: index
---
Scalev API v3 is a headless commerce API for storefront, customer, and authenticated business integrations. You can use it to power catalog, cart, checkout, orders, subscriptions, digital product access, and related commerce workflows in your own app or system.

This introduction covers the base URL, authentication families, response format, status codes, rate limits, and pagination model.

## Start here

- **[Choose an auth method](/docs/authentication-with-api-key)** — Use API keys for server-side integrations, or OAuth when you need a merchant authorization flow.
- **[Authorize with OAuth](/docs/authorization-with-o-auth)** — Connect a Scalev business account to your application with the OAuth authorization flow.
- **[Connect AI assistants](/docs/scalev-mcp-connector)** — Use the Scalev MCP connector to give supported AI assistants OAuth-approved access to Scalev.

## Build your integration

- **[Create orders](/docs/creating-orders)** — Build digital or physical product orders and redirect customers to the payment page.
- **[Receive webhooks](/docs/webhooks-overview)** — Subscribe to events and verify webhook requests before you process them.
- **[Browse the API reference](/reference)** — Inspect endpoints, parameters, request bodies, and response schemas from the interactive API reference.
- **[Read the changelog](/docs/changelog)** — Follow product updates and documentation changes as the API evolves.

## Base URL

```text
https://api.scalev.com
```

All documented endpoints in this reference live under the `/v3` namespace.

## Authentication

Authentication depends on the route family:

### Public storefront routes

Store-derived public storefront routes under `/v3/stores/{store_id}/public/*` require a publishable storefront API key:

```text
X-Scalev-Storefront-Api-Key: sfpk_...
```

Use the store `unique_id` as `{store_id}` for new Storefront API integrations. Storefront API setup is separate from hosted Storefront settings; it manages the public Store ID, publishable API keys, and allowed CORS origins.

### Customer-authenticated routes

Customer routes use bearer authentication:

```text
Authorization: Bearer CUSTOMER_ACCESS_TOKEN
```

Customer access tokens are issued by the storefront customer auth flow. A successful customer login (when OTP is not required), OTP verification, or JWT refresh returns a `CustomerAuthTokenResponse`:

```json
{
  "access": "CUSTOMER_ACCESS_TOKEN",
  "refresh": "CUSTOMER_REFRESH_TOKEN",
  "store_unique_id": "store_..."
}
```

Send `access` as `Authorization: Bearer <token>` to `/v3/stores/{store_id}/customers/me/*`. Use `refresh` with `POST /v3/stores/{store_id}/public/auth/jwt/refresh` to obtain a new access token. `store_unique_id` is returned by some OTP verification responses.

When OTP is required, `POST /v3/stores/{store_id}/public/auth/login` sends the one-time code and returns `{ "message": "..." }`; the caller should show the OTP entry step and then verify the OTP to receive tokens.

### Authenticated business routes

Authenticated business routes use bearer authentication with an access token or business API key:

```text
Authorization: Bearer YOUR_TOKEN_HERE
```

## Common Response Format

Scalev API v3 does not use the legacy `code` / `status` / `data` response envelope.

### Single Resource Success

Single-resource success responses return the resource directly:

```json
{
  "id": "ord_123",
  "status": "paid"
}
```

### Non-Paginated Collection Success

```json
{
  "data": [
    {
      "id": "prod_123"
    }
  ],
  "is_paginated": false
}
```

### Paginated Collection Success

```json
{
  "data": [
    {
      "id": "prod_123"
    }
  ],
  "is_paginated": true,
  "has_next": true,
  "has_previous": false,
  "next_cursor": "opaque-token",
  "previous_cursor": null,
  "page_size": 25
}
```

### Error Response

```json
{
  "error": "Error message",
  "error_code": "optional_error_code"
}
```

## HTTP Status Codes

The API uses standard HTTP status codes:

- `200 OK` - Successful read, update, or action request
- `201 Created` - Successful create request
- `204 No Content` - Successful request with no response body
- `400 Bad Request` - Invalid request format, parameters, or cursor
- `401 Unauthorized` - Authentication required or token is invalid
- `403 Forbidden` - Authenticated but not allowed
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `5xx` - Unexpected server error

## Rate Limiting

API requests may be rate limited. The bucket depends on how the request is authenticated:

- **Storefront public requests** that use `X-Scalev-Storefront-Api-Key` or `X-Scalev-Guest-Token` are treated as direct browser/client traffic and use the client/IP rate limiter.
- **Machine-authenticated business requests** (API keys and OAuth access tokens) use credential-scoped buckets: **10,000 requests per hour** plus **100 requests per 10 seconds** for short bursts by key or OAuth installation.

When rate limiting is applied, limit information is returned in response headers such as:

- `X-Ratelimit-Limit`
- `X-Ratelimit-Remaining`
- `X-Ratelimit-Reset`

Some endpoint-specific limits are stricter. Rate-limit responses may be plain text instead of the normal JSON error shape.

## Pagination

Paginated `/v3` endpoints use opaque cursor-based pagination.

### Request Parameters

- `page_size` - Number of items to return
- `next_cursor` - Cursor for the next page
- `previous_cursor` - Cursor for the previous page

### Response Fields

- `data` - Array of items in the current page
- `is_paginated` - Always `true` for paginated responses
- `has_next` - Whether a next page exists
- `has_previous` - Whether a previous page exists
- `next_cursor` - Opaque cursor for the next page
- `previous_cursor` - Opaque cursor for the previous page
- `page_size` - Number of items returned per page

```json
{
  "data": [
    {
      "id": "prod_123"
    }
  ],
  "is_paginated": true,
  "has_next": true,
  "has_previous": false,
  "next_cursor": "opaque-token",
  "previous_cursor": null,
  "page_size": 25
}
```

## Support

If you encounter issues, contact the Scalev support team.

---

This documentation may change as the Scalev API evolves.
